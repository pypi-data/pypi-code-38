import logging
import sys
import unittest

from lbmessaging.services.Common import ALL_EXCHANGES
from lbmessaging.services.Common import ExposedIn


@ExposedIn("DumbService_expose")
@ExposedIn("DumbService_expose2")
@ExposedIn("DumbService_expose3")
class DumbExchange():
    pass


@ExposedIn("DumbService_expose2")
class DumbExchange2():
    pass


@ExposedIn("DumbService_expose3", mapping={
    'toto': 'fifi'
})
class DumbExchange3():

    def fifi(self):
        pass


class TestExposeIn(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_services(self):
        self.assertTrue('DumbService_expose' in ALL_EXCHANGES.keys())
        self.assertTrue('DumbService_expose2' in ALL_EXCHANGES.keys())
        self.assertTrue('DumbService_expose3' in ALL_EXCHANGES.keys())

    def test_dumb_service_1(self):
        self.assertEqual(len(ALL_EXCHANGES['DumbService_expose']), 1)
        self.assertEqual(
            type(ALL_EXCHANGES['DumbService_expose'][0]['exchange']),
            type(DumbExchange))

    def test_dumb_service_2(self):
        self.assertEqual(len(ALL_EXCHANGES['DumbService_expose2']), 2)

        self.assertTrue(type(DumbExchange) in [type(x['exchange']) for x in
                                               ALL_EXCHANGES[
                                                   'DumbService_expose2']])
        self.assertTrue(type(DumbExchange2) in [type(x['exchange']) for x in
                                                ALL_EXCHANGES[
                                                    'DumbService_expose2']])

    def test_dumb_service_3(self):
        self.assertEqual(len(ALL_EXCHANGES['DumbService_expose3']), 2)

        self.assertEqual(
            list(ALL_EXCHANGES['DumbService_expose3'][1]['mapping'].keys()),
            ['toto'])

        self.assertTrue(type(DumbExchange) in [type(x['exchange']) for x in
                                               ALL_EXCHANGES[
                                                   'DumbService_expose3']])
        self.assertTrue(type(DumbExchange3) in [type(x['exchange']) for x in
                                                ALL_EXCHANGES[
                                                    'DumbService_expose3']])

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
