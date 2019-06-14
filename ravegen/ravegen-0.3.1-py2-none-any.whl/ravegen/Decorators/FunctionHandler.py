from Handler import *
import functools
import functionManager
import sadDec

class RaveFunction(Handler):
    def __init__(self, func, funcName = None, *arg, **karg):
        functools.update_wrapper(self, func)
        super(RaveFunction, self).__init__(func, sadDec._HANDLER_TYPE_FUNCTION_, funcName, *arg, **karg)
        functionManager.functionManager.addFunction(self)
