import logging

_LOGGER = logging.getLogger(__name__)

class MessageHeader:

    def __init__(self, payload):
        self.payload = payload
        
        #_LOGGER.debug("__init__")
        if payload[0] == 3:
            if payload[1] == 0:
                self.msg_type = "Text"
            elif payload[1] == 1:
                self.msg_type = "Binary"
            elif payload[1] == 2:
                self.msg_type = "Value-States"
            elif payload[1] == 3:
                self.msg_type = "Text-States"
            elif payload[1] == 4:
                self.msg_type = "Daytime-States"
            elif payload[1] == 5:
                self.msg_type = "OutOfService"
            elif payload[1] == 6:
                self.msg_type = "KeepAlive"
            elif payload[1] == 7:
                self.msg_type = "Weather-States"
            
