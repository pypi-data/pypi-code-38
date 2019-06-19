import unittest
from unittest.mock import (patch, Mock)
from decimal import Decimal
from datetime import (datetime, timedelta)
from psense_common import PSenseAWSInterface


class TestAWSItfc(unittest.TestCase):
    @patch('boto3.session.Session')
    def setUp(self, aws):
        self.mock_table = Mock()
        self.mock_db = Mock()
        self.mock_db.Table.return_value = self.mock_table
        self.mock_db.batch_write_item.return_value = dict()
        aws().resource.return_value = self.mock_db

        # generate a default response to Table methods
        self.mock_table.query.return_value = dict(
            Count=1,
            Items=[{'timestamp': datetime.utcnow().isoformat()}]
        )
        self.mock_table.put_item.return_value = dict()
        self.mock_table.delete_item.return_value = '{}'
        self.aws = PSenseAWSInterface(testmode=True, debugmode=True)
        self.test_expid = '19A01A001F01-0001-001-00-G01CPVX'

    def test_logm(self):
        self.aws.debug = False
        self.assertFalse(self.aws.logm('info', 'test'))
        self.assertFalse(self.aws.logm('debug', 'test'))
        self.assertFalse(self.aws.logm('error', 'test'))
        self.aws.debug = True
        self.assertTrue(self.aws.logm('info', 'test'))
        self.assertTrue(self.aws.logm('debug', 'test'))
        self.assertTrue(self.aws.logm('error', 'test'))

    def test_set_query_config(self):
        self.aws.set_query_config(1, 2)
        self.assertEqual(self.aws.query_req_limit, 1)
        self.assertEqual(self.aws.query_req_count_limit, 2)

    def test_setget_expid(self):
        self.aws.set_experiment('asdf')
        self.assertEqual(self.aws.experiment_name, 'asdf')
        self.assertEqual(self.aws.get_experiment(), 'asdf')
        self.aws.set_experiment('')

    def test_verif_experiment(self):
        # experiment not verified if it is None
        self.assertFalse(self.aws.verif_experiment())
        self.assertTrue(self.aws.verif_experiment(self.test_expid))
        self.assertTrue(self.aws.exp_is_valid)
        self.assertEqual(self.aws.experiment_info['study']['start'], '2019-01-01')
        self.assertEqual(self.aws.experiment_info['sensor']['vsn'], '01')

    # @patch('boto3.session.Session.resource')
    def test_check_experiment_data(self):
        self.setUp()  # reinitialize

        self.aws.test_mode = True
        valid, isactive, vout = self.aws.check_experiment_data('test')
        self.assertEqual(valid, 'Yes')
        self.assertTrue(isactive)
        self.assertEqual(vout, -999)

        self.aws.test_mode = False
        self.mock_table.query.return_value = dict(
            Count=1,
            Items=[{'timestamp': datetime.utcnow().isoformat(), 'vout1': 1}]
        )
        valid, isactive, vout = self.aws.check_experiment_data('test')
        self.assertEqual(valid, 'Yes')
        self.assertTrue(isactive)
        self.assertEqual(vout, 1)

        self.mock_table.query.return_value = dict(
            Count=0,
            Items=[{'timestamp': (datetime.utcnow() - timedelta(days=1)).isoformat(), 'vout1': 2}]
        )
        valid, isactive, vout = self.aws.check_experiment_data('test')
        self.assertEqual(valid, 'No')
        self.assertFalse(isactive)
        self.assertEqual(vout, 0)

        self.aws.test_mode = True

    def test_add_experiment(self):
        self.setUp()  # reinitialize
        # fail if no expid
        self.assertRaises(AssertionError, self.aws.add_experiment)
        self.aws.set_experiment(self.test_expid)
        # fail if expid has not been verified
        self.assertRaises(AssertionError, self.aws.add_experiment)
        self.aws.verif_experiment()

        # if in testmode, return true
        self.aws.test_mode = True
        res, msg = self.aws.add_experiment()
        self.assertTrue(res)

        # not in test mode, we need to mock the response
        self.aws.test_mode = False

        # handle aws success, but experiment already exists
        self.mock_table.query.return_value = dict(
            Count=1,
            Items=[{'timestamp': datetime.utcnow().isoformat()}]
        )
        res, msg = self.aws.add_experiment()
        self.assertFalse(res)
        self.assertEqual(msg, 'exists')

        # handle aws success
        self.mock_table.query.return_value = dict(
            Count=0,
            Items=[]
        )
        res, msg = self.aws.add_experiment()
        self.assertTrue(res)
        self.assertEqual(msg, '')

        # handle aws failed
        self.mock_table.put_item.side_effect = Exception('Test')
        res, msg = self.aws.add_experiment()
        self.assertFalse(res)
        self.assertEqual(msg, 'error')

        self.aws.test_mode = True

    def test_add_sensordata(self):
        self.setUp()
        self.assertRaises(AssertionError, self.aws.add_sensordata)

        self.aws.verif_experiment(self.test_expid)

        self.aws.test_mode = True
        self.assertTrue(self.aws.add_sensordata(vout=[0], signal=[0]))
        self.assertTrue(self.aws.add_sensordata(signal=[1, 2]), True)

        self.aws.test_mode = False
        self.assertTrue(self.aws.add_sensordata(vout=[0], signal=[0]))
        self.mock_table.put_item.side_effect = Exception('Test')
        self.assertFalse(self.aws.add_sensordata(vout=[0], signal=[0]))
        self.aws.test_mode = True

    def test_generate_put_request(self):
        self.setUp()
        self.assertRaises(AssertionError, self.aws.generate_put_request, [])

        self.aws.verif_experiment(self.test_expid)
        check_timestamp = datetime.utcnow().isoformat()
        request = self.aws.generate_put_request([check_timestamp, 0.5, 0])['PutRequest']['Item']
        self.assertEqual(request['experiment'], self.test_expid)
        self.assertEqual(request['vout1'], Decimal(0.5))
        self.assertEqual(request['signal1'], Decimal(0))

        # try multi-channel data
        test_data = [check_timestamp, 0.5, 0, 1.5, 1]
        request = self.aws.generate_put_request(test_data)['PutRequest']['Item']
        self.assertEqual(request['experiment'], self.test_expid)
        self.assertEqual(request['timestamp'], check_timestamp)
        self.assertEqual(request['vout1'], Decimal(0.5))
        self.assertEqual(request['signal1'], Decimal(0))
        self.assertEqual(request['vout2'], Decimal(1.5))
        self.assertEqual(request['signal2'], Decimal(1))

    def test_add_bulk_sensordata(self):
        self.setUp()
        self.assertRaises(AssertionError, self.aws.add_bulk_sensordata, [])

        self.aws.verif_experiment(self.test_expid)

        data = [
            [datetime.utcnow().isoformat(), 1, .1],
            [datetime.utcnow(), 2, .2],
            [datetime.now(), 3, .3]
        ]

        self.aws.test_mode = True
        self.assertTrue(self.aws.add_bulk_sensordata(data))
        self.aws.test_mode = False
        self.assertTrue(self.aws.add_bulk_sensordata(data))
        self.mock_db.batch_write_item.side_effect = Exception('Test')
        self.assertFalse(self.aws.add_bulk_sensordata(data))
        self.aws.test_mode = True

    def test_get_experiments(self):
        self.setUp()
        self.mock_table.query.return_value = dict(
            Count=2,
            Items=[{'experiment': 'Experiment1'},
                   {'experiment': 'Experiment2'}]
        )
        ret = self.aws.get_experiments()
        self.assertTrue(isinstance(ret, list))
        self.assertEqual(ret[0], 'Experiment1')
        self.assertEqual(ret[1], 'Experiment2')
        self.mock_table.query.return_value = dict(
            Count=2,
            Items=[{'experiment': 'Experiment2'},
                   {'experiment': 'Experiment1'}]
        )
        self.assertEqual(ret[0], 'Experiment1')
        self.assertEqual(ret[1], 'Experiment2')

    def test_get_sensor_data(self):
        self.setUp()
        self.aws.verif_experiment(self.test_expid)
        check_timestamp = datetime.utcnow().isoformat()
        count, request = self.aws.get_sensor_data()
        self.assertEqual(count, 1)
        self.assertEqual(request['signal1'][0], 10)
        self.assertEqual(request['vout1'][0], 0.4)

        self.aws.test_mode = False
        self.mock_table.query.return_value = {
            'Count': 1,
            'Items': [{
                'experiment': self.test_expid,
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat('T'),
                'signal1': 10,
                'vout1': 0.4
            }]
        }
        count, request = self.aws.get_sensor_data()
        self.assertEqual(count, 1)
        self.assertEqual(request['signal1'][0], 10)
        self.assertEqual(request['vout1'][0], 0.4)

        self.aws.set_query_config(req_size=2, req_count=1)
        self.mock_table.query.return_value = {
            'Count': 2,
            'Items': [{
                'experiment': self.test_expid,
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat('T'),
                'signal1': 10,
                'vout1': 0.4
            }] * 2
        }
        count, request = self.aws.get_sensor_data()
        self.assertEqual(count, 2)
        self.assertEqual(request['signal1'][0], 10)
        self.assertEqual(request['vout1'][0], 0.4)

        self.aws.set_query_config(req_size=2, req_count=2)
        count, request = self.aws.get_sensor_data()
        self.assertEqual(count, 4)
        self.assertEqual(request['signal1'][0], 10)
        self.assertEqual(request['vout1'][0], 0.4)

        self.aws.set_query_config(req_size=2, req_count=3)
        self.mock_table.query.side_effect = [
            {
                'Count': 2,
                'Items': [{
                    'experiment': self.test_expid,
                    'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat('T'),
                    'signal1': 10,
                    'vout1': 0.4
                }] * 2
            },
            {
                'Count': 2,
                'Items': [{
                    'experiment': self.test_expid,
                    'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat('T'),
                    'signal1': 10,
                    'vout1': 0.4
                }] * 2
            },
            {
                'Count': 1,
                'Items': [{
                    'experiment': self.test_expid,
                    'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat('T'),
                    'signal1': 5,
                    'vout1': .1
                }]
            }
        ]
        count, request = self.aws.get_sensor_data()
        self.assertEqual(count, 5)
        self.assertEqual(request['signal1'][0], 10)
        self.assertEqual(request['vout1'][0], 0.4)
        self.assertEqual(request['signal1'][-1], 5)
        self.assertEqual(request['vout1'][-1], 0.1)

        self.aws.test_mode = True

    def test_get_sensordata_slice(self):
        self.setUp()
        self.aws.verif_experiment(self.test_expid)
        check_timestamp = datetime.utcnow().isoformat()

        self.aws.test_mode = True
        count, request = self.aws.get_sensordata_slice(check_timestamp, 5)
        self.assertEqual(count, 1)
        self.assertEqual(request['signal1'][0], 5)
        self.assertEqual(request['vout1'][0], 0.2)

        self.aws.test_mode = False
        self.mock_table.query.return_value = {
            'Count': 1,
            'Items': [{
                'experiment': self.test_expid,
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat('T'),
                'signal1': 6,
                'vout1': 0.3
            }]
        }
        count, request = self.aws.get_sensordata_slice(check_timestamp, 5)
        self.assertEqual(count, 1)
        self.assertEqual(request['signal1'][0], 6)
        self.assertEqual(request['vout1'][0], 0.3)

        self.mock_table.query.return_value = {
            'Count': 3,
            'Items': [{
                'experiment': self.test_expid,
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat('T'),
                'signal1': 10,
                'vout1': 0.4
            }] * 3
        }
        count, request = self.aws.get_sensordata_slice(check_timestamp, 5)
        self.assertEqual(count, 3)

        self.mock_table.query.return_value = {
            'Count': 0,
            'Items': []
        }
        count, request = self.aws.get_sensordata_slice(check_timestamp, 5)
        self.assertEqual(count, 0)

        self.aws.test_mode = True

    def test_get_event_data(self):
        self.setUp()
        self.aws.set_experiment(self.test_expid)
        self.assertRaises(AssertionError, self.aws.get_event_data)
        self.aws.verif_experiment()

        check_timestamp = datetime.utcnow().isoformat()

        self.aws.test_mode = True
        self.assertEqual(len(self.aws.get_event_data()), 1)

    def test_add_event(self):
        self.setUp()
        self.aws.set_experiment(self.test_expid)
        self.assertRaises(AssertionError, self.aws.add_event, 0, '', '', 0, 0)
        self.aws.verif_experiment()
        self.assertRaises(AssertionError, self.aws.add_event, 0, '', 'not-a-real-type', 0, 0)

        self.aws.test_mode = True
        self.assertTrue(self.aws.add_event(0, datetime.now(), 'Lactate', 0, 0))
        self.assertTrue(self.aws.add_event(0, datetime.utcnow().isoformat(), 'Lactate', 0, 0))

    def test_delete_event(self):
        self.setUp()
        self.aws.set_experiment(self.test_expid)
        self.assertRaises(AssertionError, self.aws.delete_event, 0, '', '')
        self.aws.verif_experiment()
        self.assertRaises(AssertionError, self.aws.delete_event, 0, '', 'not-a-real-type')
        self.aws.test_mode = True
        self.assertTrue(self.aws.delete_event(0, datetime.now(), 'Lactate'))
        self.assertTrue(self.aws.delete_event(0, datetime.utcnow().isoformat(), 'Lactate'))
        self.aws.test_mode = False
        self.assertEqual(self.aws.delete_event(0, datetime.now(), 'Lactate'), dict())
        self.aws.test_mode = True


if __name__ == '__main__':
    unittest.main()
