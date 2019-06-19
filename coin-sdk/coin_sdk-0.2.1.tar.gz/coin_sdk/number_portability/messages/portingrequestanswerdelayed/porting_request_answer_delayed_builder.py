from coin_sdk.number_portability.domain import MessageType
from coin_sdk.number_portability.messages.common import HeaderCreator
from coin_sdk.number_portability.messages.message import Message
from .porting_request_answer_delayed import PortingRequestAnswerDelayed
from .porting_request_answer_delayed_body import PortingRequestAnswerDelayedBody
from .porting_request_answer_delayed_message import PortingRequestAnswerDelayedMessage


class PortingRequestAnswerDelayedBuilder(HeaderCreator):
    def __init__(self):
        HeaderCreator.__init__(self)
        self._dossierid = None
        self._donornetworkoperator = None
        self._donorserviceprovider = None
        self._answerduedatetime = None
        self._reasoncode = None

    def set_dossierid(self, dossierid):
        self._dossierid = dossierid
        return self

    def set_donornetworkoperator(self, donornetworkoperator: str):
        self._donornetworkoperator = donornetworkoperator
        return self

    def set_donorserviceprovider(self, donorserviceprovider: str):
        self._donorserviceprovider = donorserviceprovider
        return self

    def set_answerduedatetime(self, answerduedatetime: str):
        self._answerduedatetime = answerduedatetime
        return self

    def set_reasoncode(self, reasoncode: str):
        self._reasoncode = reasoncode
        return self

    def build(self):
        delayed = PortingRequestAnswerDelayed(
            self._dossierid,
            self._donornetworkoperator,
            self._donorserviceprovider,
            self._answerduedatetime,
            self._reasoncode
        )
        body = PortingRequestAnswerDelayedBody(delayed)
        message = PortingRequestAnswerDelayedMessage(self._header, body)
        return Message(message, MessageType.PORTING_REQUEST_ANSWER_DELAYED_V1)

