# cli.py - modified to add continuous listening
import cmd
import sys

class VoiceGitCLI(cmd.Cmd):
    intro = 'Welcome to Voice-Controlled Git Commands. Type help or ? to list commands.\n'
    prompt = 'voice-git> '
    
    def __init__(self, recognizer, mapper, executor):
        super().__init__()
        self.recognizer = recognizer
        self.mapper = mapper
        self.executor = executor
    
    def do_listen(self, arg):
        """Listen continuously for voice commands until 'stop' is heard"""
        print("Listening for voice commands... Say 'stop' to end listening mode.")
        
        while True:
            voice_text = self.recognizer.listen()
            if not voice_text:
                print("Didn't catch that. Please try again...")
                continue
                
            # Check if user wants to stop listening
            if voice_text.lower() == "stop":
                print("Exiting listening mode.")
                break
                
            # Process the voice command
            shell_command = self.mapper.map_command(voice_text)
            if shell_command:
                print(f"Executing: {shell_command}")
                output = self.executor.execute(shell_command)
                print(output)
            else:
                print(f"No mapping found for: '{voice_text}'")
    
    # The rest of the CLI class stays the same...
    
    def do_add(self, arg):
        """Add a new voice command mapping: add "voice pattern" "shell command" """
        try:
            parts = arg.split('"')
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 2:
                self.mapper.add_command(parts[0], parts[1])
                print(f"Added command: '{parts[0]}' -> '{parts[1]}'")
            else:
                print('Usage: add "voice pattern" "shell command"')
        except Exception as e:
            print(f"Error adding command: {e}")
    
    def do_remove(self, arg):
        """Remove a voice command mapping: remove "voice pattern" """
        try:
            pattern = arg.strip('"').strip()
            if self.mapper.remove_command(pattern):
                print(f"Removed command: '{pattern}'")
            else:
                print(f"Command not found: '{pattern}'")
        except Exception as e:
            print(f"Error removing command: {e}")
    
    def do_list(self, arg):
        """List all voice command mappings"""
        commands = self.mapper.list_commands()
        print("\nVoice Command Mappings:")
        print("----------------------")
        for voice, shell in commands.items():
            print(f"'{voice}' -> '{shell}'")
        print()
    
    def do_execute(self, arg):
        """Directly execute a shell command: execute ls -la"""
        if arg:
            output = self.executor.execute(arg)
            print(output)
        else:
            print("Please provide a command to execute")
    
    def do_exit(self, arg):
        """Exit the program"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the program"""
        return self.do_exit(arg)