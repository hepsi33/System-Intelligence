# RobotCLI V2 - System Intelligence

**RobotCLI** is a futuristic, AI-powered Windows Agent that allows you to control your file system and monitor system health using natural language. Built with Python, Rich, and OpenRouter (Google Gemini).

## 🚀 Features

### 🧠 Intelligent Core
*   **Natural Language Processing**: Chat with your computer. Ask it to "Clean up my desktop" or "Find large files".
*   **Context Aware**: The agent knows about your system resources and file structure.

### 📂 File Management
*   **Smart Actions**: Create, Read, Rename, Move, Copy, and Delete files.
*   **Safe Deletion**: Deletes files to the Recycle Bin by default.
*   **Organization**: Effectively organize cluttered folders (e.g., `Downloads`) by file extension.
*   **Bulk Tools**: Find duplicates, search recursively, and identify simple storage hogs.

### ⚡ System Monitoring
*   **Real-Time Stats**: Check CPU and RAM usage on demand.
*   **Process Manager**: List top memory-consuming processes.
*   **Disk Usage**: View free space across all drives.

### 🎨 "Light Robot" UI
*   **Beautiful Interface**: Powered by `rich`, featuring a clean White background with **Cyan**, **Blue**, and **Bold Black** accents.
*   **Interactive**: Spinners, progress bars, and formatted markdown responses.
*   **Auto-Close**: The window gracefully closes 3 seconds after you say "quit" or "exit".

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.10+
*   An API Key from [OpenRouter](https://openrouter.ai/) (uses `google/gemini-2.0-flash-001` by default).

### Installation
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/hepsi33/System-Intelligence.git
    cd System-Intelligence
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup**:
    Create a `.env` file in the root directory:
    ```env
    OPENROUTER_API_KEY=your_api_key_here
    ```

## 💻 Usage

### Running from Source
```bash
python main.py
```

### Running the Executable
If you have built the `.exe`:
1.  Double-click `RobotCLI.exe`.
2.  If prompted, enter your API Key (it will be saved for the session).
3.  Start chatting!

**Commands**:
*   *"Check my system health"*
*   *"Make a folder called 'Backup' and zip my Documents into it"*
*   *"Find all PDF files in Downloads"*
*   *"Quit"* (Closes the window)

## 🏗️ Building the Executable
To create a standalone `.exe` file:
```bash
python build_exe.py
```
 The output will be in the `dist/` folder.

## 🤝 Contributing
Feel free to fork this repository and submit Pull Requests.

## 📄 License
MIT License. Use responsibly.
