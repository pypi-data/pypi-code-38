import abc

from ofx2xlsmbr.model.BankStatement import BankStatement

# Data e um array de bankstatements
class IWriterController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write(self, data, factory, outputFilename=''):
        pass