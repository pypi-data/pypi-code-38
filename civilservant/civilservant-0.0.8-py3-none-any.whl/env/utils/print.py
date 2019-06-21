import os
import sys

COLORBLIND = bool(os.getenv("PIPENV_COLORBLIND", 0))

ANSI_BR_MAGENTA = "\u001b[35;1m" if not COLORBLIND else ""
ANSI_BR_RED = "\u001b[31;1m" if not COLORBLIND else ""
ANSI_BR_WHITE = "\u001b[37;1m" if not COLORBLIND else ""
ANSI_BR_YELLOW = "\u001b[33;1m" if not COLORBLIND else ""
ANSI_RESET = "\u001b[0m" if not COLORBLIND else ""


def _colored_print(color, text, arg=None, file=sys.stdout):
    """Print text with the specified ANSI coloring."""
    print(f"{color}{text}", end="", file=file)
    if arg:
        print(f"{ANSI_BR_WHITE}{arg}", end="", file=file)
    print(f"{ANSI_RESET}", file=file)


def print_action(text, arg=None):
    """Print colored action text."""
    _colored_print(ANSI_BR_MAGENTA, f"{text}…", arg)


def print_error(text, arg=None):
    """Print colored error text."""
    _colored_print(ANSI_BR_RED, f"Error: {text}", arg, file=sys.stderr)


def print_warning(text, arg=None):
    """Print colored warning text."""
    _colored_print(ANSI_BR_YELLOW, f"Warning: {text}", arg, file=sys.stderr)

