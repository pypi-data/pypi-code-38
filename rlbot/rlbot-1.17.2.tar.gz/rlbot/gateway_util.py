import os
import subprocess

from rlbot.utils.structures.game_interface import get_dll_directory


def launch():
    print("Launching RLBot.exe...")
    process = subprocess.Popen([os.path.join(get_dll_directory(), "RLBot.exe")])
    return process
