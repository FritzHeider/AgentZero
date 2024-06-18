import speech_recognition as sr
import pyttsx3
from openai import OpenAI

client = OpenAI(api_key='sk-agent-x-fsZmmi5uVEG6lyqnRCj7T3BlbkFJdBYZovJ7z6pwmAGC2xQc')
import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading

# Configure your OpenAI API key

class VoiceCommander(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ChatGPT iTerm Voice Commander')
        self.geometry('600x400')

        # Initialize speech recognition and TTS
        self.listener = sr.Recognizer()
        self.speaker = pyttsx3.init()

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
                response = self.chat_with_gpt(command)
                self.output_text.insert(tk.END, f"ChatGPT suggests: {response}\n")
                self.execute_command(response)

    def listen(self):
        """ Listen to microphone input and convert it to text. """
        with sr.Microphone() as source:
            self.output_text.insert(tk.END, "Listening...\n")
            audio = self.listener.listen(source)
        try:
            return self.listener.recognize_google(audio)
        except sr.UnknownValueError:
            self.speak("Sorry, I did not get that.")
            return None
        except sr.RequestError as e:
            self.speak("Could not request results; {0}".format(e))
            return None

    def chat_with_gpt(self, text):
        """ Send text to ChatGPT and get a response. """
        try:
            response = client.completions.create(engine="text-davinci-003",
            prompt=text,
            max_tokens=150)
            return response.choices[0].text.strip()
        except Exception as e:
            self.output_text.insert(tk.END, f"Error with ChatGPT: {e}\n")
            return "I had a problem processing that command."

    def speak(self, text):
        """ Use TTS to speak out text. """
        self.speaker.say(text)
        self.speaker.runAndWait()

    def execute_command(self, command):
        """ Execute the command in iTerm after confirmation. """
        confirm = messagebox.askyesno("Confirm", "Execute this command?")
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