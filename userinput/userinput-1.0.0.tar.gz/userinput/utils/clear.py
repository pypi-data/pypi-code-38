import os
from IPython.display import clear_output

def clear():
    os.system('clear') if os.name == "posix" else os.system('cls')
    clear_output(wait=True)