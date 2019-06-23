import logging

from sqlalchemy import Column, text
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index, Sequence

from peek_plugin_livedb._private.PluginNames import livedbTuplePrefix
from vortex.Tuple import Tuple, addTupleType, JSON_EXCLUDE
from .DeclarativeBase import DeclarativeBase
from .LiveDbModelSet import LiveDbModelSet

logger = logging.getLogger(__name__)


@addTupleType
class LiveDbItem(Tuple, DeclarativeBase):
    __tupleTypeShort__ = 'LDK'
    __tablename__ = 'LiveDbItem'
    __tupleType__ = livedbTuplePrefix + __tablename__

    NUMBER_VALUE = 0
    STRING_VALUE = 1
    COLOR = 2
    LINE_WIDTH = 3
    LINE_STYLE = 4
    GROUP_PTR = 5

    id_seq = Sequence('LiveDbItem_id_seq',
                      metadata=DeclarativeBase.metadata,
                      schema=DeclarativeBase.metadata.schema)
    id = Column(Integer, id_seq, server_default=id_seq.next_value(),
                primary_key=True, autoincrement=False)

    modelSetId = Column(Integer, ForeignKey('LiveDbModelSet.id', ondelete='CASCADE'),
                        doc=JSON_EXCLUDE, nullable=False)
    modelSet = relationship(LiveDbModelSet)

    # comment="The unique reference of the value we want from the live db"
    key = Column(String, nullable=False)

    # comment="The last value from the source"
    rawValue = Column(String)

    # comment="The PEEK value, converted to PEEK IDs if required (Color for example)"
    displayValue = Column(String)

    # comment="The type of data this value represents"
    dataType = Column(Integer, nullable=False)

    importHash = Column(String)

    # Store custom props for this link
    propsJson = Column(String)

    __table_args__ = (
        Index("idx_LiveDbDKey_importHash", importHash, unique=False),
        Index("idx_LiveDbDKey_modelSet_key", modelSetId, key, unique=True),
    )

