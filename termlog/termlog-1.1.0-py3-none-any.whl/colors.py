"""Color module

Contains resources to build 256 (standard) and 16m (true-color) text
output.

"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from .constants import (
    BLINKING,
    BRIGHT,
    DIM,
    DOUBLE_UNDERLINE,
    HIDDEN,
    INVERTED,
    ITALICS,
    PREFIX,
    RESET,
    STRIKE_THROUGH,
    STROBING,
    SUFFIX,
    TRUE_COLOR_SUPPORTED,
    TRUEPREFIX,
    UNDERLINED
)
from .decorations import factory

__all__ = ('Color', 'rgb')


_colors: Dict[Tuple[int, int, int], 'Color'] = {}


@factory(names=['red', 'green', 'blue'], repository=_colors)  # look up color by rgb value
@dataclass
class Color:
    """A data structure for packaging up Color display information

    Example:
        >>> from termlog import Color, echo
        >>> solarized_red = Color(red=220, green=50, blue=47)
        >>> solarized_magenta = Color(red=221, green=54, blue=130)
        >>> msg = ...
        >>> echo(f'{solarized_red("ERROR")}: {solarized_magenta(msg)}')

    Attributes:
        red: the value for the red aspect of the color [0-255]
        green: the value for the green aspect of the color [0-255]
        blue: the value for the blue aspect of the color [0-255]
        color_prefix: the string prefix when true-color is not enabled
        true_color_prefix: the string prefix for when true-color is enabled
        suffix: the reset suffix
        truecolor: forces output to use truecolor
        prefix: calculated prefix based on flags

    Flags:
        bright: adds bold/bright flag
        dim: adds dim flag
        italics: adds italics flag
        underlined: adds underlined flag
        double_underlined: adds double underlined flag
        strobing: adds strobing flag
        blinking: adds blinking flag
        inverted: flag that inverts foreground and background colors
        strike_through: adds strike-through flag
        hidden: adds hidden flag

    """
    red: int = 0
    green: int = 0
    blue: int = 0
    term_color: Optional[int] = None
    color_prefix: str = ''
    true_color_prefix: str = f'{TRUEPREFIX}{{red}};{{green}};{{blue}}{SUFFIX}'
    suffix: str = f'{RESET}'
    truecolor: bool = TRUE_COLOR_SUPPORTED
    name: str = ''

    # style attributes
    dim: bool = False
    bright: bool = False
    italics: bool = False
    underlined: bool = False
    double_underlined: bool = False
    blinking: bool = False
    strobing: bool = False
    inverted: bool = False
    hidden: bool = False
    strike_through: bool = False

    # style attributes combined
    postfix: str = field(default='', init=False)

    def __set_name__(self, owner: Any, name: str):
        setattr(owner, name, self)
        self.name = name

    def __post_init__(self):
        # Cap red, green and blue to integer values
        self.red = max(min(int(self.red or 0), 255), 0)
        self.green = max(min(int(self.green or 0), 255), 0)
        self.blue = max(min(int(self.blue or 0), 255), 0)

        if self.term_color is not None and not self.color_prefix:
            self.color_prefix = f'{PREFIX}{self.term_color}{SUFFIX}'

        if self.truecolor is None:
            self.truecolor = TRUE_COLOR_SUPPORTED

        self.true_color_prefix = self.true_color_prefix.format(red=self.red, green=self.green, blue=self.blue)
        if self.true_color_prefix and not self.color_prefix:
            self.color_prefix = self.true_color_prefix
        elif self.color_prefix and not self.true_color_prefix:
            self.true_color_prefix = self.color_prefix

        self.postfix = self.generate_postfix(
            dim=self.dim,
            bright=self.bright,
            italics=self.italics,
            underlined=self.underlined,
            double_underlined=self.double_underlined,
            blinking=self.blinking,
            strobing=self.strobing,
            strike_through=self.strike_through,
            hidden=self.hidden,
            inverted=self.inverted,
            )

    @staticmethod
    def generate_postfix(
            dim: Optional[bool] = None,
            bright: Optional[bool] = None,
            italics: Optional[bool] = None,
            underlined: Optional[bool] = None,
            double_underlined: Optional[bool] = None,
            hidden: Optional[bool] = None,
            inverted: Optional[bool] = None,
            strike_through: Optional[bool] = None,
            blinking: Optional[bool] = None,
            strobing: Optional[bool] = None,
            ) -> str:
        """Creates a prefix given the constraints above

        Notes:
            The following options are grouped and only one flag will be
            honored for each grouping:

            * color, truecolor
            * strobing, blinking
            * dim, bright
            * underlined, double_underlined

            Additionally, if the hidden flag is set, none of the other
            flags will be honored

        Args:
            dim: sets the dim flag
            bright: sets the bright flag
            italics: sets the italics flag
            hidden: hide the output
            inverted: invert the foreground and background colors
            strike_through: set the strike_through flag
            underlined: set the underline flag
            double_underlined: set the underline flag
            blinking: set the blinking flag
            strobing: set the strobing flag

        Returns:
            message with escape sequences for terminal colors

        """
        postfix = ''
        # ignore all of the other flags if hidden
        if hidden:
            postfix += HIDDEN
        else:
            if inverted:
                postfix += INVERTED
            if strike_through:
                postfix += STRIKE_THROUGH
            if italics:
                postfix += ITALICS
            # dim or bright but not both and only if we don't use
            #   truecolor
            if dim:
                postfix += DIM
            elif bright:
                postfix += BRIGHT
            # underline or double underline but not both
            if underlined:
                postfix += UNDERLINED
            elif double_underlined:
                postfix += DOUBLE_UNDERLINE
            # blinking or strobing but not both
            if blinking:
                postfix += BLINKING
            elif strobing:
                postfix += STROBING
        return postfix

    def __hash__(self):
        return hash((self.red, self.green, self.blue))

    def __call__(self, message: Any, color: bool = True, truecolor: Optional[bool] = None) -> str:
        """Colors a message

        Args:
            color: flag to disable color entirely
            truecolor: flag to explicitly enable truecolor

        Returns:
            message with escape sequences for terminal colors

        """
        colored_message = message
        prefix = ''
        if color is not False and (truecolor is True or (truecolor is None and self.truecolor)):
            prefix = self.true_color_prefix + self.postfix
        elif color:
            prefix = self.color_prefix + self.postfix
        if prefix:
            colored_message = f'{prefix}{message}{self.suffix}'
        return colored_message

    def __eq__(self, other):
        return id(self) == id(other)

    def __getitem__(self, item):
        if item in ('red', 'green', 'blue'):
            return getattr(self, item)
        else:
            raise KeyError(f'Could not find {item} in {self}')

    @staticmethod
    def keys():
        return ('red', 'green', 'blue')

    @staticmethod
    def __len__():
        return 3

    def __iter__(self):
        for name in ('red', 'green', 'blue'):
            yield getattr(self, name)


def rgb(message: Any, red: int = 0, green: int = 0, blue: int = 0, color: bool = True, truecolor: Optional[bool] = None) -> str:
    """Add any true color to *message*.

    Example:
        >>> from termlog import echo, rgb, Color
        >>> c = Color(red=223, green=81, blue=127)
        >>> print(f'{c!r}')
        Color(red=223, green=81, blue=127, color_prefix='', true_color_prefix='{TRUEPREFIX}{red};{green};{blue}{SUFFIX}', suffix='{RESET}', truecolor=False)
        >>> f'A {rgb("colored", **c)} message'
        'A {TRUEPREFIX}223;81;127{SUFFIX}colored{RESET} message'

    Note: this only works if the terminal supports true color and there
          is no way to definitively determine if truecolor is supported
          by the terminal.

    Args:
        message: text to color
        red: red portion of color [0 to 255]
        green: green portion of color [0 to 255]
        blue: blue portion of color [0 to 255]
        color: enable color on output

    Returns:
        Colored text if color is enabled

    """
    _color = Color(red=red, green=green, blue=blue, truecolor=True if truecolor is not False else False)
    colored_text = _color(message, color=color)
    return colored_text
