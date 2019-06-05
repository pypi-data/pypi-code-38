
class WrongCredentials(ValueError):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


class NotAuthorized(ValueError):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


class NoSwaggerDef(ValueError):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}


class EndpointURLNotFound(ValueError):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}
