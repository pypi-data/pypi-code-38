from .base import TelegramEndpoint
from .commons import DisableNotification, ParseMode, ReplyToMessageId, chat_or_inline_message
from .reply_markup import ReplyMarkup


class SendMessage(TelegramEndpoint, DisableNotification, ParseMode, ReplyMarkup, ReplyToMessageId):
    def __init__(self, chat_id, text):
        args = {
            'chat_id': chat_id,
            'text': text
        }
        super().__init__(args=args)

    def disable_web_page_overview(self):
        self.args['disable_web_page_overview'] = True
        return self


class EditMessageText(TelegramEndpoint, ParseMode, ReplyMarkup):
    def __init__(self, chat_or_inline_message_id, message_id, text):
        args = {
            'text': text,
            **chat_or_inline_message(chat_or_inline_message_id, message_id)
        }
        super().__init__(args=args)

    def disable_web_page_overview(self):
        self.args['disable_web_page_overview'] = True
        return self
