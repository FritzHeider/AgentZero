from unittest.mock import patch
import subprocess
import sys
import types
import os

# Ensure repository root is in path so main.py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Stub modules that are imported in main.py but not needed for this test
sys.modules.setdefault('speech_recognition', types.ModuleType('speech_recognition'))
sys.modules.setdefault('pyttsx3', types.ModuleType('pyttsx3'))
sys.modules.setdefault('openai', types.ModuleType('openai'))
sys.modules['speech_recognition'].Recognizer = lambda *a, **k: None
sys.modules['speech_recognition'].Microphone = lambda *a, **k: None
sys.modules['pyttsx3'].init = lambda *a, **k: None
sys.modules['openai'].OpenAI = lambda *a, **k: types.SimpleNamespace()

import main
from main import VoiceCommander


def test_execute_command_inserts_output():
    # create instance without calling __init__ to avoid Tkinter setup
    commander = VoiceCommander.__new__(VoiceCommander)
    outputs = []

    class DummyText:
        def insert(self, *args):
            outputs.append(args[1])

    commander.output_text = DummyText()

    with patch('main.messagebox.askyesno', return_value=True) as mock_ask, \
         patch('main.subprocess.run') as mock_run:
        mock_run.return_value = subprocess.CompletedProcess('cmd', 0, stdout='ok')
        commander.execute_command('ls')
        mock_ask.assert_called_once_with("Confirm", "Execute this command?")
        mock_run.assert_called_once_with('ls', shell=True, check=True, text=True, capture_output=True)

    assert any('Command executed successfully:\nok\n' in output for output in outputs)
