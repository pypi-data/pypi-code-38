class TinyTaskError(ValueError):
    pass


class TaskNotDoneError(TinyTaskError):
    pass


class TaskClearedError(TinyTaskError):
    pass


class TaskStartedError(TinyTaskError):
    pass


class TaskResultsMissingError(TinyTaskError):
    pass


class TaskNotFoundError(TinyTaskError):
    pass
