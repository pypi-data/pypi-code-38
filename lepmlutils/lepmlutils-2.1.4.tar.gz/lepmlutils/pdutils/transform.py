from __future__ import annotations
from abc import ABCMeta, abstractmethod
from .taggeddataframe import TaggedDataFrame


# Transform represents an operation that can be performed on and
# alters a LepDataFrame in place.
class Transform():
    # operate performs a specific operation on the given dataframe
    # changing its state in some way.
    @abstractmethod
    def operate(self, df: TaggedDataFrame) -> None:
        pass

    # re_operate is an alias for operate except in cases where re-
    # applying operate might cause the given dataframe to have a 
    # different number of columns than the first dataframe ended 
    # up with at the end of operate.
    @abstractmethod
    def re_operate(self, df: TaggedDataFrame) -> None:
        pass