# AgentZero
# ChatGPT Voice Command Interface for iTerm

This project provides a voice-controlled interface for executing commands in iTerm using ChatGPT's natural language processing capabilities. It allows users to speak commands, which are then interpreted by ChatGPT and potentially executed in the terminal.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/FritzHeider/chatgpt-voice-iterm.git
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Obtain an API key from OpenAI by creating an account and generating an API key.

## Usage

1. Run the script:

    ```bash
    python3 voice_commander.py
    ```

2. Speak commands into your microphone. ChatGPT will interpret your commands and suggest actions.

3. Confirm or deny the suggested action. If confirmed, the command will be executed in iTerm.

4. To stop the program, say "stop" or close the window.

## Configuration

- You can configure the script by modifying the `voice_commander.py` file directly. Be sure to update the OpenAI API key and adjust any settings as needed.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
