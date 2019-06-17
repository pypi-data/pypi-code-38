from functools import reduce
from operator import and_


def maybe_type(obj, class_or_tuple):
    """
    A type monid. Return transfered type of obj or None if type cannot assign to given obj.
    """
    if obj is None:
        return None
    if isinstance(obj, str) and class_or_tuple is iter:
        """Trick treat str as non-iterable."""
        return None

    try:
        transfered_obj = None
        transfered_obj = class_or_tuple(obj)
    except:
        pass

    if transfered_obj is not None:
        return transfered_obj
    else:
        try:
            return class_or_tuple(obj)
        except:
            return


def flat_to_list(*args):
    """
    List utility, turn a pile of shit into a flat list.

    Usage:
    >>> flat_to_list("123",[1,[2,3]],A_FILE,File(A_FILE))

    >>> ['123',
    >>>  1,
    >>>  2,
    >>>  3,
    >>>  '/mnt/gluster/resources/phantom/derenzo/derenzo.1/phantomD.bin',
    >>>  File("/mnt/gluster/resources/phantom/derenzo/derenzo.1/phantomD.bin")]
    """
    buf = []

    def flat_list(arg):
        def _flat_list(arg):
            def _on_iterable(arg):
                _flat_list(arg)

            def _on_single(arg):
                buf.append(arg)

            if maybe_type(arg, iter) is None:
                _on_single(arg)
            else:
                for i in arg:
                    _on_iterable(i)
            return buf

        return _flat_list(arg)

    for arg in args:
        flat_list(arg)

    return buf


def is_all_true(l: iter):
    return reduce(and_, l)


class TypeCheck:
    pass


def set(value):
    pass
