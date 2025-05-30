# executor.py - fixed directory indexing
import os
import subprocess
import re
import platform
import shutil

class CommandExecutor:
    def __init__(self):
        self.last_directory_listing = []
        self.history = []
        self.is_windows = platform.system() == "Windows"
        self.last_deleted_file = None  # Track the last deleted file path
        self.last_deleted_content = None  # Track the last deleted file content
        self.all_files_listing = []  # Track all files (not just directories)
        
    def execute(self, command):
        """Execute a shell command and return output"""
        if command is None:
            return "No command to execute"
        
        # Store in history
        self.history.append(command)
        # Handle 'cd', 'cd ..', 'cd .' commands
        if command.startswith("delete_file_index"):
            try:
                parts = command.split()
                index = int(parts[1])
                
                if not self.all_files_listing:
                    return "No file listing available. Please use 'list files' first."
                
                if index < 0 or index >= len(self.all_files_listing):
                    return f"File index {index+1} out of range (valid range: 1-{len(self.all_files_listing)})"
                
                file_to_delete = self.all_files_listing[index]
                file_path = os.path.join(os.getcwd(), file_to_delete)
                
                # Check if it's a file before deleting
                if os.path.isfile(file_path):
                    # Save file content before deletion
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            self.last_deleted_content = f.read()
                    except Exception as e:
                        # If we can't read the content (e.g., binary file), just note that
                        self.last_deleted_content = None
                        
                    self.last_deleted_file = file_path  # Store path for potential redo
                    os.remove(file_path)
                    return f"Deleted file: {file_to_delete}"
                else:
                    return f"Cannot delete '{file_to_delete}' as it's not a file."
            except Exception as e:
                return f"Error deleting file: {e}"
        
        # Handle deletion recovery with content preservation
        elif command == "redo_deletion":
            if self.last_deleted_file and os.path.exists(self.last_deleted_file):
                return "The file was not actually deleted or has already been restored."
            elif self.last_deleted_file:
                try:
                    # Create the file with original content if available
                    with open(self.last_deleted_file, 'w', encoding='utf-8') as f:
                        if self.last_deleted_content is not None:
                            f.write(self.last_deleted_content)
                    
                    filename = os.path.basename(self.last_deleted_file)
                    if self.last_deleted_content is not None:
                        return f"Restored file with original content: {filename}"
                    else:
                        return f"Restored empty file (original content couldn't be preserved): {filename}"
                except Exception as e:
                    return f"Error recreating file: {e}"
            else:
                return "No file has been deleted yet."
        if command.startswith("cd "):
            try:
                path = command[3:].strip()
                os.chdir(path)
                return f"Changed directory to: {os.getcwd()}"
            except Exception as e:
                return f"Error changing directory: {e}"
        
        elif command == "cd" or command == "cd.":
            return f"Current directory: {os.getcwd()}"
        elif command == "cd..":
            try:
                os.chdir("..")
                return f"Moved up to: {os.getcwd()}"
            except Exception as e:
                return f"Error moving up a directory: {e}"

        # Handle special case for directory indexing
        if command.startswith("cd_index"):
            try:
                parts = command.split()
                index = int(parts[1])
                
                if not self.last_directory_listing:
                    return "No directory listing available. Please use 'list files' first."
                
                if index < 0 or index >= len(self.last_directory_listing):
                    return f"Index {index+1} out of range (valid range: 1-{len(self.last_directory_listing)})"
                
                target_dir = self.last_directory_listing[index]
                os.chdir(target_dir)
                return f"Changed directory to: {target_dir}"
            except Exception as e:
                return f"Error changing directory: {e}"
        
        # Handle standard commands
        try:
            # Use Windows commands
            if self.is_windows:
                # For directory listing
                if command == "dir /B":
                    # Get directory listing and identify directories
                    output = subprocess.check_output(command, shell=True).decode('utf-8')
                    lines = output.strip().split('\n')
                    
                    # Reset the listings
                    self.last_directory_listing = []
                    self.all_files_listing = []
                    dir_index = 1
                    file_index = 1
                    
                    # Process each entry and identify directories vs files
                    dirs_output = []
                    files_output = []
                    
                    for line in lines:
                        item = line.strip()
                        if not item:  # Skip empty lines
                            continue
                            
                        full_path = os.path.join(os.getcwd(), item)
                        
                        # Store all items for reference
                        self.all_files_listing.append(item)
                        
                        if os.path.isdir(full_path):
                            # This is a directory
                            self.last_directory_listing.append(item)
                            dirs_output.append(f"{dir_index}. {item}")
                            dir_index += 1
                        elif os.path.isfile(full_path):
                            # This is a file
                            files_output.append(f"{file_index}. {item}")
                            file_index += 1
                    
                    # Prepare the result with directory and file lists
                    result = ""
                    if dirs_output:
                        result += "Directories (can use 'move to X'):\n"
                        result += "\n".join(dirs_output) + "\n\n"
                    
                    if files_output:
                        result += "Files (can use 'delete file number X'):\n"
                        result += "\n".join(files_output) + "\n\n"
                    
                    if not dirs_output and not files_output:
                        result = "No files or directories found."
                    
                    return result
                
                # Map other commands
                elif command.startswith("echo.>"):
                    # Handle file creation
                    file_name = command[6:].strip()
                    if not file_name:
                        file_name = "default.txt"
                    
                    # Create the file
                    with open(file_name, 'w') as f:
                        pass
                    return f"Created file: {file_name}"
                else:
                    # For other commands, execute directly
                    output = subprocess.check_output(command, shell=True).decode('utf-8')
                    return output
            else:
                # For non-Windows platforms, use the original implementation
                output = subprocess.check_output(command, shell=True).decode('utf-8')
                return output
                
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"