import pytest
from blessedblocks.line import Line
from blessed import Terminal

term = Terminal()

def test_parse_blink():
    line = Line('{t.blink}xy{t.normal}{t.green}z', 3, '^')
    print(('\n' + line.display + '{t.normal}').format(t=term))
    print(line.display)
    assert line.display == '{t.blink}xy{t.normal}{t.green}z'
    assert line.plain == 'xyz'
    assert line.last_seq == '{t.green}'

def test_parse_dups():
    line = Line('{t.green}xy{t.green}z', 3, '^')
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == 'xyz'
    assert line.last_seq == '{t.green}'

def test_parse_contig():
    line = Line('{t.green}{t.blue}xyz', 3, '^')
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == 'xyz'
    assert line.last_seq == '{t.blue}'

def test_parse_contig_3():
    line = Line('{t.green}{t.blue}{t.red}xyz', 3, '^')
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == 'xyz'
    assert line.last_seq == '{t.red}'
    
def test_width_just_center():
    line = Line('{t.green}xy{t.blue}z', 12, '^')
    left_just, right_just = 4*' ', 5*' '
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == left_just + 'xyz' + right_just

def test_width_just_left():
    line = Line('{t.green}xy{t.blue}z', 12, '<')
    left_just, right_just = '', 9*' '
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == left_just + 'xyz' + right_just

def test_width_just_right():
    line = Line('{t.green}xy{t.blue}z', 12, '>')
    left_just, right_just = 9*' ', ''
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == left_just + 'xyz' + right_just

def test_blank_line():
    line = Line('', 12, ',')
    left_just, right_just = '', 12*' '
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == right_just

def test_repeat_to_width():
    line = Line.repeat_to_width('wxyz', 10)
    assert line.plain == 'wxyzwxyzwx'
    assert line.display == '{t.normal}wxyzwxyzwx'    

def test_repeat_to_width_with_seqs():
    line = Line.repeat_to_width('w{t.blue}xy{t.red}z', 10)
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == 'wxyzwxyzwx'
    assert line.display == 'w{t.blue}xy{t.red}zw{t.blue}xy{t.red}zw{t.blue}x'

def test_repeat_to_width_with_seqs():
    line = Line.repeat_to_width('{t.red}-{t.white}-{t.blue}-', 4)
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == '----'
    assert line.display == '{t.red}-{t.white}-{t.blue}-{t.red}-'

def test_vertical_border():
    border = 'x\n'
    line = Line.repeat_to_width(border, 10 * len(border))
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == border * 10
    assert line.display == '{t.normal}' + border * 10

def test_vertical_border_complex():
    border = '{t.red}r{t.white}w{t.blue}b\n'
    text, seqs, last_seq = border_line = Line.parse(border)
    line = Line.repeat_to_width(border, 10 * len(text))
    print(('\n' + line.display + '{t.normal}').format(t=term))
    assert line.plain == text * 10
    assert line.display == border * 10

def test_simple():
    line = Line('simple line of text', 19, '<')
    assert line.plain == 'simple line of text'
    assert line.display == line.plain
    assert line.last_seq is None

def test_just_tag():
    text = '{t.green}'
    line = Line(text, 0, '<')
    assert line.plain == ''
    assert line.display == ''  # ???
    assert line.last_seq == '{t.green}'

def test_two_trailing_tags():
    # green is irrelevant, so dropped from display
    text = '{t.green}{t.blue}'
    line = Line(text, 0, '<')
    assert line.plain == ''
    assert line.display == ''
    assert line.last_seq == '{t.blue}'

def test_two_trailing_tags_with_text():
    # both tags dropped from display because no text follows them
    text = 'abc{t.green}{t.blue}'
    line = Line(text, 3, '<')
    assert line.plain == 'abc'
    assert line.display == 'abc'
    assert line.last_seq == '{t.blue}'

def test_complex():
    text = '{t.green}{}{}}{blac{t.yellow}k justp{t.cyan}laintext{t.pink}x'
    line = Line(text, 26, '<')
    # tags removed,and { and } doubled when not in tag
    assert line.plain == '{}{}}{black justplaintextx'

    # { and } doubled when not part of tag, and end with normal
    assert line.display == '{t.green}{{}}{{}}}}{{blac{t.yellow}k justp{t.cyan}laintext{t.pink}x'
    assert line.last_seq == '{t.pink}'

def test_complex_ends_in_non_normal_tag():
    text = '{t.green}{}{}}{blac{t.yellow}k justp{t.cyan}laintext{t.pink}'
    line = Line(text, 25, '<')
    # tags removed,and { and } doubled when not in tag
    assert line.plain == '{}{}}{black justplaintext'
    # Useless tags at end of markup are removed
    # { and } doubled when not part of tag, and end with normal
    assert line.display == '{t.green}{{}}{{}}}}{{blac{t.yellow}k justp{t.cyan}laintext'
    assert line.last_seq == '{t.pink}'

def test_broken_tag_front():
    text = 't.green}xyz'
    line = Line(text, 11, '<')
    assert line.plain == text
    assert line.display == 't.green}}xyz'  # non-tag brackets doubled in display
    assert line.last_seq is None

def test_last_sequence_normal():
    text = 'hi there, {t.red}Red{t.normal}!'
    line = Line(text, 14, '<')
    assert line.plain == 'hi there, Red!'
    assert line.display == text
    assert line.last_seq == '{t.normal}'

