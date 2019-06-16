from abc import ABC, abstractmethod


class AbstractReaderWriter(ABC):

    @abstractmethod
    def read(self, addr: str) -> object:
        """This method provides a response to a read request, based on last load"""
        pass

    @abstractmethod
    def write(self, addr: str, value: object):
        """This method captures the need to write a value, but isn't necessarily immediate"""
        pass



