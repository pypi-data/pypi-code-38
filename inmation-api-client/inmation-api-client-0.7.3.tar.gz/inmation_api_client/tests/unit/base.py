import getpass
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path

p = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
sys.path.append(str(p))
sys.path.append(str(Path(p).parent))

from inmation_api_client.inclient import Client
from inmation_api_client.model import Item, Identity
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

AUTH['auth']['username'] = input('inmation Profile Username:')
AUTH['auth']['password'] = getpass.getpass('inmation Profile Password:')


def setup():
    client.Connect(options=opt)
    folder_name = 'PythonTestFolder ' + datetime.now().strftime('%H:%M:%S')

    response = client.RunScript(Identity('/System'), 'return inmation.getcorepath()')
    if 'data' not in response.keys():
        sys.exit('Enable the RunScript property of the WebAPIServer object under the Server model and try again.')
    else:
        core_path = response['data'][0]['v']

    path = core_path + '/' + folder_name

    client.Mass([
        {
            'path': path,
            'operation': 'UPSERT',
            'class': 'GenFolder',
            'ObjectName': folder_name
        }
    ])
    return core_path, path

core_path, path = setup()


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = client
        cls.opt = opt
        cls.path = path
        cls.core_path = core_path

    def connect(self):
        self.client.Connect(options=self.opt)

    def run_coro(self, coro):
        return self.client.GetEventLoop().run_until_complete(coro)
