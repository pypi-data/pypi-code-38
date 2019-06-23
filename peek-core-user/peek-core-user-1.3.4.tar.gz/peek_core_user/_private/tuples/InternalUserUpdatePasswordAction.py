import logging

from vortex.TupleAction import TupleActionABC

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class InternalUserUpdatePasswordAction(TupleActionABC):
    __tupleType__ = userPluginTuplePrefix + "InternalUserUpdatePasswordAction"

    userId: int = TupleField()
    newPassword: str = TupleField()
