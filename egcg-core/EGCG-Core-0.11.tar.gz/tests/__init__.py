import json
import os.path
import unittest
from unittest.mock import Mock
from egcg_core.config import cfg


class FakeRestResponse(Mock):
    request = Mock(method='a method', path_url='a url')
    status_code = 200
    reason = 'a reason'

    def __init__(self, content, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = json.dumps(content).encode()

    def json(self):
        return json.loads(self.text)

    @property
    def text(self):
        return self.content.decode('utf-8')


class TestEGCG(unittest.TestCase):
    file_path = os.path.dirname(__file__)
    assets_path = os.path.join(file_path, 'assets')
    etc = os.path.join(os.path.dirname(file_path), 'etc')
    etc_config = os.path.join(etc, 'example_egcg.yaml')

    @classmethod
    def setUpClass(cls):
        cfg.load_config_file(cls.etc_config)
