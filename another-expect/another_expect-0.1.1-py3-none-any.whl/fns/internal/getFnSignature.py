from inspect import signature
from .raise_ import raise_


def getFnSignature(fn, callerName):
    try:
        return signature(fn)
    except Exception as e:
        raise_(
            ValueError,
            f"""\
            '{callerName}' is unable to get the signature of the passed callable
            callable passed: {fn.__name__}

            one reason this could occur is the callable is written in c (e.g.
            the builtin 'str' callable).
            """,
            fromException=e,
        )
