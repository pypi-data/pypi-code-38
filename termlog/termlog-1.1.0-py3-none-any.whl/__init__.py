from typing import Any

from .__metadata__ import package_metadata
from .colors import Color, rgb
from .formatting import beautify, format
from .palettes import Palette, get_palette, set_palette
from .terminal import echo, set_config

__author__ = package_metadata.author
__version__ = package_metadata.version


def __getattr__(name: str) -> Any:
    """__getattr__ should be called _after_ __getattribute__ and only if
    __getattribute__ could not find the correct value...

    This is magic and will grab the color of the default palette as if
    it were part of the top level termlog structure.

    """
    palette = locals()['palette'] = palettes.get_palette()
    # This handles from termlog import *
    #   But from termlog import * prevents updates to the palette,
    #   And this is by design since imports are technically cached within
    #   pythons import system.  It's all code, so we could force it to
    #   "just work" but that seems like a bad idea.
    #
    # The best practice is to use termlog as a namespace/prefix:
    #
    #    >>> import termlog
    #    >>> import termlog.palettes
    #    >>> termlog.red('hi')
    #    '\x1b[31mhi\x1b[0m'
    #    >>> termlog.red('hi', truecolor=True)
    #    '\x1b[38;2;170;0;0mhi\x1b[0m'
    #    >>> termlog.set_palette(termlog.palettes.SolarizedDark())
    #    >>> termlog.red('hi')
    #    '\x1b[31mhi\x1b[0m'
    #    >>> termlog.red('hi', truecolor=True)
    #    '\x1b[38;2;220;50;47mhi\x1b[0m'
    #
    if name == '__all__':
        return [key for key in palette.__annotations__ if isinstance(getattr(palette, key), Color)] + [
            'Color', 'rgb', 'format', 'beautify', 'get_palette', 'set_palette', 'Palette', 'echo', 'set_config'
            ]
    else:
        return getattr(palette, name)
