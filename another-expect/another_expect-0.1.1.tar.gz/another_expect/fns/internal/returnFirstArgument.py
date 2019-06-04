from .iif import iif


def returnFirstArgument(*args, **kwargs):
    return iif(len(args), args[0], None)
