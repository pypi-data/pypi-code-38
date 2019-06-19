from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from peek_plugin_docdb._private.PluginNames import docDbTuplePrefix
from peek_plugin_docdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_docdb._private.storage.DocDbModelSet import DocDbModelSet
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class DocDbDocumentTypeTuple(Tuple, DeclarativeBase):
    __tupleType__ = docDbTuplePrefix + 'DocDbDocumentTypeTuple'
    __tablename__ = 'DocDbDocumentType'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this document
    modelSetId = Column(Integer,
                        ForeignKey('DocDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(DocDbModelSet)

    name = Column(String, nullable=False)
    title = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_DocType_model_name", modelSetId, name, unique=True),
        Index("idx_DocType_model_title", modelSetId, title, unique=True),
    )
