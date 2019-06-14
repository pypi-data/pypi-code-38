from coin_sdk.number_portability.domain import MessageType
from coin_sdk.number_portability.messages.common import EnumRepeatsBuilder
from coin_sdk.number_portability.messages.common import HeaderCreator
from coin_sdk.number_portability.messages.message import Message
from .porting_request_answer import PortingRequestAnswer
from .porting_request_answer_seq import PortingRequestAnswerSeq
from .porting_request_answer_repeats import PortingRequestAnswerRepeats
from .porting_request_answer_message import PortingRequestAnswerMessage
from .porting_request_answer_body import PortingRequestAnswerBody


class PortingRequestAnswerBuilder(HeaderCreator):
    def __init__(self):
        super().__init__()
        self._blocking = None
        self._dossierid = None
        self._answer_seqs = []

    def set_dossierid(self, dossierid: str):
        self._dossierid = dossierid
        return self

    def set_blocking(self, blocking: str):
        self._blocking = blocking
        return self

    def add_porting_request_answer_seq(self):
        return PortingRequestAnswerRepeatsBuilder(self)

    def build(self):
        repeats = [PortingRequestAnswerRepeats(seq) for seq in self._answer_seqs]
        answer = PortingRequestAnswer(
            self._dossierid,
            self._blocking,
            repeats
        )
        body = PortingRequestAnswerBody(answer)
        message = PortingRequestAnswerMessage(self._header, body)
        return Message(message, MessageType.PORTING_REQUEST_ANSWER_V1)


class PortingRequestAnswerRepeatsBuilder(EnumRepeatsBuilder):
    def __init__(self, answer_builder: PortingRequestAnswerBuilder):
        super().__init__()
        self._answer_builder = answer_builder
        self._blockingcode = None
        self._firstpossibledate = None
        self._note = None
        self._donornetworkoperator = None
        self._donorserviceprovider = None

    def set_number_series(self, start: str, end: str):
        self._set_number_series(start, end)
        return self

    def set_blockingcode(self, blockingcode: str):
        self._blockingcode = blockingcode
        return self

    def set_firstpossibledate(self, firstpossibledate: str):
        self._firstpossibledate = firstpossibledate
        return self

    def set_note(self, note: str):
        self._note = note
        return self

    def set_donornetworkoperator(self, donornetworkoperator: str):
        self._donornetworkoperator = donornetworkoperator
        return self

    def set_donorserviceprovider(self, donorserviceprovider):
        self._donorserviceprovider = donorserviceprovider
        return self

    def finish(self):
        seq = PortingRequestAnswerSeq(self._number_series, self._blockingcode, self._firstpossibledate, self._note, self._donornetworkoperator, self._donorserviceprovider)
        self._answer_builder._answer_seqs.append(seq)
        return self._answer_builder
