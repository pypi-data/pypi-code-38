class IAMException(Exception):
    def __init__(self, code = 500, message = "", *arg):
        self.args = arg
        self.message = message
        self.code = code
        if arg:
            Exception.__init__(self, code, message, arg)
        else:
            Exception.__init__(self, code, message)