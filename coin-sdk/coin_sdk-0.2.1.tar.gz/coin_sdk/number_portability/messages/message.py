from coin_sdk.number_portability.domain import MessageType

class Message:
    def __init__(self, message, message_type: MessageType):
        self._message = message
        self._message_type = message_type

    def get_message(self):
        return self._message

    def get_message_type(self):
        return self._message_type

    def to_dict(self):
        return {'message': self._message.to_dict()}

    def __str__(self):
        return str(self.to_dict())
