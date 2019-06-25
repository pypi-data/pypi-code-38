import abc

from ofx2xlsmbr.model.BankStatement import BankStatement

class IWriterBankStatement(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write(self, bankStatement: BankStatement, factory, output):
        pass