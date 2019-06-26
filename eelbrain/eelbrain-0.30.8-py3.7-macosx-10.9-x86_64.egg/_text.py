"""Text generation helpers"""


def enumeration(items, link='and'):
    "['a', 'b', 'c'] -> 'a, b and c'"
    items = tuple(map(str, items))
    if len(items) >= 2:
        return (' %s ' % link).join((', '.join(items[:-1]), items[-1]))
    elif len(items) == 1:
        return items[0]
    else:
        raise ValueError("items=%s" % repr(items))


def ms(t_s):
    "Convert time in seconds to rounded milliseconds"
    return int(round(t_s * 1000))


def ms_window(t0, t1):
    return f"{ms(t0)} - {ms(t1)} ms"


def named_list(items, name='item'):
    "named_list([1, 2, 3], 'number') -> 'numbers (1, 2, 3)"
    if len(items) == 1:
        return "%s (%r)" % (name, items[0])
    else:
        if name.endswith('y'):
            name = name[:-1] + 'ie'
        return "%ss (%s)" % (name, ', '.join(map(repr, items)))


def n_of(n, of, plural_for_0=False):
    "n_of(3, 'epoch') -> '3 epochs'"
    if n == 0:
        return "no " + plural(of, not plural_for_0)
    return str(n) + ' ' + plural(of, n)


PLURALS = {
    'is': 'are',
}


def plural(singular, n):
    "plural('house', 2) -> 'houses'"
    if n == 1:
        return singular
    elif singular in PLURALS:
        return PLURALS[singular]
    elif singular.endswith('y'):
        return singular[:-1] + 'ies'
    else:
        return singular + 's'
