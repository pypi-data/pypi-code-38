from dataclasses import asdict, dataclass
from itertools import product
from typing import Any, Optional

import pytest

from ..constants import PREFIX, RESET, SUFFIX, TRUEPREFIX, true_color_supported


@dataclass
class ColorTestCase:
    func_name: str
    message: Any = ''
    color: Optional[bool] = None
    truecolor: Optional[bool] = true_color_supported()
    expected: str = ''

    def __str__(self):
        return ' '.join(f'{key}={value}' for key, value in asdict(self).items())


test_cases = [
    # standard uses
    ColorTestCase('black', message='hi', color=True, truecolor=False, expected=f'{PREFIX}30{SUFFIX}hi{RESET}'),
    ColorTestCase('red', message='hi', color=True, truecolor=False, expected=f'{PREFIX}31{SUFFIX}hi{RESET}'),
    ColorTestCase('green', message='hi', color=True, truecolor=False, expected=f'{PREFIX}32{SUFFIX}hi{RESET}'),
    ColorTestCase('yellow', message='hi', color=True, truecolor=False, expected=f'{PREFIX}33{SUFFIX}hi{RESET}'),
    ColorTestCase('blue', message='hi', color=True, truecolor=False, expected=f'{PREFIX}34{SUFFIX}hi{RESET}'),
    ColorTestCase('magenta', message='hi', color=True, truecolor=False, expected=f'{PREFIX}35{SUFFIX}hi{RESET}'),
    ColorTestCase('cyan', message='hi', color=True, truecolor=False, expected=f'{PREFIX}36{SUFFIX}hi{RESET}'),
    ColorTestCase('white', message='hi', color=True, truecolor=False, expected=f'{PREFIX}37{SUFFIX}hi{RESET}'),

    # truecolor uses
    ColorTestCase('black', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}30;30;30{SUFFIX}hi{RESET}'),
    ColorTestCase('blue', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}0;0;170{SUFFIX}hi{RESET}'),
    ColorTestCase('cyan', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}0;170;170{SUFFIX}hi{RESET}'),
    ColorTestCase('green', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}0;170;0{SUFFIX}hi{RESET}'),
    ColorTestCase('magenta', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}170;0;170{SUFFIX}hi{RESET}'),
    ColorTestCase('red', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}170;0;0{SUFFIX}hi{RESET}'),
    ColorTestCase('yellow', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}170;170;0{SUFFIX}hi{RESET}'),
    ColorTestCase('white', message='hi', color=True, truecolor=True, expected=f'{TRUEPREFIX}170;170;170{SUFFIX}hi{RESET}'),

    # test uncolored uses
    ColorTestCase('black', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('blue', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('cyan', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('green', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('grey', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('magenta', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('red', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('yellow', message='hi', color=False, truecolor=False, expected='hi'),
    ColorTestCase('white', message='hi', color=False, truecolor=False, expected='hi'),
    ]


@pytest.mark.parametrize('test_case', test_cases, ids=list(map(str, test_cases)))
def test_colors(test_case):
    import termlog

    func = getattr(termlog, test_case.func_name)
    result = func(message=test_case.message, color=test_case.color, truecolor=test_case.truecolor)
    assert result == test_case.expected, f'TrueColor={test_case.truecolor} ({tuple(result)}) != ({tuple(test_case.expected)})'


@dataclass
class RgbColorTestCase:
    red: int = 0
    green: int = 0
    blue: int = 0
    message: Any = ''
    color: Optional[bool] = None
    truecolor: Optional[bool] = None

    def __str__(self):
        return ' '.join(f'{key}={value}' for key, value in asdict(self).items())


reds = greens = blues = [0, 127, 255]
truecolors = [True, False]
rgb_test_cases = []
for values in product(reds, greens, blues, truecolors):
    rgb_test_cases.append(RgbColorTestCase(red=values[0], green=values[1], blue=values[2], message='hi', truecolor=values[3]))


@pytest.mark.parametrize('test_case', rgb_test_cases, ids=list(map(str, rgb_test_cases)))
def test_colors_rgb(test_case):
    from .. import colors

    prefix = f'\x1b[38;2;{test_case.red};{test_case.green};{test_case.blue}m'
    reset = f'\x1b[0m'
    expected = f'{prefix}{test_case.message}{reset}' if test_case.truecolor else f'{test_case.message}'

    result = colors.rgb(red=test_case.red, blue=test_case.blue, green=test_case.green, message=test_case.message, color=test_case.color, truecolor=test_case.truecolor)
    assert result == expected
