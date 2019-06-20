# -*- coding: utf-8 -*-
def str2bool(val):
    """
    Funkcja zamienia string na wartość boolową::

    'yes' -> true
    'no' -> false
    'test' -> false
    '1' -> true
    """
    if val:
        return unicode(val).lower() in ("yes", "true", "y", "t", "1")

    return False


def bool2int(val):
    """
    Funkcja zamienia wartość boolową 0 lub 1

    true -> 1
    false -> 0
    """

    return 1 if val else 0


def int2bool(val):
    """
    Funkcja zamienia int na bool

    0 -> false
    >=1 -> true
    """

    return False if int(val) == 0 else True

# @bz pomysl fajny, ale 1) daj to do db.py 2) unicode, a nie str, jesli elementem listy nie jest int/decimal/float i do tego "", zeby stringa owrapowac


def list2sqllist(list, string_wrap = True):
    if string_wrap:
        return u"(" + u",".join(['"' + unicode(x) + '"' for x in list]) + u")"
    else:
        return u"(" + u",".join([unicode(x) for x in list]) + u")"
