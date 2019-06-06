import os
import pwd
import pathlib


def get_username() -> str:
    return pwd.getpwuid(os.getuid())[0]


def get_homepath() -> pathlib.Path:
    return pathlib.Path(os.path.expanduser('~'))
