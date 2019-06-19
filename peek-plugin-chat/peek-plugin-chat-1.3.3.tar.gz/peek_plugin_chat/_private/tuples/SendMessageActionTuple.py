from peek_plugin_chat._private.PluginNames import chatTuplePrefix
from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC


@addTupleType
class SendMessageActionTuple(TupleActionABC):
    __tupleType__ = chatTuplePrefix + "SendMessageActionTuple"

    chatId = TupleField(typingType=int)
    fromUserId = TupleField(typingType=str)
    message = TupleField(typingType=str)
    priority = TupleField(typingType=int)
