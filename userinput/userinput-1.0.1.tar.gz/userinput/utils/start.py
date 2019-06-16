from .clear import clear
from typing import Callable
from time import sleep

def start(function:Callable):
    def wrapper(*args, **kwargs):
        try:
            for i in reversed(range(5)):
                print("Please type CTRL+C to start within {i} seconds...".format(i=i))
                sleep(1)
                clear()
            print("Skipping execution.")
        except KeyboardInterrupt:
            print("Starting!")
            function(*args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper