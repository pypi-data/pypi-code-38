import os
from os.path import abspath, dirname, splitext


def get_TTF_path() -> str:
    for f in os.listdir(dirname(abspath(__file__))):
        if splitext(f)[1].lower() in ['.ttf', '.ttc', '.otf']:
            TTF_path = dirname(abspath(__file__))+'/'+f
            return TTF_path
    else:
        raise FileNotFoundError(f'Font file(TTF/TTC/OTF) does not exist under package path. Re-installing the package may fix the problem.')