import sys
import threading
import itertools
from time import sleep


def spin():
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while True:
        sys.stdout.write(next(spinner))
        sleep(0.1)
        sys.stdout.flush()
        sys.stdout.write('\b')


def get_spinner_thread():
    return threading.Thread(target=spin, daemon=True)