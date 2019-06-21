from .base import TelegramEndpoint
from .commons import DisableNotification


class ForwardMessage(TelegramEndpoint, DisableNotification):
    def __init__(self, chat_id, from_chat_id, message_id):
        args = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id
        }
        super().__init__(args=args)
