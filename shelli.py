import subprocess
from openai import OpenAI

client = OpenAI(api_key='sk-agent-x-fsZmmi5uVEG6lyqnRCj7T3BlbkFJdBYZovJ7z6pwmAGC2xQc')

# Function to execute a terminal command and get the response
def execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Function to interact with ChatGPT
def chat_with_gpt(prompt):
    response = client.completions.create(engine="text-davinci-003",
    prompt=prompt,
    max_tokens=150)
    return response.choices[0].text.strip()

# Example usage
terminal_command = "ls -la"
command_output = execute_command(terminal_command)

# Create a prompt for ChatGPT based on the command output
gpt_prompt = f"The output of the command '{terminal_command}' is:\n{command_output}\nWhat should I do next?"
gpt_response = chat_with_gpt(gpt_prompt)

print(gpt_response)