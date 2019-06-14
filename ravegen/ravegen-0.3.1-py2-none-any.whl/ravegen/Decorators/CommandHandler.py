from Handler import *
import functools
import functionManager
import sadDec

class _Command(Handler):
    def __init__(self, func, funcName = None, passArgs = False, *arg, **karg):
        functools.update_wrapper(self, func)
        super(_Command, self).__init__(func, sadDec._HANDLER_TYPE_COMMAND_, funcName=funcName, *arg, **karg)
        self.passArgs = passArgs
        functionManager.functionManager.addCommand(self)


def Command(func = None, passArgs = False, description=None):
    if func != None:
        return _Command(func)
    def wrapper(func):
        return _Command(func, passArgs=passArgs, description=description)
    return wrapper
