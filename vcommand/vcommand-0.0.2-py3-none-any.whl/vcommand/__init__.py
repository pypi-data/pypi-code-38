import sys

import pyttsx3
import speech_recognition


class VCommand():
    def __init__(self, *args, **kwargs):
        self._listener = speech_recognition
        self._speaker = pyttsx3.init()
        self._sleep_state = False
        self._commands = {
            "EXIT": {
                "function": self.exit,
                "description": "Exit the program."
            },
            "SLEEP": {
                "function": self.sleep,
                "description": "The program will sleep until it hears the word 'WAKE UP'."
            },
            "LIST COMMANDS": {
                "function": self.display_commands,
                "description": "Provide a list of available commands."
            },
        }
        return super().__init__(*args, **kwargs)

    def command(self, name: str, description: str):
        def decorator(f):
            self.add_command(name, f, description)
        return decorator

    def add_command(self, name: str, function: str, description: str):
        if not isinstance(name, str):
            raise ValueError(f"Command: {name}, is not a str.")
        if name in self._commands:
            raise KeyError(f"Command: {name}, already exists.")
        if not callable(function):
            raise ValueError(f"Function: {function}, is not callable.")
        if description == None:
            raise ValueError(f"Description cannot be none.")
        if description == "":
            raise ValueError(f"Description cannot be an empty string.")
        self._commands.setdefault(
            name.upper(),
            {
                "function": function,
                "description": str(description)
            })

    def start(self, debug: bool = False):
        intro = [
            "* The program has started listening.",
            "* Say \"LIST COMMANDS\" for a list of commands.\n",
        ]
        print("\n".join(intro))
        while self._listener and self._speaker and self._commands:
            while True:
                command = self.listen()
                if debug == 1:
                    print("You said:", command)
                if command in self._commands:
                    try:
                        self._commands[command]["function"]()
                        statement = ""
                    except Exception as e:
                        self.log_error(f"{command}: {e}")
                        statement = ""
                    break

    def listen(self) -> str:
        recognizer = self._listener.Recognizer()
        microphone = self._listener.Microphone()
        with microphone as source:
            audio = recognizer.listen(source)
            try:
                result = recognizer.recognize_google(audio)
                return str(result).upper()
            except Exception as e:
                self.log_error(f"LISTEN: {e}")
                return ""

    def speak(self, value):
        self._speaker.say(str(value))
        self._speaker.runAndWait()

    def set_speaker_properties(self, properties: dict):
        for k in properties:
            self._speaker.setProperty(k, properties[k])

    def exit(self):
        print("Goodbye.")
        self.speak("Goodbye.")
        sys.exit()

    def sleep(self):
        self.speak("I will sleep until you say the command 'WAKE UP'.")
        self._sleep_state = True
        while self._sleep_state:
            command = self.listen()
            if command == "WAKE UP":
                self.speak("I am now listening.")
                self._sleep_state = False

    def display_commands(self):
        print("COMMANDS:")
        for command in self._commands:
            description = self._commands[command]["description"]
            print(f"> {command}: {description}")
        print()

    def log_error(self, e):
        with open("error_log.txt", "a+") as f:
            f.write(f"{str(e)}\n")


if __name__ == "__main__":
    app = VCommand()

    @app.command("HELLO", "Say 'Hello world!'")
    def hello_world():
        app.speak("Hello world!")

    app.start(debug=0)
