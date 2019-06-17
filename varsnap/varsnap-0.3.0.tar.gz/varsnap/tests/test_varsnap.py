import json
import os
import unittest
from unittest.mock import patch, MagicMock

from varsnap import core


class EnvVar(unittest.TestCase):
    def setUp(self):
        self.orig_varsnap = os.environ.get(core.ENV_VARSNAP, '')
        self.orig_env = os.environ.get(core.ENV_ENV, '')
        self.orig_auth_token = os.environ.get(core.ENV_AUTH_TOKEN, '')

    def tearDown(self):
        os.environ[core.ENV_VARSNAP] = self.orig_varsnap
        os.environ[core.ENV_ENV] = self.orig_env
        os.environ[core.ENV_AUTH_TOKEN] = self.orig_auth_token


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


class TestProducer(EnvVar):
    def setUp(self):
        super().setUp()
        os.environ[core.ENV_VARSNAP] = 'true'
        os.environ[core.ENV_ENV] = 'production'
        os.environ[core.ENV_AUTH_TOKEN] = 'asdf'

    def test_is_enabled(self):
        self.assertTrue(core.Producer.is_enabled())

        os.environ[core.ENV_VARSNAP] = 'false'
        self.assertFalse(core.Producer.is_enabled())
        os.environ[core.ENV_VARSNAP] = 'true'

        os.environ[core.ENV_ENV] = 'development'
        self.assertFalse(core.Producer.is_enabled())
        os.environ[core.ENV_ENV] = 'production'

        os.environ[core.ENV_AUTH_TOKEN] = ''
        self.assertFalse(core.Producer.is_enabled())
        os.environ[core.ENV_AUTH_TOKEN] = 'asdf'

    def test_serialize(self):
        data = core.Producer.serialize('abcd')
        self.assertGreater(len(data), 0)

    @patch('requests.post')
    def test_produce_not_enabled(self, mock_post):
        os.environ[core.ENV_VARSNAP] = 'false'
        core.Producer.produce('a', 'b', 'c')
        self.assertFalse(mock_post.called)

    @patch('requests.post')
    def test_produce(self, mock_post):
        core.Producer.produce('a', 'b', 'c')
        self.assertEqual(mock_post.call_args[0][0], core.ADD_SNAP_URL)
        data = mock_post.call_args[1]['data']
        self.assertEqual(data['auth_token'], 'asdf')
        self.assertIn('inputs', data)
        self.assertIn('prod_outputs', data)


class TestConsumer(EnvVar):
    def setUp(self):
        super().setUp()
        os.environ[core.ENV_VARSNAP] = 'true'
        os.environ[core.ENV_ENV] = 'development'
        os.environ[core.ENV_AUTH_TOKEN] = 'asdf'

    def test_is_enabled(self):
        self.assertTrue(core.Consumer.is_enabled())

        os.environ[core.ENV_VARSNAP] = 'false'
        self.assertFalse(core.Consumer.is_enabled())
        os.environ[core.ENV_VARSNAP] = 'true'

        os.environ[core.ENV_ENV] = 'production'
        self.assertFalse(core.Consumer.is_enabled())
        os.environ[core.ENV_ENV] = 'development'

        os.environ[core.ENV_AUTH_TOKEN] = ''
        self.assertFalse(core.Consumer.is_enabled())
        os.environ[core.ENV_AUTH_TOKEN] = 'asdf'

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
        core.Consumer.consume(MagicMock)
        self.assertFalse(mock_post.called)

    @patch('requests.post')
    def test_consume_empty(self, mock_post):
        mock_post.side_effect = [MagicMock(content='')]
        mock_func = MagicMock()
        with self.assertRaises(StopIteration):
            core.Consumer.consume(mock_func)
        self.assertFalse(mock_func.called)

    @patch('requests.post')
    def test_consume(self, mock_post):
        data = {
            'id': 'abcd',
            'inputs': core.Producer.serialize(((2,), {})),
            'prod_outputs': core.Producer.serialize((4,)),
        }
        data = json.dumps(data)
        mock_post.side_effect = [MagicMock(content=data)]
        mock_func = MagicMock()
        with self.assertRaises(StopIteration):
            core.Consumer.consume(mock_func)
        self.assertEqual(mock_func.call_count, 1)
        self.assertEqual(mock_func.call_args[0][0], 2)

    @patch('requests.post')
    def test_consume_deduplicates(self, mock_post):
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
        mock_func = MagicMock()
        with self.assertRaises(StopIteration):
            core.Consumer.consume(mock_func)
        self.assertEqual(mock_func.call_count, 1)


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
