import json
import os
import unittest
from unittest.mock import patch, MagicMock

from varsnap import core
from varsnap.__version__ import __version__


class EnvVar(unittest.TestCase):
    def setUp(self):
        self.orig_varsnap = os.environ.get(core.ENV_VARSNAP, '')
        self.orig_env = os.environ.get(core.ENV_ENV, '')
        self.orig_producer_token = os.environ.get(core.ENV_PRODUCER_TOKEN, '')
        self.orig_consumer_token = os.environ.get(core.ENV_CONSUMER_TOKEN, '')

    def tearDown(self):
        os.environ[core.ENV_VARSNAP] = self.orig_varsnap
        os.environ[core.ENV_ENV] = self.orig_env
        os.environ[core.ENV_PRODUCER_TOKEN] = self.orig_producer_token
        os.environ[core.ENV_CONSUMER_TOKEN] = self.orig_consumer_token


class TestEnvVar(EnvVar):
    def test_env_var(self):
        os.environ[core.ENV_VARSNAP] = 'true'
        env = core.env_var(core.ENV_VARSNAP)
        self.assertEqual(env, 'true')

    def test_downcases_env_var(self):
        os.environ[core.ENV_VARSNAP] = 'TRUE'
        env = core.env_var(core.ENV_VARSNAP)
        self.assertEqual(env, 'true')

    def test_unset_var(self):
        del os.environ[core.ENV_VARSNAP]
        env = core.env_var(core.ENV_VARSNAP)
        self.assertEqual(env, '')


class TestGetSignature(unittest.TestCase):
    def assertEqualVersion(self, signature, expected):
        self.assertEqual(signature, expected % __version__)

    def test_standalone_func(self):
        signature = core.get_signature(core.env_var)
        self.assertEqualVersion(signature, 'python.%s.env_var')

    def test_class_func(self):
        signature = core.get_signature(core.Producer.serialize)
        self.assertEqualVersion(signature, 'python.%s.Producer.serialize')

    def test_instance_func(self):
        signature = core.get_signature(core.Producer.__init__)
        self.assertEqualVersion(signature, 'python.%s.Producer.__init__')


class TestProducer(EnvVar):
    def setUp(self):
        super().setUp()
        os.environ[core.ENV_VARSNAP] = 'true'
        os.environ[core.ENV_ENV] = 'production'
        os.environ[core.ENV_PRODUCER_TOKEN] = 'asdf'

        self.producer = core.Producer(core.env_var)

    def test_init(self):
        target_func = MagicMock()
        producer = core.Producer(target_func)
        self.assertEquals(producer.target_func, target_func)

    def test_is_enabled(self):
        self.assertTrue(core.Producer.is_enabled())

        os.environ[core.ENV_VARSNAP] = 'false'
        self.assertFalse(core.Producer.is_enabled())
        os.environ[core.ENV_VARSNAP] = 'true'

        os.environ[core.ENV_ENV] = 'development'
        self.assertFalse(core.Producer.is_enabled())
        os.environ[core.ENV_ENV] = 'production'

        os.environ[core.ENV_PRODUCER_TOKEN] = ''
        self.assertFalse(core.Producer.is_enabled())
        os.environ[core.ENV_PRODUCER_TOKEN] = 'asdf'

    def test_serialize(self):
        data = core.Producer.serialize('abcd')
        self.assertGreater(len(data), 0)

    @patch('requests.post')
    def test_produce_not_enabled(self, mock_post):
        os.environ[core.ENV_VARSNAP] = 'false'
        self.producer.produce('a', 'b', 'c')
        self.assertFalse(mock_post.called)

    @patch('requests.post')
    def test_produce(self, mock_post):
        self.producer.produce('a', 'b', 'c')
        self.assertEqual(mock_post.call_args[0][0], core.PRODUCE_SNAP_URL)
        data = mock_post.call_args[1]['data']
        self.assertEqual(data['producer_token'], 'asdf')
        self.assertEqual(data['signature'], core.get_signature(core.env_var))
        self.assertIn('inputs', data)
        self.assertIn('prod_outputs', data)


