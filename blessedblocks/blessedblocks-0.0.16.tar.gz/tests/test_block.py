import pytest
from blessedblocks.blocks import BareBlock
from blessed import Terminal

term = Terminal()
def test_two_lines():
    bb = BareBlock(text='{t.red}This is a line.\n{t.red}This is another')
    out = bb.display(11, 2, 0, 0)
    print('\n' + '\n'.join(out).format(t=term))
    assert out == ['{t.normal}{t.red}This is a l','{t.red}This is ano{t.normal}']

def test_change_colors():
    bb = BareBlock(text='{t.red}This is {t.blue}a line.\n{t.red}This is another')
    out = bb.display(11, 2, 0, 0)
    print('\n' + '\n'.join(out).format(t=term))
    assert out == ['{t.normal}{t.red}This is {t.blue}a l','{t.red}This is ano{t.normal}']
    
def test_two_lines_with_pad():
    bb = BareBlock(text='{t.red}This is a line.\n{t.red}This is another')
    out = bb.display(20, 2, 0, 0)
    print('\n' + '\n'.join(out).format(t=term))
    assert out == ['{t.normal}{t.red}This is a line.     ','{t.red}This is another     {t.normal}']
    
