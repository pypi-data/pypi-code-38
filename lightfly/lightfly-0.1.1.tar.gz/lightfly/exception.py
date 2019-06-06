class AuthException(Exception):

    def __init__(self, *args):
        self.args = args


class BadRequestException(Exception):
    def __init__(self, *args):
        self.args = args
