from abc import ABC

from ..utils import CaseInsensitiveDict


class TelegramEndpoint(ABC):
    def __init__(self, method: str = 'GET', endpoint: str = None, args: dict = None, data: bytes = None,
                 headers: dict = None):
        if endpoint is None:
            _classname = self.__class__.__name__
            self.endpoint = f'{_classname[0].lower()}{_classname[1:]}'
        else:
            self.endpoint = endpoint

        self.method = method
        self.args = args if args is not None else {}
        self.data = data
        self.headers = CaseInsensitiveDict(headers) if headers is not None else CaseInsensitiveDict()

    def serialize(self):
        return self.method, self.endpoint, self.args, self.data, self.headers
