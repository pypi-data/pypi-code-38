from coin_sdk.number_portability.domain import MessageType
from coin_sdk.number_portability.messages.common import HeaderCreator
from coin_sdk.number_portability.messages.message import Message
from .cancel import Cancel
from .cancel_message import CancelMessage
from .cancel_body import CancelBody


class CancelBuilder(HeaderCreator):
    def __init__(self):
        HeaderCreator.__init__(self)
        self._dossierid = None
        self._note = None

    def set_dossierid(self, dossierid):
        self._dossierid = dossierid
        return self

    def set_note(self, note: str):
        self._note = note
        return self

    def build(self):
        cancel = Cancel(self._dossierid, self._note)
        body = CancelBody(cancel)
        message = CancelMessage(self._header, body)
        return Message(message, MessageType.CANCEL_V1)

