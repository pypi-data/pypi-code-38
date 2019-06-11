import requests
from lxml import etree

SUPPORTED_ERROR_HTTP_STATUES = [400, 403, 404, 405, 408, 409, 413, 416, 418, 500, 501]


class Ks3Error(Exception):
    def __init__(self, status: int, code: str, message: str, resource: str, request_id: str):
        self._status = status
        self._code = code
        self._message = message
        self._resource = resource
        self._request_id = request_id
        super().__init__()

    def __repr__(self):
        return '{}(status={!r}, code={!r}, message={!r}, resource={!r}, request_id={!r})'.format(
            self.__class__.__qualname__,
            self._status,
            self._code,
            self._message,
            self._resource,
            self._request_id
        )

    def __str__(self):
        return self._message

    @property
    def status(self):
        return self._status

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def resource(self):
        return self._resource

    @property
    def request_id(self):
        return self._request_id


def raise_for_ks3_status(resp: requests.Response):
    status = resp.status_code
    if status in SUPPORTED_ERROR_HTTP_STATUES:
        if resp.content:
            root = etree.fromstring(resp.content)
            assert root.tag == 'Error'
            kv_args = {'status': status}
            kv_args.update({k: '' for k in ('code', 'message', 'resource', 'request_id')})
            for child in root:
                tag = child.tag.strip().lower()
                if tag in kv_args:
                    kv_args[tag] = child.text.strip()
            raise Ks3Error(**kv_args)
