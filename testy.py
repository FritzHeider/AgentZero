"""Example demonstrating OpenAI function calling to run terminal commands."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Optional

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Definition passed to the model when requesting a function call.
FUNCTION_DEFINITION = {
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


def suggest_command(prompt: str) -> Optional[str]:
    """Ask the model for a terminal command based on ``prompt``."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that suggests terminal commands based on user input.",
            },
            {"role": "user", "content": prompt},
        ],
        functions=[FUNCTION_DEFINITION],
        function_call="auto",
    )
    choice = response.choices[0]
    if choice.finish_reason == "function_call" and choice.message.function_call:
        call = choice.message.function_call
        if call.name == FUNCTION_DEFINITION["name"]:
            arguments = json.loads(call.arguments)
            return arguments.get("command")
    return None


def execute_terminal_command(command: str) -> str:
    """Execute ``command`` in the local shell and return the output."""
    result = subprocess.run(
        command, shell=True, check=True, text=True, capture_output=True
    )
    return result.stdout


def main() -> None:  # pragma: no cover - example usage
    command = suggest_command("Show me the current directory.")
    if not command:
        print("Model did not return a command")
        return
    try:
        output = execute_terminal_command(command)
        print(f"Command executed successfully:\n{output}")
    except subprocess.CalledProcessError as exc:
        print(f"Error executing command: {exc}")


if __name__ == "__main__":  # pragma: no cover - manual usage
    main()
