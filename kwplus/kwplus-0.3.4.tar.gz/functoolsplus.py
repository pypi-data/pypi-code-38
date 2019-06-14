from functools import partial, reduce


def call(f, *a, **kw):
    return f(*a, **kw)


def compose(fs):
    """
    Composes functions together

    If the input is [f, g, h], the function returns r such that
    r(x) = f(g(h(x)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(acc), list(reversed(fs)))


def kwcompose(fs):
    """
    Composes keyword functions together

    If the input is [f, g, h], the function returns r such that
    r(**kw) = f(**g(**h(**kw)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(**acc), list(reversed(fs)))


def argcompose(fs):
    """
    Composes keyword functions together

    If the input is [f, g, h], the function returns r such that
    r(*a) = f(*g(*h(*a)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(*acc), list(reversed(fs)))


def headtail(xs):
    itxs = iter(xs)
    return next(itxs), itxs


def tail(xs):
    return headtail(xs)[1]


def head(xs):
    return headtail(xs)[0]


first = head

second = compose((head, tail))


def group_by(rows, key_fn, init_fn=list, group_init_fn=dict):
    grouped = group_init_fn()
    for row in rows:
        grouped.setdefault(key_fn(row), init_fn()).append(row)

    return grouped.items()
