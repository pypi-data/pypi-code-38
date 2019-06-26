from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pytest


@dataclass
class BeautifyData:
    message: Any
    expected: str = ''
    indent: int = 0
    lexer: Any = None


@pytest.mark.parametrize('test_data', [
    BeautifyData('a', expected='a'),  # expected='\x1b[38;5;247ma\x1b[39m'),
    BeautifyData('ls -lashtr $HOME', lexer='bash', expected='ls -lashtr \x1b[38;2;25;23;124m$HOME\x1b[39m'),
    BeautifyData('SELECT * FROM some_table;', expected='\x1b[38;2;0;128;0;01mSELECT\x1b[39;00m \x1b[38;2;102;102;102m*\x1b[39m \x1b[38;2;0;128;0;01mFROM\x1b[39;00m some_table;'),
    BeautifyData('SELECT * FROM some_table;', lexer='postgres', expected='\x1b[38;2;0;128;0;01mSELECT\x1b[39;00m \x1b[38;2;102;102;102m*\x1b[39m \x1b[38;2;0;128;0;01mFROM\x1b[39;00m some_table;'),
    BeautifyData(Path('.'), expected='.'),
    ])
def test_beautify(test_data):
    from ..formatting import beautify

    input_params = asdict(test_data)
    expected = input_params.pop('expected')
    result = beautify(**input_params)
    assert result == expected, f'{result} did not match {expected}, {(result,)}'
