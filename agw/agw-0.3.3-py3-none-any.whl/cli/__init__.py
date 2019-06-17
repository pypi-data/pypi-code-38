"""
Usage:
    agw cursor
    agw jiggle
    agw screenshot (--capture | --find)

Options:
    -h --help       Display this screen.
    --version       Display application version.
"""
import docopt
from .cursor import position as cursor
from .jiggler import jiggle
from .screen import capture, find


def main():
    args = docopt.docopt(__doc__)

    if args.get("cursor") is True:
        cursor()
    elif args.get("jiggle") is True:
        jiggle()
    elif args.get("screenshot") is True and args.get("--capture"):
        capture()
    elif args.get("screenshot") is True and args.get("--find"):
        find()
