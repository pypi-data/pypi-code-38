from ..._vendor.ordered_set import OrderedSet
from ..._vendor import wrapt

from ..internal.discardWhen import discardWhen
from ..internal.get import get
from ..internal.getArgName import getArgName
from ..internal.isLaden import isLaden
from ..internal.isType import isType
from ..internal.joinWith import joinWith
from ..internal.map_ import map_
from ..internal.passThrough import passThrough
from ..internal.raise_ import raise_
from ..internal.sort import sort
from ..internal.toType import toType


def argIsListOfType(aType):
    @wrapt.decorator
    def wrapper(fn, _instance, args, kwargs):
        typePassed = type(args[0])

        fnName = fn.__name__
        typeName = aType.__name__

        if typePassed is not list:
            argName = getArgName(fn)
            raise_(
                ValueError,
                f"""\
                {fnName} requires {argName} to have the type list
                type passed: {typePassed.__name__}
                """,
            )

        invalidTypes = discardWhen(isType(aType))(args[0])
        if isLaden(invalidTypes):
            argName = getArgName(fn)
            invalidTypeNames = passThrough(
                invalidTypes,
                [
                    map_(toType),
                    OrderedSet,
                    list,
                    map_(get("__name__")),
                    sort,
                    joinWith(", "),
                ],
            )
            raise_(
                ValueError,
                f"""\
                {fnName} requires {argName} to be a list of {typeName}
                invalid types passed: {invalidTypeNames}
                """,
            )

        return fn(*args, **kwargs)

    return wrapper
