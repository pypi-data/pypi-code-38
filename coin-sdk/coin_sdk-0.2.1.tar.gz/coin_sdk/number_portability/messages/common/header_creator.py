from datetime import datetime

from .header import Header
from .sender import Sender
from .receiver import Receiver


class HeaderCreator:
    def __init__(self):
        self._header = None

    def set_header(self, sender_network_operator: str, receiver_network_operator: str, sender_service_provider: str = None, receiver_service_provider: str = None):
        sender = Sender(sender_network_operator, sender_service_provider)
        receiver = Receiver(receiver_network_operator, receiver_service_provider)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self._header = Header(receiver, sender, timestamp)
        return self
