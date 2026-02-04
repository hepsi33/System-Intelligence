import PyInstaller.__main__
import os
import shutil

def build():
    print("Building RobotCLI...")
    
    # Ensure dist/build directories are clean
    if os.path.exists("dist"):
        shutil.rmtree("dist", ignore_errors=True)
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)

    PyInstaller.__main__.run([
        'main.py',
        '--name=RobotCLI',
        '--onefile',
        '--console',
        '--clean',
        # Add hidden imports if necessary (e.g. some tyrosine/rich internals sometimes need help)
        '--hidden-import=rich.live',
        '--hidden-import=rich.spinner',
        '--hidden-import=rich.markdown',
        '--hidden-import=typer',
        '--hidden-import=psutil',
        '--hidden-import=send2trash',
        '--collect-all=psutil',
        '--collect-all=rich',
    ])
    
    print("\nBuild complete! Executable is in the 'dist' folder.")

if __name__ == "__main__":
    build()
