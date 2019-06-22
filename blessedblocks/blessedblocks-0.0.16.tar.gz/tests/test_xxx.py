import pytest
from blessedblocks.line import Line
from blessed import Terminal

term = Terminal()

def test_parse_blink():
    line = Line('{t.blink}xy{t.normal}{t.green}z', 3, '^')
    print(('\n' + line.display + '{t.normal}').format(t=term))
    print(line.display)
    assert line.plain == 'xyz'
    assert line.last_seq == '{t.green}'
