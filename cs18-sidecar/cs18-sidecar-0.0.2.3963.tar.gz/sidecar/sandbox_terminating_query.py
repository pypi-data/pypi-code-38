from abc import ABCMeta, abstractmethod


class ISandboxTerminatingQuery:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def is_terminating(self) -> bool:
        raise NotImplementedError


