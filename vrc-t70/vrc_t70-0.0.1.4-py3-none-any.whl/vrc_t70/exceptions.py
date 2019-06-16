class BadCrc(Exception):
    pass


class WrongEventId(Exception):
    pass


class WrongControllerAddress(Exception):
    pass


class NoAnswerFromController(Exception):
    pass


class WrongBytesCount(Exception):
    pass
