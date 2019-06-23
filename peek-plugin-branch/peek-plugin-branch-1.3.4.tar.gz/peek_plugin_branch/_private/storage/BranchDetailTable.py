from sqlalchemy import Column, DateTime, Integer, String

from peek_plugin_branch._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_branch.tuples.BranchDetailTuple import BranchDetailTuple


class BranchDetailTable(DeclarativeBase):
    __tablename__ = 'BranchDetail'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetKey = Column(String, nullable=False)

    key = Column(String, nullable=False)

    name = Column(String, nullable=False)

    comment = Column(String)

    userName = Column(String, nullable=False)

    updatedDate = Column(DateTime(timezone=True), nullable=False)

    createdDate = Column(DateTime(timezone=True), nullable=False)

    def toTuple(self) -> BranchDetailTuple:
        branch = BranchDetailTuple()
        for fieldName in BranchDetailTuple.tupleFieldNames():
            setattr(branch, fieldName, getattr(self, fieldName))
        return branch

    @staticmethod
    def fromTuple(inTuple: BranchDetailTuple) -> 'BranchDetailTable':
        branch = BranchDetailTable()
        for fieldName in BranchDetailTuple.tupleFieldNames():
            setattr(branch, fieldName, getattr(inTuple, fieldName))
        return branch
