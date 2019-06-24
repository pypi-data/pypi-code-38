from PySide2.QtWidgets import *
from PySide2.QtCore import *
import sys
import argparse
from .mainwindow import MainWindow

from .scriptbrowser import ScriptBrowserDialog


def parse_cli_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)

    # flags
    parser.add_argument('--load-example', '-l', type=str, default=None,
                        help='Which code example to load.')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cli_args()
    MainWindow.start_gui(default_script=args.load_example)
