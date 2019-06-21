from .base import TelegramEndpoint
from .commons import DisableNotification
from ..utils import MultipartEncoder


class ExportChatInviteLink(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)


class SetChatPhoto(TelegramEndpoint):
    def __init__(self, chat_id, photo):
        args = {
            'chat_id': chat_id
        }
        self.multipart_encoder = MultipartEncoder()
        self.multipart_encoder.add_file('photo', photo)
        boundary, data = self.multipart_encoder.encode()
        headers = {
            'content-type': f'multipart/form-data; boundary={boundary}'
        }
        super().__init__(method='POST', args=args, data=data, headers=headers)


class DeleteChatPhoto(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)


class SetChatTitle(TelegramEndpoint):
    def __init__(self, chat_id, title):
        args = {
            'chat_id': chat_id,
            'title': title
        }
        super().__init__(args=args)


class SetChatDescription(TelegramEndpoint):
    def __init__(self, chat_id, description):
        args = {
            'chat_id': chat_id,
            'description': description
        }
        super().__init__(args=args)


class PinChatMessage(TelegramEndpoint, DisableNotification):
    def __init__(self, chat_id, message_id):
        args = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        super().__init__(args=args)


class UnpinChatMessage(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)


class LeaveChat(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)


class GetChat(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)


class GetChatAdministrators(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)


class GetChatMemberCount(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)


class GetChatMember(TelegramEndpoint):
    def __init__(self, chat_id, user_id):
        args = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        super().__init__(args=args)


class SetChatStickerSet(TelegramEndpoint):
    def __init__(self, chat_id, sticker_set_name):
        args = {
            'chat_id': chat_id,
            'sticker_set_name': sticker_set_name
        }
        super().__init__(args=args)


class DeleteChatStickerSet(TelegramEndpoint):
    def __init__(self, chat_id):
        args = {
            'chat_id': chat_id
        }
        super().__init__(args=args)
