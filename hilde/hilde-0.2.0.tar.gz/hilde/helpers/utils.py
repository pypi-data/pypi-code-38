""" A simple timer """

import sys
from time import time, strftime
import inspect

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    tqdm = lambda x, *args, **kwargs: x


def progressbar(func):
    """ show progressbar when looping """
    return tqdm(func, file=sys.stdout)


# print in bold
def bold(text):
    """ print test in bold face """
    return "\033[1m" + text + "\033[0m"


def talk(message):
    """ https://stackoverflow.com/a/2654130/5172579 """

    curframe = inspect.currentframe()
    frame = inspect.getouterframes(curframe, 2)[1]

    file = frame[1].split("hilde")[-1][1:]

    timestr = strftime("%H:%M:%S %Y/%m/%d")

    print(f"[{timestr} from {file}, l. {frame[2]}, {frame[3]}():")
    print(f"  {message}\n")


class Timer:
    def __init__(self, message=None):
        self.time = time()

        if message:
            print(message)

    def __call__(self, info_str=""):
        """ print how much time elapsed """

        time_str = f"{time() - self.time:.3f}s"

        if info_str.strip():
            print(f".. {info_str} in {time_str}")
        else:
            print(f".. time elapsed: {time_str}")
        return float(time_str[:-1])
