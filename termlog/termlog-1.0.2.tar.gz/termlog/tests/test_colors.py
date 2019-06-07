from dataclasses import dataclass
from typing import Any, Optional

import pytest

from ..colors import true_color_supported


@dataclass
class ColorTestCase:
    func_name: str
    message: Any = ''
    color: Optional[bool] = None
    expected: str = ''


TRUE_COLOR = true_color_supported()


@pytest.mark.parametrize('test_case', [
    # standard uses
    ColorTestCase('black', message='hi', color=True, expected='\x1b[30mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;0;0;0mhi\x1b[0m'),
    ColorTestCase('blue', message='hi', color=True, expected='\x1b[34mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;0;0;255mhi\x1b[0m'),
    ColorTestCase('cyan', message='hi', color=True, expected='\x1b[36mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;0;255;255mhi\x1b[0m'),
    ColorTestCase('green', message='hi', color=True, expected='\x1b[32mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;0;255;0mhi\x1b[0m'),
    ColorTestCase('grey', message='hi', color=True, expected='\x1b[37m\x1b[2mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;127;127;127mhi\x1b[0m'),
    ColorTestCase('magenta', message='hi', color=True, expected='\x1b[35mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;255;0;255mhi\x1b[0m'),
    ColorTestCase('red', message='hi', color=True, expected='\x1b[31mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;255;0;0mhi\x1b[0m'),
    ColorTestCase('yellow', message='hi', color=True, expected='\x1b[33mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;255;255;0mhi\x1b[0m'),
    ColorTestCase('white', message='hi', color=True, expected='\x1b[37mhi\x1b[0m' if not TRUE_COLOR else f'\x1b[38;2;255;255;255mhi\x1b[0m'),

    # test uncolored uses
    ColorTestCase('black', message='hi', color=False, expected='hi'),
    ColorTestCase('blue', message='hi', color=False, expected='hi'),
    ColorTestCase('cyan', message='hi', color=False, expected='hi'),
    ColorTestCase('green', message='hi', color=False, expected='hi'),
    ColorTestCase('grey', message='hi', color=False, expected='hi'),
    ColorTestCase('magenta', message='hi', color=False, expected='hi'),
    ColorTestCase('red', message='hi', color=False, expected='hi'),
    ColorTestCase('yellow', message='hi', color=False, expected='hi'),
    ColorTestCase('white', message='hi', color=False, expected='hi'),
    ])
def test_colors(test_case):
    from .. import colors

    func = getattr(colors, test_case.func_name)
    result = func(message=test_case.message, color=test_case.color, truecolor=TRUE_COLOR)
    assert result == test_case.expected, f'TrueColor={TRUE_COLOR} ({tuple(result)}) != ({tuple(test_case.expected)})'


@dataclass
class RgbColorTestCase:
    red: int = 0
    green: int = 0
    blue: int = 0
    message: Any = ''
    color: Optional[bool] = None


@pytest.mark.parametrize('test_case', [
    # black
    RgbColorTestCase(red=0, green=0, blue=0, message='hi', color=True),
    # blue
    RgbColorTestCase(red=0, green=0, blue=255, message='hi', color=True),
    # cyan
    RgbColorTestCase(red=0, green=255, blue=255, message='hi', color=True),
    # green
    RgbColorTestCase(red=0, green=255, blue=0, message='hi', color=True),
    # grey
    RgbColorTestCase(red=127, green=127, blue=127, message='hi', color=True),
    # magenta
    RgbColorTestCase(red=255, green=0, blue=255, message='hi', color=True),
    # red
    RgbColorTestCase(red=255, green=0, blue=0, message='hi', color=True),
    # yellow
    RgbColorTestCase(red=255, green=255, blue=0, message='hi', color=True),
    # white
    RgbColorTestCase(red=255, green=255, blue=255, message='hi', color=True),

    # black
    RgbColorTestCase(red=0, green=0, blue=0, message='hi', color=False),
    # blue
    RgbColorTestCase(red=0, green=0, blue=255, message='hi', color=False),
    # cyan
    RgbColorTestCase(red=0, green=255, blue=255, message='hi', color=False),
    # green
    RgbColorTestCase(red=0, green=255, blue=0, message='hi', color=False),
    # grey
    RgbColorTestCase(red=127, green=127, blue=127, message='hi', color=False),
    # magenta
    RgbColorTestCase(red=255, green=0, blue=255, message='hi', color=False),
    # red
    RgbColorTestCase(red=255, green=0, blue=0, message='hi', color=False),
    # yellow
    RgbColorTestCase(red=255, green=255, blue=0, message='hi', color=False),
    # white
    RgbColorTestCase(red=255, green=255, blue=255, message='hi', color=False),
    ])
def test_colors_rgb(test_case):
    from .. import colors

    prefix = f'\x1b[38;2;{test_case.red};{test_case.green};{test_case.blue}m'
    reset = f'\x1b[0m'
    expected = f'{prefix}{test_case.message}{reset}' if test_case.color else f'{test_case.message}'

    result = colors.rgb(red=test_case.red, blue=test_case.blue, green=test_case.green, message=test_case.message, color=test_case.color, truecolor=True)
    assert result == expected


def test_colors_factory():
    from .. import colors

    all_colors = {
        'BLACK': colors.BLACK, 'RED': colors.RED, 'GREEN': colors.GREEN,
        'BLUE': colors.BLUE, 'CYAN': colors.CYAN, 'MAGENTA': colors.MAGENTA,
        'YELLOW': colors.YELLOW, 'WHITE': colors.WHITE, 'GREY': colors.GREY
        }

    new_colors = {
        'BLACK': [colors.Color(), colors.Color(red=0, green=0, blue=0)],
        'RED': [colors.Color(red=255), colors.Color(red=255, green=0, blue=0)],
        'YELLOW': [colors.Color(red=255, green=255), colors.Color(red=255, green=255, blue=0)],
        'MAGENTA': [colors.Color(red=255, blue=255), colors.Color(red=255, green=0, blue=255)],
        'CYAN': [colors.Color(green=255, blue=255), colors.Color(red=0, green=255, blue=255)],
        'BLUE': [colors.Color(blue=255), colors.Color(red=0, green=0, blue=255)],
        'GREEN': [colors.Color(green=255), colors.Color(red=0, green=255, blue=0)],
        'WHITE': [colors.Color(red=255, green=255, blue=255)],
        'GREY': [colors.Color(red=127, green=127, blue=127)],
        }

    for index, color in enumerate(all_colors.values()):
        previous = list(all_colors.values())[index - 1]
        assert color != previous
        assert color.keys() == ('red', 'green', 'blue')

    for name, values in new_colors.items():
        original = all_colors[name]
        assert all([original == value for value in values]), f'{name}: {original} not equal to {values}'

    color = colors.Color()
    assert len(color) == 3
    assert list(color) == [0, 0, 0]
    assert list(color.keys()) == ['red', 'green', 'blue']
    for key in color.keys():
        assert color[key] == getattr(color, key)
    with pytest.raises(KeyError):
        assert color['not-a-key']
