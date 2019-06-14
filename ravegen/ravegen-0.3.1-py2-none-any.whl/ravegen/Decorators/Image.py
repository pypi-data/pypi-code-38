from MessageHandler import *
import functools
import sadDec

class Image(MessageHandler):
    def __init__(self, func, *arg, **karg):
        functools.update_wrapper(self, func)
        super(Image, self).__init__(func, sadDec._MESSAGE_HANDLER_IMAGE_, *arg, **karg)
