"""Tkinter voice interface that asks OpenAI for terminal commands."""

import json
import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import Optional

import playsound
import speech_recognition as sr
from gtts import gTTS
from openai import OpenAI

# OpenAI client configured via the standard environment variable.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class VoiceCommander(tk.Tk):
    """Simple GUI application that listens for voice commands."""

    def __init__(self) -> None:
        super().__init__()
        self.title("ChatGPT iTerm Voice Commander")
        self.geometry("600x400")

        self.listener = sr.Recognizer()
        self.output_text = scrolledtext.ScrolledText(self, height=10)
        self.output_text.pack(pady=20)
        threading.Thread(target=self.listen_and_process, daemon=True).start()

    # ------------------------------------------------------------------
    def listen_and_process(self) -> None:
        """Listen for voice commands and execute suggested terminal actions."""
        while True:
            command = self.listen()
            if command and "stop" in command.lower():
                self.speak("Goodbye!")
                break
            if command:
                self.output_text.insert(tk.END, f"You said: {command}\n")
                terminal_command = self.chat_with_gpt(command)
                if terminal_command:
                    self.output_text.insert(
                        tk.END, f"ChatGPT suggests: {terminal_command}\n"
                    )
                    self.execute_command(terminal_command)

    # ------------------------------------------------------------------
    def listen(self) -> Optional[str]:
        """Listen to the microphone and return recognised text."""
        try:
            with sr.Microphone() as source:
                self.output_text.insert(tk.END, "Listening...\n")
                audio = self.listener.listen(source)
            return self.listener.recognize_google(audio)
        except sr.UnknownValueError:
            self.speak("Sorry, I did not get that.")
        except sr.RequestError as e:
            self.speak(f"Could not request results; {e}")
        except Exception as e:  # pragma: no cover - hardware issues
            self.output_text.insert(tk.END, f"Error accessing microphone: {e}\n")
        return None

    # ------------------------------------------------------------------
    def chat_with_gpt(self, text: str) -> Optional[str]:
        """Send ``text`` to OpenAI and return a suggested terminal command."""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that suggests terminal commands based on user input.",
                    },
                    {"role": "user", "content": text},
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
                                    "description": "The terminal command to execute",
                                }
                            },
                            "required": ["command"],
                        },
                    }
                ],
                function_call="auto",
            )
            choice = response.choices[0]
            if choice.finish_reason == "function_call" and choice.message.function_call:
                call = choice.message.function_call
                if call.name == "execute_terminal_command":
                    args = json.loads(call.arguments)
                    return args.get("command")
        except Exception as e:  # pragma: no cover - network errors
            self.output_text.insert(tk.END, f"Error with ChatGPT: {e}\n")
        return None

    # ------------------------------------------------------------------
    def speak(self, text: str) -> None:
        """Speak ``text`` using gTTS and play the result."""
        filename = "response.mp3"
        tts = gTTS(text=text, lang="en")
        tts.save(filename)
        playsound.playsound(filename)
        if os.path.exists(filename):
            os.remove(filename)

    # ------------------------------------------------------------------
    def execute_command(self, command: str) -> None:
        """Execute ``command`` after user confirmation."""
        confirm = messagebox.askyesno("Confirm", f"Execute this command: {command}?")
        if not confirm:
            self.output_text.insert(tk.END, "Execution cancelled.\n")
            return
        try:
            result = subprocess.run(
                command, shell=True, check=True, text=True, capture_output=True
            )
            self.output_text.insert(
                tk.END, f"Command executed successfully:\n{result.stdout}\n"
            )
        except subprocess.CalledProcessError as exc:
            self.output_text.insert(tk.END, f"Error executing command: {exc}\n")


if __name__ == "__main__":  # pragma: no cover - manual usage
    app = VoiceCommander()
    app.mainloop()
