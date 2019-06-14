from MessageHandler import *
import functools
import sadDec

class _Text(MessageHandler):
    def __init__(self, func, *arg, **karg):
        functools.update_wrapper(self, func)
        super(_Text, self).__init__(func, sadDec._MESSAGE_HANDLER_TEXT_, *arg, **karg)


def Text(func = None, description=""):
    if func != None:
        return _Text(func)
    def wrapper(func):
        return _Text(func, description=description)
    return wrapper
