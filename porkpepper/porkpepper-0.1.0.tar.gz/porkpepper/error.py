

class RedisProtocolFormatError(Exception):
    pass


class ExceptionWithReplyError(Exception):
    def __init__(self, reply="ERR", *args):
        super().__init__(*args)
        self.reply = reply


class NoPasswordError(ExceptionWithReplyError):
    pass


class ReducerTypeNotFound(Exception):
    pass


class StoreNotFound(Exception):
    pass


class NodeNotFound(Exception):
    pass


class ReducerNotFound(Exception):
    pass


class DatabaseNotFound(Exception):
    pass


class CommandNotFound(ExceptionWithReplyError):
    def __init__(self):
        super(CommandNotFound, self).__init__(reply="COMMAND NOT FOUND")


__all__ = [
    "RedisProtocolFormatError",
    "ExceptionWithReplyError",
    "NoPasswordError",
    "ReducerTypeNotFound",
    "StoreNotFound",
    "NodeNotFound",
    "ReducerNotFound",
    "DatabaseNotFound",
    "CommandNotFound",
]
