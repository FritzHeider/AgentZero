import os
import subprocess
from typing import Optional

from openai import OpenAI


# Initialise the OpenAI client using the standard environment variable.
# This avoids hard coding credentials in source control.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def execute_command(command: str) -> str:
    """Run a shell command and return the trimmed standard output."""
    result = subprocess.run(
        command, shell=True, text=True, capture_output=True, check=False
    )
    return result.stdout.strip()


def chat_with_gpt(prompt: str, model: str = "gpt-3.5-turbo") -> Optional[str]:
    """Send ``prompt`` to the chat model and return the text response.

    Any exception raised by the API is caught and returned as a message so
    callers can surface the problem to a user without crashing.
    """
    try:
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
    except Exception as exc:  # pragma: no cover - network failures etc.
        return f"Error communicating with model: {exc}"
    return response.choices[0].message.content.strip()


def main() -> None:
    """Example usage that lists files and asks the model for guidance."""
    terminal_command = "ls -la"
    command_output = execute_command(terminal_command)
    gpt_prompt = (
        f"The output of the command '{terminal_command}' is:\n"
        f"{command_output}\n"
        "What should I do next?"
    )
    gpt_response = chat_with_gpt(gpt_prompt)
    print(gpt_response)


if __name__ == "__main__":  # pragma: no cover - manual usage
    main()
