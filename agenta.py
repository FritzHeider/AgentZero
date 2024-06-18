import os
import subprocess
import sys
import json
import speech_recognition as sr
from gtts import gTTS
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import playsound

def ensure_distutils():
    try:
        import distutils
    except ImportError:
        print("distutils is not installed. Attempting to install...")
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools"])

ensure_distutils()

# Ensure your API key is set

class VoiceCommander(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ChatGPT iTerm Voice Commander')
        self.geometry('600x400')

        # Initialize speech recognition
        self.listener = sr.Recognizer()

        # Text widget for command output
        self.output_text = scrolledtext.ScrolledText(self, height=10)
        self.output_text.pack(pady=20)

        # Start listening to commands in a separate thread
        threading.Thread(target=self.listen_and_process, daemon=True).start()

    def listen_and_process(self):
        """ Listen to voice commands, process them, and handle command execution. """
        while True:
            command = self.listen()
            if command and 'stop' in command.lower():
                self.speak("Goodbye!")
                break
            elif command:
                self.output_text.insert(tk.END, f"You said: {command}\n")
                terminal_command = self.chat_with_gpt(command)
                if terminal_command:
                    self.output_text.insert(tk.END, f"ChatGPT suggests: {terminal_command}\n")
                    self.execute_command(terminal_command)

    def listen(self):
        """ Listen to microphone input and convert it to text. """
        try:
            with sr.Microphone() as source:
                self.output_text.insert(tk.END, "Listening...\n")
                audio = self.listener.listen(source)
            try:
                return self.listener.recognize_google(audio)
            except sr.UnknownValueError:
                self.speak("Sorry, I did not get that.")
                return None
            except sr.RequestError as e:
                self.speak(f"Could not request results; {e}")
                return None
        except Exception as e:
            self.output_text.insert(tk.END, f"Error accessing microphone: {e}\n")

    def chat_with_gpt(self, text):
        """ Send text to ChatGPT and get a suggested terminal command. """
        try:
            response = client.chat.completions.create(model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that suggests terminal commands based on user input and then searches online for current api syxtax and executes the proper commands."},
                {"role": "user", "content": text}
            ],
            functions=[
                {
                    "name": "execute_terminal_command",
                    "description": "Execute a terminal command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The terminal command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                }
            ],
            function_call="auto")
            # Parse the function call
            if response.choices[0].finish_reason == "function_call":
                function_call = response.choices[0].message.function_call
                if function_call.name == 'execute_terminal_command':
                    arguments = json.loads(function_call.arguments)
                    command = arguments['command']
                    return command
            return None
        except Exception as e:
            self.output_text.insert(tk.END, f"Error with ChatGPT: {e}\n")
            return None

    def speak(self, text):
        """ Use gTTS to speak out text. """
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        playsound.playsound("response.mp3")
        os.remove("response.mp3")

    def execute_command(self, command):
        """ Execute the command in iTerm after confirmation. """
        confirm = messagebox.askyesno("Confirm", f"Execute this command: {command}?")
        if confirm:
            try:
                result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
                self.output_text.insert(tk.END, f"Command executed successfully:\n{result.stdout}\n")
            except subprocess.CalledProcessError as e:
                self.output_text.insert(tk.END, f"Error executing command: {e}\n")
        else:
            self.output_text.insert(tk.END, "Execution cancelled.\n")

if __name__ == "__main__":
    app = VoiceCommander()
    app.mainloop()