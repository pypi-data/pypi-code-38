from abc import ABCMeta, abstractmethod
from typing import List

class ParamRange(metaclass=ABCMeta):
    @abstractmethod
    def value(self, index: int) -> int:
        pass
