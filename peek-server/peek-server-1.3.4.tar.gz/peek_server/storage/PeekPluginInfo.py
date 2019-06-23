""" 
 * orm.ExtensionData.py
 *
 *  Copyright Synerty Pty Ltd 2011
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Index

from peek_server.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class PeekPluginInfo(Tuple, DeclarativeBase):
    """ PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server.plugin.info'
    __tablename__ = 'PeekPluginInfo'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    name = Column(String(50), nullable=False)
    version = Column(String(40), nullable=False)
    creator = Column(String, nullable=True)
    website = Column(String, nullable=True)
    buildNumber = Column(String, nullable=True)
    buildDate = Column(String, nullable=True)

    # File location columns
    fileName = Column(String, nullable=False)
    dirName = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_PeekPluginInfo_NameVersion",
              name, version, unique=True),
    )
