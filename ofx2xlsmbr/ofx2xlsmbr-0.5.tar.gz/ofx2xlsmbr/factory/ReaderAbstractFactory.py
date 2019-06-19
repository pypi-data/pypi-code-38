import abc

from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.reader.IReaderCashFlow import IReaderCashFlow

class ReaderAbstractFactory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def createReaderBankStatement(self) -> IReaderBankStatement:
        pass

    @abc.abstractmethod
    def createReaderCashFlow(self) -> IReaderCashFlow:
        pass