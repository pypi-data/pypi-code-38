from sqlalchemy import Column, Integer, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, String

from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from peek_plugin_chat._private.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class ChatTuple(Tuple, DeclarativeBase):
    __tupleType__ = chatTuplePrefix + 'ChatTuple'
    __tablename__ = 'ChatTuple'

    # This will include the users relationship when serialising the data
    __fieldNames__ = ["users"]

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Message details
    lastActivity = Column(DateTime(True), nullable=False)

    #: Unique users key, A comma separated string of the users in this chat
    #  This is used to ensure there is only one chat for these user combinations.
    usersKey = Column(String(4000), nullable=False)

    # Use a TupleField instead of a relationship so we can decide when it will
    # include the messages or not.
    messages = TupleField()  # relationship("Message.chatId")

    users = relationship("ChatUserTuple", lazy='joined')

    __table_args__ = (
        Index("idx_Chat_usersKey", usersKey, unique=True),
    )
