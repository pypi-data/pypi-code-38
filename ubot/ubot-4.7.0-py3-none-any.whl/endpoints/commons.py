from .exceptions import InvalidParseMode


def chat_or_inline_message(chat_or_inline_message_id, message_id):
    if message_id is not None:
        return {
            'chat_id': chat_or_inline_message_id,
            'message_id': message_id
        }
    else:
        return {
            'inline_message_id': chat_or_inline_message_id
        }


class ReplyToMessageId:
    def reply_to_message_id(self, message_id):
        self.args['reply_to_message_id'] = message_id
        return self


class DisableNotification:
    def disable_notification(self):
        self.args['disable_notification'] = True
        return self


class ParseMode:
    parse_modes = ['Markdown', 'HTML']

    def parse_mode(self, parse_mode):
        if parse_mode not in self.parse_modes:
            raise InvalidParseMode

        self.args['parse_mode'] = parse_mode
        return self
