import abc

from ofx2xlsmbr.writer.IWriterBankStatement import IWriterBankStatement
from ofx2xlsmbr.writer.IWriterCashFlow import IWriterCashFlow

class WriterAbstractFactory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def createWriterBankStatement(self) -> IWriterBankStatement:
        pass

    @abc.abstractmethod
    def createWriterCashFlow(self) -> IWriterCashFlow:
        pass