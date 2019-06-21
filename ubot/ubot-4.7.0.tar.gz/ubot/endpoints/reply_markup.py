from .base import TelegramEndpoint
from .commons import chat_or_inline_message
from .exceptions import InvalidInlineKeyboardButtonPosition, InvalidInlineKeyboardButtonType


class InlineKeyboard:
    button_types = ['url', 'callback_data', 'switch_inline_query', 'switch_inline_query_current_chat', 'callback_game',
                    'pay']
    must_be_first_button_types = ['callback_game', 'pay']

    def __init__(self):
        self.buttons = []

    def serialize(self):
        return {'inline_keyboard': self.buttons}

    def add_button(self, text, button_type, button_value):
        if button_type not in self.button_types:
            raise InvalidInlineKeyboardButtonType

        if button_type in self.must_be_first_button_types and self.buttons:
            raise InvalidInlineKeyboardButtonPosition('You must insert a callback_game/pay button as the first button')

        self.buttons.append({
            'text': text,
            button_type: button_value
        })
        return self


class ReplyKeyboard:
    def __init__(self):
        self.buttons = []
        self.options = {}

    def serialize(self):
        return {
            'keyboard': self.buttons,
            **self.options
        }

    def resize_keyboard(self):
        self.options['resize_keyboard'] = True
        return self

    def one_time_keyboard(self):
        self.options['one_time_keyboard'] = True
        return self

    def selective(self):
        self.options['selective'] = True
        return self

    def add_button(self, text, request_contact=False, request_location=False):
        button = {
            'text': text
        }

        if request_contact is True:
            button['request_contact'] = True

        if request_location is True:
            button['request_location'] = True

        self.buttons.append(button)
        return self


class ReplyKeyboardRemove:
    def __init__(self):
        self.options = {}

    def serialize(self):
        return {
            'remove_keyboard': True,
            **self.options
        }

    def selective(self):
        self.options['selective'] = True
        return self


class ForceReply:
    def __init__(self):
        self.options = {}

    def serialize(self):
        return {
            'force_reply': True,
            **self.options
        }

    def selective(self):
        self.options['selective'] = True
        return self


class ReplyMarkup:
    def reply_markup(self, reply_markup):
        self.args['reply_markup'] = reply_markup.serialize()
        return self


class AnswerCallbackQuery(TelegramEndpoint):
    def __init__(self, callback_query_id):
        args = {
            'callback_query_id': callback_query_id
        }
        super().__init__(args=args)

    def text(self, text):
        self.args['text'] = text
        return self

    def show_alert(self):
        self.args['show_alert'] = True
        return self

    def url(self, url):
        self.args['url'] = url
        return self

    def cache_time(self, cache_time):
        self.args['cache_time'] = cache_time
        return self


class EditMessageReplyMarkup(TelegramEndpoint, ReplyMarkup):
    def __init__(self, chat_or_inline_message_id, message_id):
        super().__init__(args=chat_or_inline_message(chat_or_inline_message_id, message_id))
