from microlab.io.files import file_exist
from playsound import playsound


def play(path):
    if file_exist(path=path):
        playsound(path)
