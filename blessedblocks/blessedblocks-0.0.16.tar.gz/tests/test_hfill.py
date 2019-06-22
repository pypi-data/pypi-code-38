import pytest
from blessedblocks.blocks import HFillBlock
from blessed import Terminal

term = Terminal()
def test_simple():
    hb = HFillBlock('x')
    out = hb.display(10, 10, 0, 0)
    print('\n' + '\n'.join(out).format(t=term))
    assert out == ['{t.normal}' + 'x' * 10]

def test_alternating():
    hb = HFillBlock('xy')
    out = hb.display(9, 9, 0, 0)
    print('\n' + '\n'.join(out).format(t=term))
    assert out == ['{t.normal}' + 'xy' * 4 + 'x']
    
def test_longer_than_width():
    hb = HFillBlock('x' * 10)
    out = hb.display(9, 9, 0, 0)
    print('\n' + '\n'.join(out).format(t=term))
    assert out == ['{t.normal}' + 'x' * 9]  

    
