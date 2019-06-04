from inspect import isclass


def isType(aType):
    if not isclass(aType):
        raise ValueError("isType requires argument 'aType' to pass isclass")

    def isType_inner(something):
        return type(something) is aType

    return isType_inner
