import json

from .commons import Caption
from ..base import TelegramEndpoint
from ..commons import DisableNotification, ParseMode, ReplyToMessageId, chat_or_inline_message
from ..exceptions import InvalidMediaType
from ..reply_markup import ReplyMarkup
from ...utils import MultipartEncoder


class SendMedia(TelegramEndpoint, DisableNotification, ReplyMarkup, ReplyToMessageId):
    def __init__(self, file, chat_id):
        args = {
            'chat_id': chat_id
        }
        if file.args:
            args.update(file.args)

        endpoint = f'Send{file.__class__.__name__}'

        if file.method == 'POST':
            multipart_encoder = MultipartEncoder()
            multipart_encoder.files = file.value
            boundary, data = multipart_encoder.encode()
            headers = {
                'content-type': f'multipart/form-data; boundary={boundary}'
            }
            super().__init__(method='POST', endpoint=endpoint, args=args, data=data, headers=headers)
        else:
            args[file.file_type] = file.value
            super().__init__(endpoint=endpoint, args=args)


class SendMediaGroup(TelegramEndpoint, DisableNotification, ReplyToMessageId):
    media_types = ['photo', 'video']

    def __init__(self, chat_id, files, json_lib=None):
        if json_lib is None:
            _json = json
        else:
            _json = json_lib

        self.__multipart_encoder = None
        method = 'GET'
        media = []

        for file in files:
            if file.file_type not in self.media_types:
                raise InvalidMediaType('You can only use Photo and Video in SendMediaGroup')

            serialized, files = file.to_input_media()
            media.append(serialized)
            if files is not None:
                method = 'POST'
                self.multipart_encoder.files.extend(files)

        args = {
            'chat_id': chat_id,
            'media': _json.dumps(media)
        }

        if method == 'POST':
            boundary, data = self.multipart_encoder.encode()
            headers = {
                'content-type': f'multipart/form-data; boundary={boundary}'
            }
            super().__init__(method='POST', args=args, data=data, headers=headers)
        else:
            super().__init__(args=args)

    @property
    def multipart_encoder(self):
        if self.__multipart_encoder is None:
            self.__multipart_encoder = MultipartEncoder()
        return self.__multipart_encoder


class GetFile(TelegramEndpoint):
    # https://api.telegram.org/file/bot<token>/<file_path>
    def __init__(self, file_id):
        args = {
            'file_id': file_id
        }
        super().__init__(args=args)


class EditMessageCaption(TelegramEndpoint, Caption, ParseMode, ReplyMarkup):
    def __init__(self, chat_or_inline_message_id, message_id):
        args = chat_or_inline_message(chat_or_inline_message_id, message_id)
        super().__init__(args=args)


class EditMessageMedia(TelegramEndpoint, ReplyMarkup):
    def __init__(self, chat_or_inline_message_id, message_id, media):
        args = {
            'media': media.to_input_media(),
            **chat_or_inline_message(chat_or_inline_message_id, message_id)
        }
        super().__init__(args=args)
