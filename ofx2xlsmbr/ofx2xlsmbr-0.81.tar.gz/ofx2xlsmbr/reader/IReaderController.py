import abc
from typing import List

from ofx2xlsmbr.model.BankStatement import BankStatement

class IReaderController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self, factory, files=[]) -> List[BankStatement]:
        pass