from enum import Enum
from openProduction.common import Signals

class IOAnswer(Enum):
    YES = 0
    NO = 1
    CANCEL = 2

class BaseIOHandler:
    def __init__(self):
        self.signalMessage = Signals.Signal()

    def queryYesNo(self, msg, timeout=10):
        return IOAnswer.CANCEL

    def message(self, msg, timeout=10):
        self.signalMessage.emit(msg)

class IOMessage:
    def __init__(self, msg):
        self.msg = msg