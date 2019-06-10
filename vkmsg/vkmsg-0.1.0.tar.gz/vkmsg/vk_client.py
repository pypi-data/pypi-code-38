import json
from urllib.parse import urlencode

import requests

from .errors import VkError
from .models.messages import Message
from .models.requests import IncomingRequest, IncomingMessage


class VkClient(object):
    def __init__(self, token, group_id, api_version='5.87'):
        self.token = token
        self.group_id = group_id
        self._vk_api_url = 'https://api.vk.com/method'
        self._api_version = api_version
        self._text_message_processor = None
        self._callback_processor = None

    def register_text_message_processor(self):
        def add(processor):
            self._text_message_processor = processor
            return processor

        return add

    def register_callback_processor(self):
        def add(processor):
            self._callback_processor = processor
            return processor

        return add

    def process_json(self, msg: dict):
        if not isinstance(msg, dict):
            raise TypeError('msg must be an instance of dict')
        request = IncomingRequest(**msg)
        if isinstance(request.object, IncomingMessage):
            if hasattr(request.object, 'payload'):
                if not self._callback_processor:
                    raise AttributeError('_callback_processor not declared')
                self._callback_processor(request)
                return None
            else:
                if not self._text_message_processor:
                    raise AttributeError('_text_message_processor not declared')
                self._text_message_processor(request)
                return None
        raise Exception('Now available just text_message')

    def send_message(self, user_id: int, message: Message):
        if not isinstance(user_id, int):
            raise TypeError('user_id must be an instance of int')
        if not isinstance(message, Message):
            raise TypeError('message must be an instance of Message')
        msg = message.to_dict()
        msg['user_id'] = user_id
        if msg.get('keyboard'):
            msg['keyboard'] = json.dumps(msg['keyboard'], ensure_ascii=False).encode("utf-8")
        result = self.post_request('messages.send', msg)
        if 'error' in result:
            raise VkError(**result['error'])
        return result['response']

    def get_callback_confirmation_code(self):
        result = self.post_request('groups.getCallbackConfirmationCode')
        if 'error' in result:
            raise VkError(**result['error'])
        return result['response']

    def set_webhook(self, url: str, title: str):
        if not isinstance(url, str):
            raise TypeError('url must be an instance of str')
        if not isinstance(title, str):
            raise TypeError('title must be an instance of str')
        result = self.post_request('groups.addCallbackServer', {'url': url, 'title': title})
        if 'error' in result:
            raise VkError(**result['error'])
        return result['response']

    def post_request(self, endpoint: str, data: dict = None):
        if data is None:
            data = {}
        if not isinstance(endpoint, str):
            raise TypeError('endpoint must be an instance of str')
        if not isinstance(data, dict):
            raise TypeError('data must be an instance of dict')
        headers = requests.utils.default_headers()
        data.update({'access_token': self.token, 'v': self._api_version, 'group_id': self.group_id})
        data = urlencode(data)
        response = requests.post(f'{self._vk_api_url}/{endpoint}', data=data, headers=headers)
        response.raise_for_status()
        return json.loads(response.text)
