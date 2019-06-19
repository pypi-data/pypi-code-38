from fastscoredeploy.suite import Connect

from unittest import TestCase
from mock import patch

class SuiteTests(TestCase):

    class ServiceInfo(object):
        def __init__(self, name):
            self.api = 'engine'
            self.name = name
            self.health = 'ok'

    class ActiveModelInfo(object):
        class SchemaInfo(object):
            def __init__(self, schema = {"type":"int"}):
                self.schema = schema
                self.recordsets = False

        def __init__(self):
            self.slots = [self.SchemaInfo(), self.SchemaInfo()]


    class StreamInfo(object):
        def __init__(self, slot=0):
            self.descriptor = {"Transport":{"Type": "REST"}}
            self.slot = slot

    class EngineStateInfo(object):
        def __init__(self):
            self.state = 'RUNNING'

    @patch('fastscore.suite.connect.ConnectApi.connect_get',
                return_value=[ServiceInfo('engine-1')])
    def setUp(self, connect_get):
        self.connect = Connect('https://dashboard:1234')
        self.engine = self.connect.get('engine-1')

    @patch('fastscore.suite.engine.EngineApi2.engine_state_get',
            return_value=EngineStateInfo())
    @patch('fastscore.suite.engine.EngineApi2.active_model_get',
            return_value=ActiveModelInfo())
    @patch('fastscore.suite.engine.EngineApi2.active_stream_list',
            return_value=[StreamInfo(0), StreamInfo(1)])
    @patch('fastscore.suite.engine.EngineApi.job_io_input')
    @patch('fastscore.suite.engine.EngineApi.job_io_output',
            return_value='1\n2\n3\n4\n{"$fastscore":"pig"}\n')
    def test_score(self, job_output, job_input, active_streams, active_model, state):
        data = [1, 2, 3, 4]
        scores = self.engine.score(data)
        self.assertEqual(scores, [1, 2, 3, 4])
        job_output.assert_called_once()
        job_input.assert_called_once_with(instance='engine-1', data='1\n2\n3\n4\n{"$fastscore":"pig"}\n', id=1)
        active_model.assert_called_once()
        active_streams.assert_called_once()
