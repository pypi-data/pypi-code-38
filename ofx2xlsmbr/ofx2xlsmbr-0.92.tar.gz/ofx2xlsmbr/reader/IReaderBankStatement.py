import abc

from ofx2xlsmbr.model.BankStatement import BankStatement

class IReaderBankStatement(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self, factory, ofx) -> BankStatement:
        pass