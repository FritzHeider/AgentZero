from openai import OpenAI
import os 

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
import os
import json
import subprocess

# Ensure your API key is set

# Define the function
function_definition = {
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

# Configure the API call
response = client.chat.completions.create(model="gpt-3.5-turbo",
messages=[
    {"role": "system", "content": "You are an assistant that suggests terminal commands based on user input."},
    {"role": "user", "content": "Show me the current directory."}
],
functions=[function_definition],
function_call="auto")

# Handle the function call
if response.choices[0].finish_reason == "function_call":
    function_call = response.choices[0].message.function_call
    if function_call.name == 'execute_terminal_command':
        arguments = json.loads(function_call.arguments)
        command = arguments['command']
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print(f"Command executed successfully:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")