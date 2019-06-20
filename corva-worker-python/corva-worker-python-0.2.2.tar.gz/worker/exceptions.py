class CorvaException(Exception):
    pass


class Misconfigured(Exception):
    pass


class APIError(CorvaException):
    pass


class AssetNotFound(CorvaException):
    pass


class Forbidden(CorvaException):
    pass
