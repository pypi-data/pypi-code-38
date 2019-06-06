import enum


class ErrorLevel(enum.Enum):
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


class Error:
    def __init__(self, message, level):
        self.message = message
        self.level = level

    def __str__(self):
        return self.message
