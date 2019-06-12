from abc import ABC, abstractmethod


class AbstractReaderWriter(ABC):

    @abstractmethod
    def read(self, addr: str) -> object:
        """This method provides a response to a read request, based on last load"""
        pass

    @abstractmethod
    def read_immediate(self, addr: str) -> object:
        """This method must provide an immediate response to a read request"""
        pass

    @abstractmethod
    def write(self, addr: str, value: object):
        """This method captures the need to write a value, but isn't necessarily immediate"""
        pass

    @abstractmethod
    def write_immediate(self, addr: str, value: object):
        """This method should force an immediate write"""
        pass

