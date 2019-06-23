from protex.lexer import Lexer
from protex.text_pos import TextDeltaPos, TextPos, ContiguousPosMap, RootPosMap

# test data
t1 = '''\
Un texte

Avec des lignes vides
et des \\commandes{avec}{des argument}.
Et qui finit pas par un newline.
Pouet.'''

t2 = '''Un bout de texte sans newline.'''


def test_text_delta_pos():
    tp = TextDeltaPos.from_source(t1)
    assert tp.offset == len(t1)
    assert tp.line == 5
    assert tp.col == 6

    tp = TextDeltaPos.from_source(t2)
    assert tp.offset == len(t2)
    assert tp.line == 0
    assert tp.col == len(t2)


def test_text_pos_from_source():
    tp = TextPos.from_source(t1)
    assert tp.offset == len(t1)
    assert tp.line == 6
    assert tp.col == 6

    tp = TextPos.from_source(t2)
    assert tp.offset == len(t2)
    assert tp.line == 1
    assert tp.col == len(t2)


def test_text_pos_from_lexer():
    lx = Lexer.from_source(t1)
    list(lx.tokens())
    assert lx.pos.offset == len(t1)
    assert lx.pos.line == 6
    assert lx.pos.col == 7


def test_text_pos_additive():
    tp1 = TextPos.from_source(t1 + ' ' + t2)

    tp2 = TextPos.from_source(t1 + ' ') + TextDeltaPos.from_source(t2)
    assert tp1 == tp2

    tp2 = TextPos.from_source(t1) + TextDeltaPos.from_source(' ' + t2)
    assert tp1 == tp2

    tp1 = TextPos.from_source(t1 + '\n' + t2)
    tp2 = TextPos.from_source(t1 + '\n') + TextDeltaPos.from_source(t2)
    assert tp1 == tp2

    tp2 = TextPos.from_source(t1) + TextDeltaPos.from_source('\n' + t2)
    assert tp1 == tp2


def test_text_pos_sub():
    tp1 = TextPos.from_source(t1 + ' ' + t2) - TextPos.from_source(t1 + ' ')
    tp2 = TextDeltaPos.from_source(t2)
    assert tp1 == tp2

    tp1 = TextPos.from_source(t1 + ' ' + t2) - TextPos.from_source(t1)
    tp2 = TextDeltaPos.from_source(' ' + t2)
    assert tp1 == tp2

    tp1 = TextPos.from_source(t1 + '\n' + t2) - TextPos.from_source(t1 + '\n')
    tp2 = TextDeltaPos.from_source(t2)
    assert tp1 == tp2

    tp1 = TextPos.from_source(t1 + '\n' + t2) - TextPos.from_source(t1)
    tp2 = TextDeltaPos.from_source('\n' + t2)
    assert tp1 == tp2


def test_convert_pos():
    text = 'un petit bout de texte\navec un saut de ligne'
    src_start = TextPos(50, 8, 10)
    src_end = src_start + TextDeltaPos.from_source(text)

    dest_start = TextPos(10, 5, 2)
    dest_end = dest_start + TextDeltaPos.from_source(text)

    map = RootPosMap('anonym', [ContiguousPosMap(src_start, src_end, dest_start, dest_end)])

    pos = src_start

    while pos != src_end:
        interm = map.src_to_dest(pos)
        print(pos, '->', interm)
        assert pos == map.dest_to_src(interm)[1]
        if text[pos.offset - 50] == '\n':
            pos = pos.new_line()
        else:
            pos += 1

    pos = dest_start

    while pos != dest_end:
        interm = map.dest_to_src(pos)[1]
        print(pos, '->', interm)
        assert pos == map.src_to_dest(interm)
        if text[pos.offset - 10] == '\n':
            pos = pos.new_line()
        else:
            pos += 1


def test_order():
    tp1 = TextPos(50, 30, 45)
    tp2 = TextPos(90, 10, 48)
    tp3 = TextPos(-1, 35, 45)
    tp4 = TextPos(-1, 8, 48)

    assert tp1 < tp2
    assert tp1 <= tp2
    assert tp2 > tp1
    assert tp2 >= tp1

    assert not tp1 > tp2
    assert not tp1 >= tp2
    assert not tp2 < tp1
    assert not tp2 <= tp1

    assert tp3 < tp4
    assert tp3 < tp2
    assert tp4 < tp2
    assert tp3 > tp1
    assert tp4 > tp1
