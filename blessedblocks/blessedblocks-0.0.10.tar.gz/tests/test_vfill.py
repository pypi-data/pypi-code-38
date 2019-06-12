import pytest
from blessedblocks.blocks import VFillBlock
from blessed import Terminal

term = Terminal()
def test_simple():
    vb = VFillBlock('x')
    out = vb.display(1, 10, 0, 0)
    print('len', len(out))
    #print('\n' + '\n'.join(out).format(t=term))
    print('\n'.join(out).format(t=term))
    #assert out == ['{t.normal}' + 'x'] * 10
    assert out == ['x'] * 10

    
