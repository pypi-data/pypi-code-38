class TrainException(Exception):
    def __init__(self, code = 0, message = "", *arg):
        self.args = arg
        self.message = message
        self.code = code
        if arg:
            Exception.__init__(self, code, message, arg)
        else:
            Exception.__init__(self, code, message)
