import unittest
from datetime import datetime
from ttlab import FlowReactor


class FlowReactorTestCases(unittest.TestCase):

    class FlowReactorDataExample:
        filename = 'tests/mock_data/flow_reactor_example.txt'
        d = datetime(2018,1,16,14,13,10)
        start_time = d.timestamp()

    def test_import_flow_reactor(self):
        result = FlowReactor(self.FlowReactorDataExample.filename)
        self.assertEqual(self.FlowReactorDataExample.filename, result.filename)
        self.assertEqual(self.FlowReactorDataExample.start_time, result.start_time)

