import unittest
from datetime import datetime

from cpbox.app import eventlog
from cpbox.app.devops import DevOpsApp


class App(DevOpsApp):
    def __init__(self):
        DevOpsApp.__init__(self, 'cptool-test')


class TestToolUtils(unittest.TestCase):

    def setUp(self):
        self.app = App()

    def test_event_log(self):
        for i in range(1, 10):
            payload = {'time': str(datetime.now())}
            eventlog.add_event_log('test', payload)


if __name__ == '__main__':
    unittest.main()
