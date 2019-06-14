class Error(Exception):
    pass


class GracefulExit(SystemExit):
    pass


class PrepareError(Error):
    pass


class TaskFormatError(Error):
    pass


class ValidationResponseError(Error):
    pass


class WidgetResponseError(Error):
    pass


class UnknownTaskError(Error):
    pass


class BadTaskParamsError(Error):
    pass


class PayErrorException(Error):
    pass
