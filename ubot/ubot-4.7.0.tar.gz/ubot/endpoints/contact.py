from .base import TelegramEndpoint
from .commons import DisableNotification, ReplyToMessageId
from .reply_markup import ReplyMarkup


class SendContact(TelegramEndpoint, DisableNotification, ReplyMarkup, ReplyToMessageId):
    def __init__(self, chat_id, phone_number, first_name):
        args = {
            'chat_id': chat_id,
            'phone_number': phone_number,
            'first_name': first_name  # noqa: S001
        }
        super().__init__(args=args)

    def last_name(self, last_name):
        self.args['last_name'] = last_name
        return self

    def vcard(self, vcard):
        self.args['vcard'] = vcard
        return self
