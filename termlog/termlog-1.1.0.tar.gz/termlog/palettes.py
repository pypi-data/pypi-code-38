"""Palettes allow someone to create a specific color scheme for the
terminal log.
"""
from dataclasses import asdict, dataclass, field
from typing import Dict

from .colors import Color
from .decorations import factory

__all__ = ('get_palette', 'set_palette', 'Palette')
_palettes: Dict[str, 'Palette'] = {}


@factory(names=['name'], repository=_palettes)
@dataclass
class Palette:
    """A data structure to capture colors.

    Palettes can be defined which will modify termlog's color
    and output.

    Example:

        >>> import termlog
        >>> termlog.red('hi', truecolor=True)
        '\x1b[38;2;170;0;0mhi\x1b[0m'

        >>> from dataclasses import dataclass, field
        >>> @dataclass
            class NewPalette(termlog.Palette):
                name: str = 'My special palette'

                red: termlog.Color = field(default=termlog.Color(185, 10, 10, term_color=31))

        >>> p = NewPalette()
        >>> termlog.set_palette(p)
        >>> termlog.red('hi', truecolor=True)
        '\x1b[38;2;185;10;10mhi\x1b[0m'

    """
    name: str = ''
    colors: Dict = field(default_factory=dict)

    def __init_subclass__(cls, **kwargs):
        if cls.name not in _palettes:
            _palettes[cls.name] = cls()
            super().__init_subclass__(**kwargs)
        return _palettes[cls.name]

    def __post_init__(self):
        for key, value in asdict(self).items():
            if isinstance(value, Color):
                self.colors[key] = value

    def __getattr__(self, key):
        if key in self.colors:
            return self.colors[key]
        else:
            raise AttributeError(f'Could not find `{key}` in `{self}`')


@dataclass
class Default(Palette):
    name: str = 'default'

    black: Color = field(default=Color(30, 30, 30, term_color=30))
    red: Color = field(default=Color(170, 0, 0, term_color=31))
    green: Color = field(default=Color(0, 170, 0, term_color=32))
    yellow: Color = field(default=Color(170, 170, 0, term_color=33))
    blue: Color = field(default=Color(0, 0, 170, term_color=34))
    magenta: Color = field(default=Color(170, 0, 170, term_color=35))
    cyan: Color = field(default=Color(0, 170, 170, term_color=36))
    white: Color = field(default=Color(170, 170, 170, term_color=37))

    bright_black: Color = field(default=Color(60, 60, 60, term_color=90))
    bright_red: Color = field(default=Color(255, 0, 0, term_color=91))
    bright_green: Color = field(default=Color(0, 255, 0, term_color=92))
    bright_yellow: Color = field(default=Color(255, 255, 0, term_color=93))
    bright_blue: Color = field(default=Color(0, 0, 255, term_color=94))
    bright_magenta: Color = field(default=Color(255, 0, 255, term_color=95))
    bright_cyan: Color = field(default=Color(0, 255, 255, term_color=96))
    bright_white: Color = field(default=Color(255, 255, 255, term_color=97))

    dim_black: Color = field(default=Color(0, 0, 0, term_color=30, dim=True))
    dim_red: Color = field(default=Color(85, 0, 0, term_color=31, dim=True))
    dim_green: Color = field(default=Color(0, 85, 0, term_color=32, dim=True))
    dim_yellow: Color = field(default=Color(85, 85, 0, term_color=33, dim=True))
    dim_blue: Color = field(default=Color(0, 0, 85, term_color=34, dim=True))
    dim_magenta: Color = field(default=Color(85, 0, 85, term_color=35, dim=True))
    dim_cyan: Color = field(default=Color(0, 85, 85, term_color=36, dim=True))
    dim_white: Color = field(default=Color(85, 85, 85, term_color=37, dim=True))
    grey: Color = field(default=dim_white)


@dataclass
class SolarizedDark(Palette):
    name: str = 'solarized_dark'

    # Standard terminal names
    black: Color = field(default=Color(7, 54, 66, term_color=30))
    red: Color = field(default=Color(220, 50, 47, term_color=31))
    green: Color = field(default=Color(133, 153, 0, term_color=32))
    yellow: Color = field(default=Color(181, 137, 0, term_color=33))
    blue: Color = field(default=Color(38, 139, 210, term_color=34))
    magenta: Color = field(default=Color(211, 54, 130, term_color=35))
    cyan: Color = field(default=Color(42, 161, 152, term_color=36))
    white: Color = field(default=Color(238, 232, 213, term_color=37))

    # Standard bright terminal names
    bright_black: Color = field(default=Color(0, 43, 54, term_color=90))
    bright_red: Color = field(default=Color(203, 75, 22, term_color=91))
    bright_green: Color = field(default=Color(88, 110, 117, term_color=92))
    bright_yellow: Color = field(default=Color(101, 123, 131, term_color=93))
    bright_blue: Color = field(default=Color(131, 148, 150, term_color=94))
    bright_magenta: Color = field(default=Color(108, 113, 196, term_color=95))
    bright_cyan: Color = field(default=Color(147, 161, 161, term_color=96))
    bright_white: Color = field(default=Color(253, 246, 227, term_color=97))

    # solarized specific names
    base03: Color = field(default=bright_black)
    base02: Color = field(default=black)
    base01: Color = field(default=bright_green)
    base00: Color = field(default=bright_yellow)
    base0: Color = field(default=bright_blue)
    base1: Color = field(default=bright_cyan)
    base2: Color = field(default=white)
    base3: Color = field(default=bright_white)
    orange: Color = field(default=bright_red)
    violet: Color = field(default=bright_magenta)


_default_palette: Palette = Default()


def get_palette() -> Palette:
    return _default_palette


def set_palette(palette: Palette):
    global _default_palette
    _default_palette = palette
