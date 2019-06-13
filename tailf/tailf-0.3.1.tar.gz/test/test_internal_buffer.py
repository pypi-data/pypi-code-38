import io

from tailf.base import InternalBuffer


def test_basic():
    buf = InternalBuffer(100)
    buf.readfrom(io.BytesIO(b"alpha"))
    assert len(buf) == 5, "5 chars in buffer"
    assert buf.get() == b"alpha", "alpha got"
    assert len(buf) == 5, "5 chars in buffer"
    assert buf.pop() == b"alpha", "alpha popped"
    assert len(buf) == 0, "0 chars in buffer"


def test_cut():
    buf = InternalBuffer(100)
    buf.readfrom(io.BytesIO(b"alphabetagamma"))
    assert buf.pop(5) == b"alpha", "alpha popped"
    assert buf.pop(4) == b"beta", "beta popped"
    assert buf.pop() == b"gamma", "gamma popped"


def test_overcut():
    buf = InternalBuffer(100)
    buf.readfrom(io.BytesIO(b"alpha"))
    assert buf.pop(10) == b"alpha"


def test_find_shifted():
    buf = InternalBuffer(100)
    buf.readfrom(io.BytesIO(b"_" * 10 + b"abc"))
    buf.pop(10)
    assert buf.find(b"a") == 0
    assert buf.find(b"b") == 1
    assert buf.find(b"c") == 2
    assert buf.find(b"d") == -1

    assert buf.find(b"a", 1) == -1
    assert buf.find(b"b", 1) == 1

    assert buf.find(b"a", 0, 1) == 0
    assert buf.find(b"b", 0, 1) == -1
