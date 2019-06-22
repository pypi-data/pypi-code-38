from mint import exceptions


def get(func):
    def wrapper(self):
        if self.request.method != "GET":
            raise exceptions.HttpNotAllowed("This action needs to be a HTTP GET.")
        return func(self)
    return wrapper


def post(func):
    def wrapper(self):
        if self.request.method != "POST":
            raise exceptions.HttpNotAllowed("This action needs to be a HTTP POST.")
        return func(self)
    return wrapper


def put(func):
    def wrapper(self):
        if self.request.method != "PUT":
            raise exceptions.HttpNotAllowed("This action needs to be a HTTP PUT.")
        return func(self)
    return wrapper


def delete(func):
    def wrapper(self):
        if self.request.method != "DELETE":
            raise exceptions.HttpNotAllowed("This action needs to be a HTTP DELETE.")
        return func(self)
    return wrapper


def requires_id(func):
    def wrapper(self):
        if hasattr(self, 'id') and self.id is None:
            raise exceptions.ParameterError("This action requires an ID")
        return func(self)
    return wrapper


def requires(**kwargs):
    def decorator(function):
        def wrapper(self):
            for arg, typex in kwargs.items():
                if arg not in self.args.keys():
                    raise exceptions.ParameterError("This action requires argument '%s' but it was not passed." % arg)
                try:
                    self.args[arg] = typex(self.args[arg])
                except ValueError:
                    raise exceptions.ParameterError("Could not convert argument '%s' to a '%s'" %
                                                    (arg, typex.__name__))
            return function(self)
        return wrapper
    return decorator