from enum import Enum


class ConfirmationStatus(Enum):
    CONFIRMED = "Confirmed"
    ALL = "All"


class MessageType(Enum):
    PORTING_REQUEST_V1 = "portingrequest"
    PORTING_REQUEST_ANSWER_V1 = "portingrequestanswer"
    PORTING_PERFORMED_V1 = "portingperformed"
    PORTING_REQUEST_ANSWER_DELAYED_V1 = "pradelayed"
    CANCEL_V1 = "cancel"
    DEACTIVATION_V1 = "deactivation"
    CONFIRMATION_V1 = "confirmations"
    ERROR_FOUND_V1 = "errorfound"
    _VERSION_SUFFIX_V1 = "-v1"

    def get_event_type(self):
        return f'{self.value}{self._VERSION_SUFFIX_V1.value}'
