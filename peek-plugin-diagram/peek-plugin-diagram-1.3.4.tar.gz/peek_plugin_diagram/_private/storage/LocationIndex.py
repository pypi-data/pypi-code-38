import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index

from peek_plugin_base.storage.TypeDecorators import PeekLargeBinary
from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase
from .Display import DispBase
from .ModelSet import ModelSet

logger = logging.getLogger(__name__)


@addTupleType
class LocationIndexCompilerQueue(Tuple, DeclarativeBase):
    __tablename__ = 'LocationIndexCompilerQueue'
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)

    indexBucket = Column(String(100), primary_key=True)
    modelSetId = Column(Integer,
                        ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        primary_key=True)

    __table_args__ = (
        Index("idx_LICompQueue_modelSetId_indexBucket", modelSetId, indexBucket,
              unique=False),
    )


@addTupleType
class LocationIndex(Tuple, DeclarativeBase):
    __tablename__ = 'LocationIndex'
    __tupleType__ = diagramTuplePrefix + __tablename__

    indexBucket = Column(String(100), primary_key=True)
    dispId = Column(Integer,
                    ForeignKey('DispBase.id', ondelete='CASCADE'),
                    primary_key=True)

    disp = relationship(DispBase)

    modelSetId = Column(Integer, ForeignKey('ModelSet.id'), nullable=False)
    modelSet = relationship(ModelSet)

    __table_args__ = (
        Index("idx_LocationIndex_indexBucket", indexBucket, unique=False),
        Index("idx_LocationIndex_dispId", dispId, unique=False),
        Index("idx_LocationIndex_modelSetId", modelSetId, unique=False),
    )


@addTupleType
class LocationIndexCompiled(Tuple, DeclarativeBase):
    __tablename__ = 'LocationIndexCompiled'
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)

    indexBucket = Column(String(100), primary_key=True)
    blobData = Column(PeekLargeBinary, nullable=False)
    lastUpdate = Column(String(50), nullable=False)

    modelSetId = Column(Integer,
                        ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(ModelSet)

    __table_args__ = (
        Index("idx_LIIndexUpdate_modelSetId", modelSetId, unique=False),
        Index("idx_LIIndexUpdate_indexBucket", indexBucket, unique=True),
    )
