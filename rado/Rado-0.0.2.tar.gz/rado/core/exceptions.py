# encodeing: utf-8

""" failure type exceptions
    these exceptions will mark test as failure
"""


class MyBaseFailure(Exception):
    pass


class ValidationFailure(MyBaseFailure):
    pass


""" error type exceptions
    these exceptions will mark test as error
"""


class MyBaseError(Exception):
    pass


class FileFormatError(MyBaseError):
    pass


class ParamsError(MyBaseError):
    pass


class NotFoundError(MyBaseError):
    pass


class ExcelFileError(MyBaseError):
    pass


class FunctionNotFound(NotFoundError):
    pass


class VariableNotFound(NotFoundError):
    pass


class EnvNotFound(NotFoundError):
    pass


class ApiNotFound(NotFoundError):
    pass


class TestcaseNotFound(NotFoundError):
    pass
