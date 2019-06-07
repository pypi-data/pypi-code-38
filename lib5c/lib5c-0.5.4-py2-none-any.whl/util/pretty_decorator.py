"""
Module providing the ``@pretty_decorator`` meta-decorator.
"""


def pretty_decorator(dec):
    """
    Decorator to turn any existing decorator into a "pretty" decorator.

    A "pretty" decorator retains the signature information of the original
    function, improving the readability of ``help(func)`` and auto-generated
    documentation.

    This functionality is completely cosmetic.

    Requires the optional dependency ``decorator`` - if importing this fails,
    the decorator will not be modified.

    Parameters
    ----------
    dec : function
        The decorator to prettify.

    Returns
    -------
    function
        The pretty decorator.

    Examples
    --------
    >>> from lib5c.util.pretty_decorator import pretty_decorator
    >>> @pretty_decorator
    ... def dec1(func):
    ...     def wrapped_func(*args, **kwargs):
    ...         print "you've been decorated"
    ...         return func(*args, **kwargs)
    ...     return wrapped_func
    >>> @dec1
    ... def my_func(a, b):
    ...    "Adds two numbers"
    ...    return a + b
    >>> my_func(1, 2)
    you've been decorated
    3
    >>> help(my_func)
    Help on function my_func in module lib5c.util.pretty_decorator:
    <BLANKLINE>
    my_func(a, b)
        Adds two numbers
    <BLANKLINE>
    """
    try:
        import decorator

        def new_dec(func):
            """
            Decorate a function by preserving the signature even if dec is not a
            signature-preserving decorator.
            """
            return decorator.FunctionMaker.create(
                func, 'return decfunc(%(signature)s)',
                dict(decfunc=dec(func)), __wrapped__=func)

        return new_dec
    except ImportError:
        return dec
