import os
import sys
import subprocess


def open_file_with_default_os_opener(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        if sys.platform == "darwin":
            opener = "open"
        else:
            opener = "xdg-open"
        subprocess.call([opener, filename])
