from .base import TelegramEndpoint
from .exceptions import InvalidChatAction


class SendChatAction(TelegramEndpoint):
    actions = ['typing', 'upload_photo', 'record_video', 'upload_video', 'record_audio', 'upload_audio',
               'upload_document', 'find_location', 'record_video_note', 'upload_video_note']

    def __init__(self, chat_id, action):
        if action not in self.actions:
            raise InvalidChatAction
        args = {
            'chat_id': chat_id,
            'action': action  # noqa: S001
        }
        super().__init__(args=args)
