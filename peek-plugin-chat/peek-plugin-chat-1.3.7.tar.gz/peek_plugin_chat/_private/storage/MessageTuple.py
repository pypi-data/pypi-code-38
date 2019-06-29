from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Index
from sqlalchemy.sql.sqltypes import DateTime

from peek_plugin_base.storage.TypeDecorators import PeekLargeBinary
from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from peek_plugin_chat._private.storage.ChatTuple import ChatTuple
from peek_plugin_chat._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_chat.server.ChatApiABC import NewMessage
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class MessageTuple(Tuple, DeclarativeBase):
    __tupleType__ = chatTuplePrefix + 'MessageTuple'
    __tablename__ = 'MessageTuple'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #: Foreign key to a chat
    chatId = Column(Integer,
                    ForeignKey(ChatTuple.id, ondelete="CASCADE"),
                    nullable=False)

    # Message details
    message = Column(String(2000), nullable=False)

    priority = Column(Integer, nullable=False)
    PRIORITY_EMERGENCY = NewMessage.PRIORITY_EMERGENCY
    PRIORITY_NORMAL_STICKY = NewMessage.PRIORITY_NORMAL_STICKY
    PRIORITY_NORMAL_FLEETING = NewMessage.PRIORITY_NORMAL_FLEETING

    # User to / from
    fromUserId = Column(String(40), nullable=False)

    # Message state details
    dateTime = Column(DateTime(True), nullable=False)

    onReadPayload = Column(PeekLargeBinary)

    __table_args__ = (
        Index("idx_ChatMsgTuple_chatId", chatId, unique=False),
        Index("idx_ChatMsgTuple_dateTime", dateTime, unique=False),
    )
