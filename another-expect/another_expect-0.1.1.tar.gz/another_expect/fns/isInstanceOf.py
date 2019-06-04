from .decorators.argIsClass import argIsClass


@argIsClass
def isInstanceOf(aType):
    def isInstanceOf_inner(something):
        return isinstance(something, aType)

    return isInstanceOf_inner
