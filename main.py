import os
import sys
import time
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.live import Live
from rich.theme import Theme
from rich.style import Style
from dotenv import load_dotenv
from pathlib import Path
from backend import RobotBackend

# Determine if running as script or frozen exe
if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

# Flag for auto-closing window
SHOULD_AUTO_CLOSE = False

# Load environment variables
load_dotenv(dotenv_path=application_path / ".env")

# Actually, I should use multiple chunks or target specific blocks. 
# Let's do it in one go if possible, but the file is large. 
# I will use multi_replace for safer editing.

# --- Light Robot Theme ---
robot_theme = Theme({
    "info": "cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "user_input": "bold black",
    "robot_text": "blue",
    "panel.border": "cyan",
    "spinner": "cyan"
})

app = typer.Typer(help="RobotCLI: Your Windows AI Agent")
console = Console(theme=robot_theme, style="black on white") # Light mode base

def get_api_key():
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        console.print("[bold warning]OPENROUTER_API_KEY not found in environment.[/bold warning]")
        key = Prompt.ask("Please enter your OpenRouter API Key", password=True)
    return key

def interactive_session(model: str):
    try:
        api_key = get_api_key()
        if not api_key:
            console.print("[error]API Key is required to proceed.[/error]")
            return

        bot = RobotBackend(api_key=api_key, model=model)
        
        welcome_text = f"[bold cyan]RobotCLI V2[/bold cyan]\n[dim]System Intelligence Online[/dim]\nInitialized with [blue]{model}[/blue].\nType 'exit' or 'quit' to stop."
        console.print(Panel(welcome_text, title="Welcome", border_style="cyan"))

        while True:
            try:
                user_input = Prompt.ask("\n[user_input]You[/user_input]")
                if user_input.lower() in ["exit", "quit"]:
                    global SHOULD_AUTO_CLOSE
                    SHOULD_AUTO_CLOSE = True
                    console.print("\n[bold cyan]Goodbye! Closing in 3 seconds...[/bold cyan]")
                    time.sleep(3)
                    break
                
                with Live(Spinner("bouncingBall", text="[cyan]Processing...[/cyan]", style="cyan"), refresh_per_second=10, console=console) as live:
                    response_generator = bot.chat_step(user_input)
                    
                    final_content = ""
                    for step in response_generator:
                        if step["type"] == "status":
                            live.update(Spinner("dots", text=f"[blue]{step['value']}[/blue]", style="cyan"))
                        elif step["type"] == "content":
                            final_content += step["value"]
                            live.update(Panel(Markdown(final_content), title="[bold cyan]Robot[/bold cyan]", border_style="cyan", style="black on white"))


            except KeyboardInterrupt:
                console.print("\n[warning]Exiting...[/warning]")
                break
            except Exception as e:
                console.print(f"[error]An error occurred during chat:[/error] {e}")

    except Exception as e:
         console.print(f"[error]Fatal Error:[/error] {e}")
    finally:
        console.print("\n[dim]Session ended.[/dim]")
        # Removed redundant wait here, handled in __main__


@app.command()
def start(
    model: str = typer.Option("google/gemini-2.0-flash-001", help="Initial model to use")
):
    """Start the interactive RobotCLI chat session."""
    interactive_session(model)

@app.command()
def models():
    """List available models from OpenRouter."""
    try:
        api_key = get_api_key()
        if not api_key:
            if getattr(sys, 'frozen', False):
                input("\nPress Enter to close...")
            return
            
        bot = RobotBackend(api_key=api_key)
        console.print("[bold]Fetching models...[/bold]")
        models_list = bot.get_models()
        
        console.print(Panel("\n".join([f"- {m}" for m in models_list]), title="Available Models", border_style="cyan"))
    except Exception as e:
        console.print(f"[error]Error checking models:[/error] {e}")
    finally:
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to close...")

if __name__ == "__main__":
    # If double-clicked (no args), default to 'start' command
    if len(sys.argv) == 1:
        sys.argv.append("start")

    try:
        app()
    except SystemExit:
        pass
    except BaseException as e:
         desktop = Path(os.path.expanduser("~")) / "Desktop"
         log_file = desktop / "RobotCLI_CrashLog.txt"
         with open(log_file, "w") as f:
             f.write(f"RUNTIME ERROR:\n{traceback.format_exc()}")
         
         console.print(f"[error]System Error: {e}[/error]")
         console.print(f"[warning]Log written to {log_file}[/warning]")
    finally:
        if getattr(sys, 'frozen', False) and not SHOULD_AUTO_CLOSE:
            input("\nPress Enter to close this window...")
