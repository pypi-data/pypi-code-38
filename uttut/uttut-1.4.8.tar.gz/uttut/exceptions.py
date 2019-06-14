class UttutBaseException(Exception):
    pass


class EntityPositionError(UttutBaseException):
    pass


class EntityOverlapping(UttutBaseException):
    pass


class DifferentUtterance(UttutBaseException):
    pass
