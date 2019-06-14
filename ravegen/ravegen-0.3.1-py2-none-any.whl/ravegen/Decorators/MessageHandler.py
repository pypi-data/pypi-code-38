import functionManager
from Handler import *
import sadDec

class MessageHandler(Handler):
    def __init__(self, func, filter, funcName = None, *arg, **karg):
        super(MessageHandler, self).__init__(func, sadDec._HANDLER_TYPE_MESSAGE_, funcName, *arg, **karg)
        self.filter = filter
        functionManager.functionManager.addMessage(self)
