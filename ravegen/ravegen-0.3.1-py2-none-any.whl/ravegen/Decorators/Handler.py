class Handler(object):
    def __init__(self, func, handlerType, funcName = None, description = None):
        if funcName is None:
            funcName = func.__name__
        self.funcName = funcName
        self.func = func
        self.handlerType = handlerType
        self.description = description

    def __call__(self, *arg, **karg):
        return self.func(*arg, **karg)
