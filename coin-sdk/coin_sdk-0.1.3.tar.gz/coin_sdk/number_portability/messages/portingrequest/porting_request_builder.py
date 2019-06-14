from coin_sdk.number_portability.domain import MessageType
from coin_sdk.number_portability.messages.common import CustomerInfo, EnumRepeatsBuilder, HeaderCreator
from coin_sdk.number_portability.messages.message import Message
from .porting_request import PortingRequest
from .porting_request_body import PortingRequestBody
from .porting_request_message import PortingRequestMessage
from .porting_request_repeats import PortingRequestRepeats
from .porting_request_seq import PortingRequestSeq


class PortingRequestBuilder(HeaderCreator):
    def __init__(self):
        super().__init__()
        self._dossierid = None
        self._recipientnetworkoperator = None
        self._recipientserviceprovider = None
        self._donornetworkoperator = None
        self._donorserviceprovider = None
        self._note = None
        self._customerinfo = None
        self._porting_request_seqs = []

    def set_dossierid(self, dossierid: str):
        self._dossierid = dossierid
        return self

    def set_recipientnetworkoperator(self, recipientnetworkoperator: str):
        self._recipientnetworkoperator = recipientnetworkoperator
        return self

    def set_recipientserviceprovider(self, recipientserviceprovider: str):
        self._recipientserviceprovider = recipientserviceprovider
        return self

    def set_donornetworkoperator(self, donornetworkoperator: str):
        self._donornetworkoperator = donornetworkoperator
        return self

    def set_donorserviceprovider(self, donorserviceprovider: str):
        self._donorserviceprovider = donorserviceprovider
        return self

    def set_note(self, note: str):
        self._note = note
        return self

    def set_customerinfo(self, lastname: str = None, companyname: str = None, housenr: str = None, housenrext: str = None, postcode: str = None, customerid: str = None):
        self._customerinfo = CustomerInfo(lastname, companyname, housenr, housenrext, postcode, customerid)
        return self

    def add_porting_request_seq(self):
        return PortingRequestRepeatsBuilder(self)

    def build(self):
        repeats = [PortingRequestRepeats(seq) for seq in self._porting_request_seqs]
        porting_request = PortingRequest(
            self._dossierid,
            self._recipientserviceprovider,
            self._recipientnetworkoperator,
            self._donornetworkoperator,
            self._donorserviceprovider,
            self._customerinfo,
            self._note,
            repeats
        )
        body = PortingRequestBody(porting_request)
        message = PortingRequestMessage(self._header, body)
        return Message(message, MessageType.PORTING_REQUEST_V1)


class PortingRequestRepeatsBuilder(EnumRepeatsBuilder):
    def __init__(self, porting_request_builder: PortingRequestBuilder):
        super().__init__()
        self._porting_request_builder = porting_request_builder

    def set_number_series(self, start: str, end: str):
        self._set_number_series(start, end)
        return self

    def add_enum_profiles(self, *profileids):
        self._add_enum_prof_seq(*profileids)
        return self

    def finish(self):
        seq = PortingRequestSeq(self._number_series, self._enum_repeats)
        self._porting_request_builder._porting_request_seqs.append(seq)
        return self._porting_request_builder
