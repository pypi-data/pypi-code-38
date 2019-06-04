""" Core exceptions raised by PyRaftLog. """


class PyRaftLogException(Exception):
    pass


class ReducedException(PyRaftLogException):
    pass
