import os


# This will get updated below, see: _true_color_supported
def true_color_supported() -> bool:
    """Check if truecolor is supported by the current tty.

    Note: this currently only checks to see if COLORTERM contains
          one of the following enumerated case-sensitive values:
             - truecolor
             - 24bit

    """
    color_term = os.getenv('COLORTERM', '')
    return True if any(check in color_term for check in ['truecolor', '24bit']) else False


TRUE_COLOR_SUPPORTED = true_color_supported()

ESCAPE: str = '\x1b'
PREFIX: str = f'{ESCAPE}['
TRUEPREFIX: str = f'{PREFIX}38;2;'
SUFFIX: str = 'm'
RESET: str = f'{PREFIX}0{SUFFIX}'

# style codes
#  Not all of these are supported within all terminals
BRIGHT: str = f'{PREFIX}1{SUFFIX}'
DIM: str = f'{PREFIX}2{SUFFIX}'

BLINKING: str = f'{PREFIX}5{SUFFIX}'
STROBING: str = f'{PREFIX}6{SUFFIX}'

UNDERLINED: str = f'{PREFIX}4{SUFFIX}'
DOUBLE_UNDERLINE: str = f'{PREFIX}21{SUFFIX}'

ITALICS: str = f'{PREFIX}3{SUFFIX}'
INVERTED: str = f'{PREFIX}7{SUFFIX}'
HIDDEN: str = f'{PREFIX}8{SUFFIX}'
STRIKE_THROUGH: str = f'{PREFIX}9{SUFFIX}'
