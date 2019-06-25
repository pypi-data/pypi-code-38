import abc

from ofx2xlsmbr.model.CashFlow import CashFlow

class IWriterCashFlow(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write(self, cashFlow: CashFlow, factory, output):
        pass