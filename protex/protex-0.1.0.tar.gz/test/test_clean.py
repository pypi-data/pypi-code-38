from protex.lexer import Lexer
from protex.parser import Parser

from protex.commands import CommandDict, CommandPrototype, PrintOnePrototype

from protex.text_pos import TextPos

# test data

t0 = 'Hop'
r0 = 'Hop'

t1 = '''\
Hop \\title{Un titre}

Des histoires de \\phi.
Pouet.'''

r1 = '''\
Hop Un titre

Des histoires de phi. Pouet.'''

commands = CommandDict({
    'title': PrintOnePrototype('title'),
    'phi': CommandPrototype('phi', 0, 'phi'),
}, default_proto=lambda name: None)


def test_clean_1():
    lx = Lexer.from_source(t1)
    psr = Parser(lx, commands)
    root = psr.parse()
    assert root.render() == r1


def test_pos_map():
    lx = Lexer.from_source(t1)
    psr = Parser(lx, commands)
    root = psr.parse()
    root.render()
    pmap = root.dump_pos_map()

    tp1 = TextPos.from_source('')
    tp2 = TextPos.from_source(r0)

    _, st, en = pmap.dest_to_src_range(tp1, tp2)
    print(repr(st), repr(en))
    assert r0[tp1.offset:tp2.offset] == t0[st.offset:en.offset]


def test_pos_map_rev():
    lx = Lexer.from_source(t1)
    psr = Parser(lx, commands)
    root = psr.parse()
    root.render()
    pmap = root.dump_pos_map()

    tp1 = TextPos.from_source('')
    tp2 = TextPos.from_source(t0)

    st, en = pmap.src_to_dest_range(tp1, tp2)
    print(repr(st), repr(en))
    assert t0[tp1.offset:tp2.offset] == r0[st.offset:en.offset]


def test_pos_map2():
    lx = Lexer.from_source(t1)
    psr = Parser(lx, commands)
    root = psr.parse()
    root.render()
    pmap = root.dump_pos_map()

    tp1 = TextPos.from_source(r1[:7])
    tp2 = TextPos.from_source(r1[:12])

    _, st, en = pmap.dest_to_src_range(tp1, tp2)
    print(repr(st), repr(en))
    assert r1[tp1.offset:tp2.offset] == t1[st.offset:en.offset]


def test_pos_map3():
    lx = Lexer.from_source(t1)
    psr = Parser(lx, commands)
    root = psr.parse()
    root.render()
    pmap = root.dump_pos_map()

    tp1 = TextPos.from_source(r1[:18])
    tp2 = TextPos.from_source(r1[:27])

    _, st, en = pmap.dest_to_src_range(tp1, tp2)
    print(repr(st), repr(en))
    assert r1[tp1.offset:tp2.offset] == t1[st.offset:en.offset]


def test_pos_map_rev2():
    lx = Lexer.from_source(t1)
    psr = Parser(lx, commands)
    root = psr.parse()
    root.render()
    pmap = root.dump_pos_map()

    tp1 = TextPos.from_source(t1[:11])
    tp2 = TextPos.from_source(t1[:19])

    st, en = pmap.src_to_dest_range(tp1, tp2)
    print(repr(st), repr(en))
    assert t1[tp1.offset:tp2.offset] == r1[st.offset:en.offset]


def test_pos_map_rev3():
    lx = Lexer.from_source(t1)
    psr = Parser(lx, commands)
    root = psr.parse()
    root.render()
    pmap = root.dump_pos_map()

    tp1 = TextPos.from_source(t1[:26])
    tp2 = TextPos.from_source(t1[:35])

    st, en = pmap.src_to_dest_range(tp1, tp2)
    print(repr(st), repr(en))
    assert t1[tp1.offset:tp2.offset] == r1[st.offset:en.offset]
