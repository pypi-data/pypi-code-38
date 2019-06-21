from .base import TelegramEndpoint


class GetMe(TelegramEndpoint):
    pass


class GetUserProfilePhotos(TelegramEndpoint):
    def __init__(self, user_id):
        args = {
            'user_id': user_id
        }
        super().__init__(args=args)

    def offset(self, offset):
        self.args['offset'] = offset
        return self

    def limit(self, limit):
        self.args['limit'] = limit
        return self


class DeleteMessage(TelegramEndpoint):
    def __init__(self, chat_id, message_id):
        args = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        super().__init__(args=args)
