import unittest
import sys
import os
sys.path.append(os.pardir)
from odstibmivb import ODStibMivb

# put here your own api key
API_KEY = '2133c416f69f5acaa67351501153d892'

class TestODStibMivb(unittest.TestCase):
    def setUp(self):
        self.api_instance = ODStibMivb(API_KEY)

    def test_get_vehicle_position_single(self):
        result = self.api_instance.get_vehicle_position(('1',))
        self.assertEqual(result['lines'][0]['lineId'], '1')

    def test_get_vehicle_position_multiple(self):
        result = self.api_instance.get_vehicle_position(('1','5'))
        self.assertEqual(result['lines'][0]['lineId'], '1')
        self.assertEqual(result['lines'][1]['lineId'], '5')

    def test_get_waiting_time_single(self):
        result = self.api_instance.get_waiting_time(('8301',))
        self.assertEqual(result['points'][0]['pointId'], '8301')

    def test_get_waiting_time_multiple(self):
        result = self.api_instance.get_waiting_time(('8301', '8302'))
        self.assertEqual(result['points'][0]['pointId'], '8301')
        self.assertEqual(result['points'][1]['pointId'], '8302')

    def test_get_message_by_line_single(self):
        result = self.api_instance.get_message_by_line(('1',))
        assert isinstance(result, dict)

    def test_get_message_by_line_multiple(self):
        result = self.api_instance.get_message_by_line(('1','5'))
        assert isinstance(result, dict)

    def test_get_stops_by_line_single(self):
        result = self.api_instance.get_stops_by_line(('1',))
        self.assertEqual(result['lines'][0]['destination']['fr'], 'STOCKEL')

    def test_get_stops_by_line_multiple(self):
        result = self.api_instance.get_stops_by_line(('1','5'))
        self.assertEqual(result['lines'][0]['destination']['fr'], 'STOCKEL')
        self.assertEqual(result['lines'][1]['destination']['nl'], 'WESTSTATION')

    def test_get_point_detail_single(self):
        result = self.api_instance.get_point_detail(('8301',))
        self.assertEqual(result['points'][0]['name']['fr'], 'TRONE')

    def test_get_point_detail_multiple(self):
        result = self.api_instance.get_point_detail(('8301', '0470F'))
        self.assertEqual(result['points'][0]['name']['fr'], 'TRONE')
        self.assertEqual(result['points'][1]['name']['fr'], 'SIMONIS')

if __name__ == '__main__':
    unittest.main()
