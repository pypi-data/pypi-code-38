from categories.utils import flip, id_, compose, cp


def test_id_():
    assert id_('a') == 'a'
    assert id_(42) == 42
    assert id_([1, 2, 3]) == [1, 2, 3]
    assert id_(id_)(12) == 12


def test_flip():
    def div(a, b):
        return a / b

    assert div(9, 3) == 9 / 3
    assert flip(div)(9, 3) == 3 / 9


def test_compose():
    f = lambda x: x * 3
    g = lambda x: x + 3
    h = lambda x: x / 2

    for i in [7, 8, 42, 1234]:
        assert compose(f, g, h)(i) == f(g(h(i)))
        assert compose(h, g, f)(i) == h(g(f(i)))


def test_compose_infix():
    f = lambda x: x * 3
    g = lambda x: x + 3
    h = lambda x: x / 2

    for i in [7, 8, 42, 1234]:
        assert (f |compose| g |compose| h)(i) == f(g(h(i)))
        assert (h |compose| g |compose| f)(i) == h(g(f(i)))
        assert (f |cp| g |cp| h)(i) == f(g(h(i)))
        assert (h |cp| g |cp| f)(i) == h(g(f(i)))
