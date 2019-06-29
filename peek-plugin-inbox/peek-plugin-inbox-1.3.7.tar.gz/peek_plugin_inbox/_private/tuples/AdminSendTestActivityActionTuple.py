from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_plugin_inbox._private.PluginNames import inboxTuplePrefix


@addTupleType
class AdminSendTestActivityActionTuple (TupleActionABC):
    __tupleType__ = inboxTuplePrefix + "AdminSendTestActivityActionTuple"

    formData = TupleField()
