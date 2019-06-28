
__all__ = ['CommandError', 'CommandInterface', 'ACK', 'NACK']


class CommandError(Exception):
    pass


class CommandInterface(object):
    """Commands can be any object but they must be known to the listener process."""


class ACK(CommandInterface):
    def __init__(self, cmd=''):
        if not isinstance(cmd, str):
            cmd = cmd.__class__.__name__
        self.cmd = cmd


class NACK(CommandInterface):
    def __init__(self, error=None):
        self.error = error
