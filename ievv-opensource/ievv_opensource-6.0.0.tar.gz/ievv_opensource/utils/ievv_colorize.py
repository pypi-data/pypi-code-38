from django.conf import settings
from termcolor import colored


#: Red color constant for :func:`.ievv_colorize`.
COLOR_RED = 'red'

#: Blue color constant for :func:`.ievv_colorize`.
COLOR_BLUE = 'blue'

#: Yellow color constant for :func:`.ievv_colorize`.
COLOR_YELLOW = 'yellow'

#: Grey color constant for :func:`.ievv_colorize`.
COLOR_GREY = 'grey'

#: Green color constant for :func:`.ievv_colorize`.
COLOR_GREEN = 'green'


def colorize(text, color, bold=False):
    """
    Colorize a string for stdout/stderr.

    Colors are only applied if :setting:`IEVV_COLORIZE_USE_COLORS` is
    ``True`` or not defined (so it defaults to ``True``).

    Examples:

        Print blue text::

            from ievv_opensource.utils import ievv_colorize

            print(ievv_colorize('Test', color=ievv_colorize.COLOR_BLUE))

        Print bold red text::

            print(ievv_colorize('Test', color=ievv_colorize.COLOR_RED, bold=True))

    Args:
        text: The text (string) to colorize.
        color: The color to use.
            Should be one of:

            - :obj:`.COLOR_RED`
            - :obj:`.COLOR_BLUE`
            - :obj:`.COLOR_YELLOW`
            - :obj:`.COLOR_GREY`
            - :obj:`.COLOR_GREEN`
            - ``None`` (no color)
        bold: Set this to ``True`` to use bold font.
    """
    if getattr(settings, 'IEVV_COLORIZE_USE_COLORS', True) and color:
        attrs = []
        if bold:
            attrs.append('bold')
        return colored(text, color=color, attrs=attrs)
    else:
        return text
