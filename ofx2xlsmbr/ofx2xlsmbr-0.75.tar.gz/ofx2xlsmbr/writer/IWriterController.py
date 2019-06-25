import abc

from ofx2xlsmbr.model.BankStatement import BankStatement

class IWriterController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write(self, data: BankStatement, factory, outputFilename=''):
        pass