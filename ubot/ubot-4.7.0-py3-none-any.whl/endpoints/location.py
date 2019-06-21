from .base import TelegramEndpoint
from .commons import DisableNotification, ReplyToMessageId, chat_or_inline_message
from .reply_markup import ReplyMarkup


class SendLocation(TelegramEndpoint, DisableNotification, ReplyMarkup, ReplyToMessageId):
    def __init__(self, chat_id, latitude, longitude):
        args = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude
        }
        super().__init__(args=args)

    def live_period(self, live_period):
        self.args['live_period'] = live_period
        return self


class EditMessageLiveLocation(TelegramEndpoint, ReplyMarkup):
    def __init__(self, chat_or_inline_message_id, message_id, latitude, longitude):
        args = {
            'latitude': latitude,
            'longitude': longitude,
            **chat_or_inline_message(chat_or_inline_message_id, message_id)
        }
        super().__init__(args=args)


class StopMessageLiveLocation(TelegramEndpoint, ReplyMarkup):
    def __init__(self, chat_or_inline_message_id, message_id):
        super().__init__(args=chat_or_inline_message(chat_or_inline_message_id, message_id))
