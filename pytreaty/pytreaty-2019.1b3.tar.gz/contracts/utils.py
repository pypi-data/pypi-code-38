# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import traceback
import warnings

import six


__all__ = [
    'indent',
    'deprecated',
    'raise_type_mismatch',
    'raise_wrapped',
    'raise_desc',
    'check_isinstance',
    'ignore_typeerror'
]


def indent(s, prefix, first=None):
    if not isinstance(s, six.string_types):
        s = u'{}'.format(s)

    assert isinstance(prefix, six.string_types)
    try:
        lines = s.split('\n')
    except UnicodeDecodeError:
        print(type(s))  # XXX
        print(s)  # XXX
        lines = [s]
    if not lines:
        return u''

    if first is None:
        first = prefix

    m = max(len(prefix), len(first))

    prefix = ' ' * (m - len(prefix)) + prefix
    first = ' ' * (m - len(first)) + first

    # different first prefix
    res = [u'%s%s' % (prefix, line.rstrip()) for line in lines]
    res[0] = u'%s%s' % (first, lines[0].rstrip())
    return '\n'.join(res)


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


def check_isinstance(ob, expected, **kwargs):
    if not isinstance(ob, expected):
        kwargs['object'] = ob
        raise_type_mismatch(ob, expected, **kwargs)


def raise_type_mismatch(ob, expected, **kwargs):
    """ Raises an exception concerning ob having the wrong type. """
    e = 'Object not of expected type:'
    e += '\n  expected: {}'.format(expected)
    e += '\n  obtained: {}'.format(type(ob))
    e += '\n' + indent(format_obs(kwargs), ' ')
    raise ValueError(e)


def format_dict_long(d, informal=False):
    """
        k: value
           kooked
        k: value
    """
    if not d:
        return '{}'

    maxlen = max([len(n) for n in d]) + 2

    def pad(pre):
        return ' ' * (maxlen - len(pre)) + pre

    res = ""
    order = sorted(d)
    for i, name in enumerate(order):
        value = d[name]
        prefix = pad('%s: ' % name)
        if i > 0:
            res += '\n'

        s = _get_str(value, informal)

        if len(s) > 512:
            s = s[:512] + ' [truncated]'
        res += indent(s, ' ', first=prefix)
    return res


def _get_str(x, informal):
    from contracts.interface import describe_value_multiline
    if informal:
        s = x.__str__()
    else:
        s = describe_value_multiline(x)
    return s


def format_list_long(l, informal=False):
    """
        - My 
          first
        - Second
    """
    res = ""
    for i, value in enumerate(l):
        prefix = '- '
        if i > 0:
            res += '\n'
        s = _get_str(value, informal)
        res += indent(s, ' ', first=prefix)
    return res


def format_obs(d, informal=False):
    """ Shows objects values and typed for the given dictionary """
    if not d:
        return d.__str__()

    maxlen = 0
    for name in d:
        maxlen = max(len(name), maxlen)

    def pad(pre):
        return ' ' * (maxlen - len(pre)) + pre

    res = ''

    S = sorted(d)
    for i, name in enumerate(S):
        value = d[name]
        prefix = pad('%s: ' % name)
        if i > 0:
            res += '\n'

        s = _get_str(value, informal)

        res += indent(s, ' ', first=prefix)

    return res


def raise_wrapped(etype, e, msg, compact=False, **kwargs):
    """ Raises an exception of type etype by wrapping
        another exception "e" with its backtrace and adding
        the objects in kwargs as formatted by format_obs.
        
        if compact = False, write the whole traceback, otherwise just str(e).
    
        exc = output of sys.exc_info()
    """

    if six.PY3:
        from six import raise_from
        msg += '\n' + indent(e, '| ')
        e2 = etype(_format_exc(msg, **kwargs))
        raise_from(e2, e)
    else:
        e2 = raise_wrapped_make(etype, e, msg, compact=compact, **kwargs)
        raise e2


def raise_wrapped_make(etype, e, msg, compact=False, **kwargs):
    """ Constructs the exception to be thrown by raise_wrapped() """
    assert isinstance(e, BaseException), type(e)
    check_isinstance(msg, six.text_type)
    s = msg
    if kwargs:
        s += '\n' + format_obs(kwargs)

    if compact:
        es = e.__str__()
    else:
        es = traceback.format_exc()  # only PY2

    s += '\n' + indent(es.strip(), '| ')

    return etype(s)


def _format_exc(msg, **kwargs):
    check_isinstance(msg, six.text_type)
    s = msg
    if kwargs:
        s += '\n' + format_obs(kwargs)
    return s


def raise_desc(etype, msg, args_first=False, **kwargs):
    """
    
        Example:
            raise_desc(ValueError, "I don't know", a=a, b=b)
    """
    assert isinstance(msg, six.string_types), type(msg)
    s1 = msg
    if kwargs:
        s2 = format_obs(kwargs)
    else:
        s2 = ""

    if args_first:
        s = s2 + "\n" + s1
    else:
        s = s1 + "\n" + s2

    raise etype(s)


def ignore_typeerror(f):
    """ Recasts TypeError as Exception; otherwise pyparsing gets confused. """

    def f2(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except TypeError as e:
            raise Exception(traceback.format_exc())

    return f2
