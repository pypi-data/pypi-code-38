import os
import inspect
import colorama


def cprint(text, color='reset', verbose=True):
    """Print with colorama.

    text:       Text to be colored.
    color:      Color string or integer for foreground.
                Tuple of integers for both foreground and background.
    verbose:    Option to use this function as a verbose mode.
    """
    if verbose:
        colorama.init(autoreset=True)

        if type(color) is str:
            color = colorama.Fore.__dict__[color.upper()]
        elif type(color) is int:
            color = f"\x1b[38;5;{color}m"
        elif type(color) is tuple:
            color = f"\x1b[38;5;{color[0]};48;5;{color[1]}m"
            width, _ = os.get_terminal_size()
            text = f"{text}{' ' * (width - len(text))}"

        print(f"{color}{text}")
        colorama.deinit()


def doc(arg):
    """Docstring decorator.

    arg:    Docstring text or object.
    """
    def decorator(func):
        if type(arg) is str:
            func.__doc__ = arg
        elif inspect.isclass(arg):
            func.__doc__ = arg.__doc__
        else:
            func.__doc__ = None

        return func
    return decorator
