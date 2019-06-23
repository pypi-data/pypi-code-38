""" 
 *  Copyright Synerty Pty Ltd 2017
 *
 *  MIT License
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""

import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String, Index

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class InternalGroupTuple(Tuple, DeclarativeBase):
    """ Group Table

    This table contains the user plugin groups, for the internal directory.

    """
    __tupleType__ = userPluginTuplePrefix + 'InternalGroupTuple'
    __tablename__ = 'InternalGroup'

    id = Column(Integer, primary_key=True, autoincrement=True)
    groupName = Column(String, unique=True, nullable=False)
    groupTitle = Column(String, unique=True, nullable=False)

    importHash = Column(String)

    __table_args__ = (
        Index("idx_InternalGroupTable_importHash", importHash),
    )
