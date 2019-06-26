from sys import exit
from prompt_toolkit import PromptSession

from kismet.core import process

print("Greetings, human! I am Kismet <3")
print("Input a roll and press ENTER.")

# Create prompt object.
session = PromptSession("> ")

while True:
    try:
        text = session.prompt()
        print(process(text))
    except EOFError:
        exit(0)
    except KeyboardInterrupt:
        exit(130)
