""" 
 *  Copyright Synerty Pty Ltd 2017
 *
 *  MIT License
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
'''
import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class DirectoryTuple(Tuple, DeclarativeBase):
    """ Directory Table

    This table contains different directories that can be authenticated against.

    """
    __tupleType__ = userPluginTuplePrefix + 'DirectoryTuple'
    __tablename__ = 'Directory'

    TYPE_INTERNAL = 1
    # TYPE_ACTIVE_DIRECYORY = 2 // TODO

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(30), unique=True, nullable=False)
    name = Column(String(30), unique=True, nullable=False)
    type = Column(String, nullable=False)

    # __table_args__ = (
    #     Index("idx_UserDbTable_unique_index", userName,
    #           unique=True),
    # )
'''