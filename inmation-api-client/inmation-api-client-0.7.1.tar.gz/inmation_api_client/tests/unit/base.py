import os
import sys
import unittest
from pathlib import Path

p = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
sys.path.append(str(p))
sys.path.append(str(Path(p).parent))

from inmation_api_client.inclient import Client
from inmation_api_client.model import Item
from inmation_api_client.options import Options

AUTH = {
    'auth': {
        'username': 'username',
        'password': 'password',
    }
}
OPTIONS = Options(AUTH)

client = Client()
# client.EnableDebug()
opt = OPTIONS
client.Connect(options=opt)


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = client
        cls.opt = opt
        cls.path = '/System/Core/PythonApiTests/'
        cls.HolderItems = [cls.path + i for i in ['Item01', 'Item02', 'Item03']]

    def connect(self):
        self.client.Connect(options=self.opt)

    def run_coro(self, coro):
        return self.client.GetEventLoop().run_until_complete(coro)
