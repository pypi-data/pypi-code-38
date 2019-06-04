from inspect import signature


def getArgName(fn, idx=0):
    return list(signature(fn).parameters)[idx]
