import requests
import json
from .log import *
from .mq_decode import list_queues, list_consumers, dict_queues


class RabbitmqFactory(object):
    def __init__(self, label):
        self.user = config(label, 'user')
        self.password = config(label, 'password')
        self.host = 'http://{}:{}'.format(config(label, 'host'), config(label, 'api_port'))

    def _api_get(self, url):
        _code = 0
        try:
            res = requests.get(self.host + url, auth=(self.user, self.password), timeout=5)
            if res.status_code == 200:
                return _code, json.loads(res.content.decode())
        except Exception as e:
            log_info(e.__str__())
            _code = -1
        return _code, []

    def list_queues(self, dict_type=False):
        url = '/api/queues'
        _queue_data = []
        if dict_type:
            _queue_data = {}
        _code, queues_list = self._api_get(url)
        if _code != 0:
            return _code, _queue_data
        if dict_type:
            return _code, dict_queues(queues_list)
        else:
            return _code, list_queues(queues_list)

    def list_consumers(self):
        url = '/api/consumers'
        _code, queues_list = self._api_get(url)
        if _code != 0:
            return _code, []
        return _code, list_consumers(queues_list)
