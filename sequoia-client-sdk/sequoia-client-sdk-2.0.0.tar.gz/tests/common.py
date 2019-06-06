import json
import unittest

import shutil
import tempfile
import yaml
from abc import ABCMeta
from collections import namedtuple


class TestGeneric(unittest.TestCase):
    __metaclass__ = ABCMeta

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config = self._load_config_yaml()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _load_config_yaml(self):
        with open("./tests/config.yml", 'r') as ymlfile:
            cfg = json.loads(json.dumps(yaml.safe_load(ymlfile)),
                             object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        return cfg
