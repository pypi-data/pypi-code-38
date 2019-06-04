from inspect import signature
from ..internal.raise_ import raise_
from ..._vendor import wrapt


def argIsType(aType):
    @wrapt.decorator
    def wrapper(fn, _instance, args, kwargs):
        typePassed = type(args[0])
        if typePassed is not str:
            argName = list(signature(fn).parameters)[0]
            fnName = fn.__name__
            typeName = aType.__name__
            raise_(
                ValueError,
                f"""\
                {fnName} requires {argName} to have the type {typeName}
                type passed: {typePassed.__name__}
                """,
            )

        return fn(*args, **kwargs)

    return wrapper
