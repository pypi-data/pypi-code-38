from coin_sdk.number_portability.domain import MessageType
from coin_sdk.number_portability.messages.common import EnumRepeatsBuilder
from coin_sdk.number_portability.messages.common import HeaderCreator
from coin_sdk.number_portability.messages.message import Message
from .deactivation import Deactivation
from .deactivation_seq import DeactivationSeq
from .deactivation_repeats import  DeactivationRepeats
from .deactivation_body import DeactivationBody
from .deactivation_message import  DeactivationMessage


class DeactivationBuilder(HeaderCreator):
    def __init__(self):
        super().__init__()
        self._currentnetworkoperator = None
        self._originalnetworkoperator = None
        self._dossierid = None
        self._deactivation_seqs = []

    def set_dossierid(self, dossierid: str):
        self._dossierid = dossierid
        return self

    def set_currentnetworkoperator(self, currentnetworkoperator: str):
        self._currentnetworkoperator = currentnetworkoperator
        return self

    def set_originalnetworkoperator(self, originalnetworkoperator: str):
        self._originalnetworkoperator = originalnetworkoperator
        return self

    def add_deactivation_seq(self):
        return DeactivationRepeatsBuilder(self)

    def build(self):
        repeats = [DeactivationRepeats(seq) for seq in self._deactivation_seqs]
        deactivation = Deactivation(
            self._dossierid,
            self._currentnetworkoperator,
            self._originalnetworkoperator,
            repeats
        )
        body = DeactivationBody(deactivation)
        message = DeactivationMessage(self._header, body)
        return Message(message, MessageType.DEACTIVATION_V1)


class DeactivationRepeatsBuilder(EnumRepeatsBuilder):
    def __init__(self, deactivation_builder: DeactivationBuilder):
        super().__init__()
        self._deactivation_builder = deactivation_builder

    def set_number_series(self, start: str, end: str):
        self._set_number_series(start, end)
        return self

    def finish(self):
        seq = DeactivationSeq(self._number_series)
        self._deactivation_builder._deactivation_seqs.append(seq)
        return self._deactivation_builder