class TestConsumer(EnvVar):
    def setUp(self):
        super().setUp()
        os.environ[core.ENV_VARSNAP] = 'true'
        os.environ[core.ENV_ENV] = 'development'
        os.environ[core.ENV_CONSUMER_TOKEN] = 'asdf'

        self.target_func = MagicMock()
        self.consumer = core.Consumer(self.target_func)

    def test_init(self):
        target_func = MagicMock()
        producer = core.Consumer(target_func)
        self.assertEquals(producer.target_func, target_func)

    def test_is_enabled(self):
        self.assertTrue(core.Consumer.is_enabled())

        os.environ[core.ENV_VARSNAP] = 'false'
        self.assertFalse(core.Consumer.is_enabled())
        os.environ[core.ENV_VARSNAP] = 'true'

        os.environ[core.ENV_ENV] = 'production'
        self.assertFalse(core.Consumer.is_enabled())
        os.environ[core.ENV_ENV] = 'development'

        os.environ[core.ENV_CONSUMER_TOKEN] = ''
        self.assertFalse(core.Consumer.is_enabled())
        os.environ[core.ENV_CONSUMER_TOKEN] = 'asdf'

    def test_deserialize(self):
        data = core.Producer.serialize('abcd')
        output = core.Consumer.deserialize(data)
        self.assertEqual(output, 'abcd')

        data = core.Producer.serialize(EnvVar)
        output = core.Consumer.deserialize(data)
        self.assertEqual(output, EnvVar)

    @patch('requests.post')
    def test_consume_not_enabled(self, mock_post):
        os.environ[core.ENV_VARSNAP] = 'false'
        self.consumer.consume()
        self.assertFalse(mock_post.called)

    @patch('varsnap.core.qualname')
    @patch('requests.post')
    def test_consume_empty(self, mock_post, mock_qualname):
        mock_qualname.return_value = 'magicmock'
        mock_post.side_effect = [MagicMock(content='')]
        with self.assertRaises(StopIteration):
            self.consumer.consume()
        self.assertFalse(self.target_func.called)

    @patch('varsnap.core.qualname')
    @patch('requests.post')
    def test_consume(self, mock_post, mock_qualname):
        mock_qualname.return_value = 'magicmock'
        data = {
            'id': 'abcd',
            'inputs': core.Producer.serialize(((2,), {})),
            'prod_outputs': core.Producer.serialize((4,)),
        }
        data = json.dumps(data)
        mock_post.side_effect = [MagicMock(content=data)]
        with self.assertRaises(StopIteration):
            self.consumer.consume()
        self.assertEqual(self.target_func.call_count, 1)
        self.assertEqual(self.target_func.call_args[0][0], 2)
        data = mock_post.call_args[1]['data']
        self.assertEqual(data['consumer_token'], 'asdf')
        self.assertEqual(data['signature'], core.get_signature(core.env_var))

    @patch('varsnap.core.qualname')
    @patch('requests.post')
    def test_consume_deduplicates(self, mock_post, mock_qualname):
        mock_qualname.return_value = 'magicmock'
        data = {
            'id': 'abcd',
            'inputs': core.Producer.serialize(((2,), {})),
            'prod_outputs': core.Producer.serialize((4,)),
        }
        data = json.dumps(data)
        mock_post.side_effect = [
            MagicMock(content=data),
            MagicMock(content=data),
        ]
        with self.assertRaises(StopIteration):
            self.consumer.consume()
        self.assertEqual(self.target_func.call_count, 1)

    @patch('varsnap.core.qualname')
    @patch('requests.post')
    def test_consume_catches_exceptions(self, mock_post, mock_qualname):
        mock_qualname.return_value = 'magicmock'
        data = {
            'id': 'abcd',
            'inputs': core.Producer.serialize(((2,), {})),
            'prod_outputs': core.Producer.serialize((4,)),
        }
        data = json.dumps(data)
        mock_post.side_effect = [
            MagicMock(content=data),
        ]
        self.target_func.side_effect = ValueError('asdf')
        with self.assertRaises(StopIteration):
            self.consumer.consume()
        self.assertEqual(self.target_func.call_count, 1)


class TestVarsnap(EnvVar):
    @patch('requests.post')
    def test_no_op(self, mock_post):
        os.environ[core.ENV_VARSNAP] = 'false'
        mock_func = core.varsnap(MagicMock())
        mock_func(1)
        self.assertFalse(mock_post.called)

    @patch('varsnap.core.Consumer.consume')
    @patch('varsnap.core.Producer.produce')
    def test_consume(self, mock_produce, mock_consume):
        mock_func = MagicMock()
        mock_func.return_value = 2
        varsnap_mock_func = core.varsnap(mock_func)
        result = varsnap_mock_func(1)
        self.assertEqual(result, 2)
        self.assertEqual(mock_func.call_count, 1)
        self.assertEqual(mock_consume.call_count, 1)
        self.assertEqual(mock_produce.call_count, 1)
        self.assertEqual(mock_produce.call_args[0][2], 2)

    @patch('varsnap.core.Consumer.consume')
    @patch('varsnap.core.Producer.produce')
    def test_consume_exception(self, mock_produce, mock_consume):
        mock_func = MagicMock()
        mock_func.side_effect = ValueError('asdf')
        varsnap_mock_func = core.varsnap(mock_func)
        with self.assertRaises(ValueError):
            varsnap_mock_func(1)
        self.assertEqual(mock_func.call_count, 1)
        self.assertEqual(mock_consume.call_count, 1)
        self.assertEqual(mock_produce.call_count, 1)
        self.assertEqual(str(mock_produce.call_args[0][2]), 'asdf')
