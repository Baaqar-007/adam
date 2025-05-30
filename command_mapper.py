# command_mapper.py - modified to handle number words
import json
import os
import re

class CommandMapper:
    def __init__(self, commands_file="commands.json"):
        self.commands_file = commands_file
        self.commands = self._load_commands()
        
        # Number word to digit mapping
        self.number_words = { "zero" :"0",
            "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
        }
    
    def _load_commands(self):
        """Load commands from JSON file, create if not exists"""
        if not os.path.exists(self.commands_file):
            default_commands = {
                "list directory": "dir /B",
                "list files": "dir /B",
                "move to ([0-9]+)": "cd_index",
                "create folder (.*)": "mkdir",
                "create folder": "mkdir default",
                "create file (.*)": "echo.>",
                "create file": "echo.>default.txt",
                "back": "cd ..",
                "home": "cd .",
                "stop": "stop_listening"
            }
            with open(self.commands_file, 'w') as f:
                json.dump(default_commands, f, indent=4)
        
        with open(self.commands_file, 'r') as f:
            return json.load(f)
    
    def save_commands(self):
        """Save current commands to JSON file"""
        with open(self.commands_file, 'w') as f:
            json.dump(self.commands, f, indent=4)
    
    def convert_number_words(self, text):
        """Convert number words to digits in text"""
        # Process full commands like "move to one"
        for word, digit in self.number_words.items():
            # Look for patterns like "move to one" and replace with "move to 1"
            pattern = r"\b(move to) " + word + r"\b"
            text = re.sub(pattern, r"\1 " + digit, text, flags=re.IGNORECASE)
        
        return text
    
    def map_command(self, voice_command):
        """Map a voice command to a shell command"""
        # Convert number words to digits first
        processed_command = self.convert_number_words(voice_command)
        
        # Check exact matches first
        if processed_command in self.commands:
            return self.commands[processed_command]
        
        # Check regex patterns
        for pattern, shell_cmd in self.commands.items():
            match = re.match(f"^{pattern}$", processed_command)
            if match:
                # Handle special case for "move to X" (directory index)
                if shell_cmd == "cd_index":
                    try:
                        index = int(match.group(1)) - 1  # Convert to 0-based index
                        return f"cd_index {index}"
                    except:
                        return None
                
                # Handle other parameterized commands
                if '(' in pattern:
                    # Extract parameter from voice command
                    param = match.group(1)
                    # Replace placeholder in shell command if present
                    if ' ' in shell_cmd:
                        cmd_parts = shell_cmd.split(' ', 1)
                        return f"{cmd_parts[0]} {param}"
                    else:
                        return f"{shell_cmd} {param}"
                return shell_cmd
        
        return None
    
    
    def add_command(self, voice_pattern, shell_command):
        """Add a new command mapping"""
        self.commands[voice_pattern] = shell_command
        self.save_commands()
    
    def remove_command(self, voice_pattern):
        """Remove a command mapping"""
        if voice_pattern in self.commands:
            del self.commands[voice_pattern]
            self.save_commands()
            return True
        return False
    
    def list_commands(self):
        """Return all command mappings"""
        return self.commands