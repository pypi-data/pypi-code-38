from coin_sdk.number_portability.domain import MessageType
from coin_sdk.number_portability.messages.common import EnumRepeatsBuilder, HeaderCreator
from coin_sdk.number_portability.messages.message import Message
from .porting_performed import PortingPerformed
from .porting_performed_body import PortingPerformedBody
from .porting_performed_message import PortingPerformedMessage
from .porting_performed_repeats import PortingPerformedRepeats
from .porting_performed_seq import PortingPerformedSeq


class PortingPerformedBuilder(HeaderCreator):
    def __init__(self):
        super().__init__()
        self._dossierid = None
        self._recipientnetworkoperator = None
        self._donornetworkoperator = None
        self._actualdatetime = None
        self._batchporting = None
        self._porting_performed_seqs = []

    def set_dossierid(self, dossier_id: str):
        self._dossierid = dossier_id
        return self

    def set_recipientnetworkoperator(self, recipientnetworkoperator: str):
        self._recipientnetworkoperator = recipientnetworkoperator
        return self

    def set_donornetworkoperator(self, donornetworkoperator: str):
        self._donornetworkoperator = donornetworkoperator
        return self

    def set_actualdatetime(self, actualdatetime: str):
        self._actualdatetime = actualdatetime
        return self

    def set_batchporting(self, batchporting: str):
        self._batchporting = batchporting
        return self

    def add_porting_performed_seq(self):
        return PortingPerformedRepeatsBuilder(self)

    def build(self):
        repeats = [PortingPerformedRepeats(seq) for seq in self._porting_performed_seqs]
        porting_performed = PortingPerformed(
            self._dossierid,
            self._recipientnetworkoperator,
            self._donornetworkoperator,
            self._actualdatetime,
            self._batchporting,
            repeats
        )
        body = PortingPerformedBody(porting_performed)
        message = PortingPerformedMessage(self._header, body)
        return Message(message, MessageType.PORTING_PERFORMED_V1)


class PortingPerformedRepeatsBuilder(EnumRepeatsBuilder):
    def __init__(self, porting_performed_builder: PortingPerformedBuilder):
        super().__init__()
        self._porting_performed_builder = porting_performed_builder
        self._backporting = None
        self._pop = None

    def set_number_series(self, start: str, end: str):
        self._set_number_series(start, end)
        return self

    def add_enum_profiles(self, *profileids):
        self._add_enum_prof_seq(*profileids)
        return self

    def set_backporting(self, backporting: str):
        self._backporting = backporting
        return self

    def set_pop(self, pop: str):
        self._pop = pop
        return self

    def finish(self):
        seq = PortingPerformedSeq(
            self._number_series,
            self._backporting,
            self._pop,
            self._enum_repeats
        )
        self._porting_performed_builder._porting_performed_seqs.append(seq)
        return self._porting_performed_builder
