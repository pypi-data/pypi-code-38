from peek_plugin_inbox._private.PluginNames import inboxTuplePrefix
from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC


@addTupleType
class AdminSendTestTaskActionTuple(TupleActionABC):
    __tupleType__ = inboxTuplePrefix + "AdminSendTestTaskActionTuple"

    formData = TupleField()
