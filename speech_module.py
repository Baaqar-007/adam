import speech_recognition as sr

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise and mic sensitivity
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def listen(self):
        """Listen for voice input and return recognized text"""
        print("Listening for voice command...")
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text.lower()
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Error with the speech recognition service: {e}")
                return None
            except Exception as e:
                print(f"Error: {e}")
                return None