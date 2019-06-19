import logging
import sys
import unittest

from lbmessaging.services.Common import BaseService, ExposedIn

mapping1 = {
        'send': 'dumb_send',
        'receive': 'dumb_receive'
    }

mapping2 = {
        'send_2': 'dumb_send',
        'receive_2': 'dumb_receive'
    }

@ExposedIn("DumbService", mapping=mapping1)
@ExposedIn("DumbService2", mapping=mapping2)
class DumbExchange():

    def __init__(self, channel):
        self.channel = channel
        self.lastAction = None

    def dumb_send(self, arg1, kwarg1=None):
        print(arg1),
        print(kwarg1)
        self.lastAction = 'SENT'

    def dumb_receive(self):
        self.lastAction = 'RECEIVED'
        return 'RECEIVED'


@ExposedIn("DumbService")
class DumbExchange2():
    pass


class DumbService(BaseService):
    pass


class DumbService2(BaseService):
    pass


class TestExposeIn(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_meta_usage(self):
        srv = DumbService()
        try:
            srv.send()
            self.fail("Send with no arguments")
        except:
            pass
        srv.send('arg1', kwarg1='toto')
        res = srv.receive()
        self.assertEqual(res, 'RECEIVED')

    def test_meta_setup(self):
        srv = DumbService()
        for funct in mapping1.keys():
            self.assertTrue(funct in dir(srv))
        for funct in mapping2.keys():
            self.assertFalse(funct in dir(srv))
        srv = DumbService2()
        for funct in mapping2.keys():
            self.assertTrue(funct in dir(srv))

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
