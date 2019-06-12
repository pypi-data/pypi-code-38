import sys


def is_running_directly_from_interactive_shell() -> bool:
    # https://stackoverflow.com/questions/6108330/checking-for-interactive-shell-in-a-python-script
    return sys.stdout.isatty()
    # os.isatty(sys.stdout.fileno())
