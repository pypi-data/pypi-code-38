from Handler import *
import functools
import functionManager
import sadDec

class CallBack(Handler):
    def __init__(self, func, funcName = None, *arg, **karg):
        functools.update_wrapper(self, func)
        super(CallBack, self).__init__(func, sadDec._HANDLER_TYPE_CALLBACK_, funcName, *arg, **karg)
        functionManager.functionManager.addCallBack(self)
