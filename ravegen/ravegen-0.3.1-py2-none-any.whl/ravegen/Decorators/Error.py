from Handler import *
import functionManager
import functools
import sadDec

class Error(Handler):
    def __init__(self, func, funcName = None, *arg, **karg):
        functools.update_wrapper(self, func)
        super(Error, self).__init__(func, sadDec._HANDLER_TYPE_ERROR_, funcName=funcName, *arg, **karg)
        functionManager.functionManager.addError(self)
