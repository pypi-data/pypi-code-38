import abc

from ofx2xlsmbr.model.BankStatement import BankStatement

class IReaderController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self, factory, inputFilename='', file=None) -> BankStatement:
        pass