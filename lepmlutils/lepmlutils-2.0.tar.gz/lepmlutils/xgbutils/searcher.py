from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Dict

class Searcher(metaclass=ABCMeta):
    @abstractmethod
    def __iter__(self) -> "Searcher":
        pass

    @abstractmethod
    def __next__(self) -> Dict:
        pass