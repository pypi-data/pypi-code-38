""" 
 *  Copyright Synerty Pty Ltd 2016
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import logging

from sqlalchemy import Column, DateTime
from sqlalchemy import Integer, String
from vortex.Tuple import Tuple, addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class UserLoggedIn(Tuple, DeclarativeBase):
    """ UserLoggedIn

    This table stores which users are logged into which devices

    """
    __tupleType__ = userPluginTuplePrefix + 'UserLoggedIn'
    __tablename__ = 'UserLoggedIn'

    id = Column(Integer, primary_key=True, autoincrement=True)
    loggedInDateTime = Column(DateTime(True), nullable=False)
    userName = Column(String(50), unique=True)
    deviceToken = Column(String(100), unique=True, nullable=False)
    vehicle = Column(String)
