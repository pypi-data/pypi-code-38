
class FixtureDoesNotExistError(BaseException):
    MESSAGE_FORMAT = "Cannot find a fixture json file in \"%s\" with name=\"%s\"."

    def __init__(self, fix_dir, fix_name):
        BaseException.__init__(self, self.MESSAGE_FORMAT % (fix_dir, fix_name))


class FieldNotInFixtureError(BaseException):
    MESSAGE_FORMAT = "Cannot find a field \"%s\".\"%s\" in fixture loaded \"%s\"."
    MESSAGE_FORMAT2 = "Cannot find a field \"%s\".\"%s\" when a fixture was not loaded."

    def __init__(self, model, field, fixture=None):
        if fixture is None:
            message = self.MESSAGE_FORMAT2 % (model, field)
        else:
            message = self.MESSAGE_FORMAT % (model, field, fixture)
        BaseException.__init__(self, message)


class ModelNotInFixtureError(BaseException):
    MESSAGE_FORMAT = "Cannot find a model \"%s\" in fixture loaded \"%s\"."
    MESSAGE_FORMAT2 = "Cannot find a model \"%s\" when a fixture was not loaded."

    def __init__(self, model, fixture=None):
        if fixture is None:
            message = self.MESSAGE_FORMAT2 % model
        else:
            message = self.MESSAGE_FORMAT % (model, fixture)
        BaseException.__init__(self, message)