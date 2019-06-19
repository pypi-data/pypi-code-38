from sqlalchemy import Column, ForeignKey, LargeBinary
from sqlalchemy import Integer, Index
from sqlalchemy.orm import relationship

from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .ChatUserTuple import ChatUserTuple
from .DeclarativeBase import DeclarativeBase
from .MessageTuple import MessageTuple


@addTupleType
class MessageReadPayloadTuple(Tuple, DeclarativeBase):
    __tupleType__ = chatTuplePrefix + 'MessageReadPayloadTuple'
    __tablename__ = 'MessageReadPayloadTuple'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #: Foreign key to a Message
    messageId = Column(Integer,
                       ForeignKey(MessageTuple.id, ondelete="CASCADE"),
                       nullable=False)
    message = relationship(MessageTuple)

    #: Foreign key to a ChatUser
    chatUserId = Column(Integer,
                        ForeignKey(ChatUserTuple.id, ondelete="CASCADE"),
                        nullable=True)
    chatUser = relationship(ChatUserTuple)

    onReadPayload = Column(LargeBinary, nullable=False)

    __table_args__ = (
        Index("idx_ChatPayloads", messageId, chatUserId, unique=False),
    )
