from typing import List

from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC


@addTupleType
class CreateChatActionTuple(TupleActionABC):
    __tupleType__ = chatTuplePrefix + "CreateChatActionTuple"

    userIds = TupleField(typingType=List)
    fromUserId = TupleField(typingType=str)
