import os
import json
from typing import List, Dict, Any, Generator
from openai import OpenAI
from tools import (
    create_file, delete_file, rename_file, get_file_info,
    make_directory, list_directory, is_directory,
    search_files, organize_files_by_extension,
    move_file, copy_file,
    read_file, write_to_file, append_to_file,
    zip_folder, extract_archive,
    check_resources, disk_usage, list_processes,
    find_duplicates, find_large_files,
    git_manager
)

# --- V2 Tools Schema ---
TOOLS_SCHEMA = [
    # 1. Basic File Actions
    {"type": "function", "function": {"name": "create_file", "description": "Create a new file with optional content.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "delete_file", "description": "Delete a file. safe=True moves to recycle bin.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "safe": {"type": "boolean"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "rename_file", "description": "Rename a file.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "new_name": {"type": "string"}}, "required": ["path", "new_name"]}}},
    {"type": "function", "function": {"name": "get_file_info", "description": "Get size, creation date, etc.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "move_file", "description": "Move a file or folder.", "parameters": {"type": "object", "properties": {"source": {"type": "string"}, "destination": {"type": "string"}}, "required": ["source", "destination"]}}},
    {"type": "function", "function": {"name": "copy_file", "description": "Copy a file or folder.", "parameters": {"type": "object", "properties": {"source": {"type": "string"}, "destination": {"type": "string"}}, "required": ["source", "destination"]}}},
    
    # 2. Folder Actions
    {"type": "function", "function": {"name": "make_directory", "description": "Create a directory recursively.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "list_directory", "description": "List contents of a directory.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    
    # 3. Bulk & Organization
    {"type": "function", "function": {"name": "search_files", "description": "Search recursively by name or extension.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "search_path": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "organize_files_by_extension", "description": "Sort files in a folder into subfolders by type.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    
    # 4. Content Manipulation
    {"type": "function", "function": {"name": "read_file", "description": "Read text from a file.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_to_file", "description": "Overwrite file content.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "append_to_file", "description": "Append content to a file.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    
    # 5. Pro Features
    {"type": "function", "function": {"name": "zip_folder", "description": "Compress folder to zip.", "parameters": {"type": "object", "properties": {"folder_path": {"type": "string"}, "output_path": {"type": "string"}}, "required": ["folder_path", "output_path"]}}},
    {"type": "function", "function": {"name": "extract_archive", "description": "Unzip an archive.", "parameters": {"type": "object", "properties": {"archive_path": {"type": "string"}, "output_path": {"type": "string"}}, "required": ["archive_path", "output_path"]}}},
    {"type": "function", "function": {"name": "check_resources", "description": "Check CPU and RAM usage.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "disk_usage", "description": "Check free space on drives.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "list_processes", "description": "List top memory consuming processes.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "find_duplicates", "description": "Find duplicate files in a folder.", "parameters": {"type": "object", "properties": {"folder_path": {"type": "string"}}, "required": ["folder_path"]}}},
    {"type": "function", "function": {"name": "find_large_files", "description": "Find files larger than threshold MB.", "parameters": {"type": "object", "properties": {"folder_path": {"type": "string"}, "size_mb_threshold": {"type": "integer"}}, "required": ["folder_path"]}}},
    
    # 6. DevOps
    {"type": "function", "function": {"name": "git_manager", "description": "Manage git repo (init, add, commit, push).", "parameters": {"type": "object", "properties": {"repo_path": {"type": "string"}, "remote_url": {"type": "string"}, "commit_message": {"type": "string"}}, "required": ["repo_path"]}}}
]

class RobotBackend:
    def __init__(self, api_key: str, model: str = "google/gemini-2.0-flash-001"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=120.0,
        )
        self.model = model
        self.history: List[Dict[str, Any]] = [
            {"role": "system", "content": "You are RobotCLI, an advanced Windows System Intelligence Agent. You can manage files (create, delete safe, zip), organize folders, and monitor system health (CPU/RAM). Always prefer 'safe' delete (Recycle Bin). When asked to organize, use the organize tool. Be helpful and precise."}
        ]

    def set_model(self, model: str):
        self.model = model

    def get_models(self) -> List[str]:
        return [
            "google/gemini-2.0-flash-001",
            "google/gemini-pro",
            "openai/gpt-4-turbo",
            "anthropic/claude-3-opus",
        ]

    def chat_step(self, user_input: str) -> Generator[Dict[str, Any], None, None]:
        self.history.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
            
            msg = response.choices[0].message
            
            if msg.tool_calls:
                self.history.append(msg)
                
                for tool_call in msg.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    yield {"type": "status", "value": f"Running {func_name}..."}
                    
                    # Dispatcher
                    try:
                        if func_name in globals():
                            func = globals()[func_name]
                            result = func(**args)
                        else:
                            result = f"Error: Function {func_name} not implemented."
                    except Exception as e:
                        result = f"Execution Error: {str(e)}"
                    
                    self.history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": str(result)
                    })
                    yield {"type": "status", "value": f"Completed {func_name}."}
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.history
                )
                final_content = final_response.choices[0].message.content
                self.history.append({"role": "assistant", "content": final_content})
                yield {"type": "content", "value": final_content}
                
            else:
                content = msg.content
                self.history.append({"role": "assistant", "content": content})
                yield {"type": "content", "value": content}

        except Exception as e:
            yield {"type": "content", "value": f"Error: {str(e)}"}
