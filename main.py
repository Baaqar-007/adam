import os
import sys

from speech_module import SpeechRecognizer
from command_mapper import CommandMapper
from executor import CommandExecutor
from cli import VoiceGitCLI

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import speech_recognition as sr
        return True
    except ImportError:
        print("Required package 'SpeechRecognition' is missing.")
        print("Please install it using: pip install SpeechRecognition")
        return False

def main():
    if not check_dependencies():
        sys.exit(1)
    
    print("Initializing Voice-Controlled Git Command System...")
    
    # Initialize components
    recognizer = SpeechRecognizer()
    mapper = CommandMapper()
    executor = CommandExecutor()
    
    # Start CLI
    cli = VoiceGitCLI(recognizer, mapper, executor)
    cli.cmdloop()

if __name__ == "__main__":
    main()