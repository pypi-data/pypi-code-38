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

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Index
from sqlalchemy.orm import relationship

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase
from peek_core_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_core_user._private.storage.InternalUserGroupTuple import \
    InternalUserGroupTuple
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from vortex.Tuple import Tuple, addTupleType, TupleField

logger = logging.getLogger(__name__)


class InternalUserPassword(DeclarativeBase):
    """ Internal

    This table doesn't do anything

    """
    __tablename__ = 'InternalUserPassword'

    id = Column(Integer, primary_key=True, autoincrement=True)

    userId = Column(Integer, ForeignKey('InternalUser.id', ondelete='CASCADE'),
                    nullable=False)
    user = relationship(InternalUserTuple)

    password = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_InternalUserPassword_userId", userId, unique=True),
    )
