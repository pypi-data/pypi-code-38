# -*- coding: utf-8 -*-
import datetime
import json
import logging
import time

import six

from ...data_management.http_session import create_http_session
from .json_encoder import MissingLinkJsonEncoder

KEEP_ALIVE_EVENT = 'KEEP_ALIVE'


def chart_name_to_id(chart_name):
    from hashlib import sha256
    return sha256(six.text_type(chart_name).encode('utf-8').lower().strip()).hexdigest()


class LoggerRequestsDispatcher(object):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger()
        self.logger.addHandler(logging.StreamHandler())

        self.logger.info('got init %s %s', args, kwargs)

    def create_new_experiment(self, *args, **kwargs):
        self.logger.info('got create_new_experiment %s %s', args, kwargs)

    def send_commands(self, *args, **kwargs):
        self.logger.info('got send_commands %s %s', args, kwargs)


class PostRequests(object):
    retry_interval = 1
    max_retries = 3

    def __init__(self, owner_id, project_token, host, stoppable=False):
        host = host or 'https://missinglinkai.appspot.com'

        self.logger = logging.getLogger('missinglink')

        self.owner_id = owner_id
        self.project_token = project_token
        self.experiment_token = None
        self.host = host
        self.packet_sequence = 0
        self.stoppable = stoppable
        self.stopped = False
        self.project_id = None
        self.experiment_id = None
        self.session = create_http_session()
        self.__allow_source_tracking = True

    def send_chart(self, name, x_values, y_values, x_legend=None, y_legends=None, scope='test', type='line', experiment_id=None, model_weights_hash=None, throw_exceptions=False):
        """
        Send experiment external chart to an experiment. The experiment can be identified by its ID (experiment_id) or by model_weights_hash in the experiment. Exactly one of experiment_id or model_weights_hash must be provided
        :param name: The name of the chart. The name is used in order to identify the chart against different experiments and through the same experiment.
        :param x_values: Array of `m` Strings / Ints / Floats  -  X axis points.
        :param y_values: Array/Matrix of `m` Y axis points. Can be either array `m` of Integers/Floats or a matrix (having `n` Ints/Floats each), a full matrix describing the values of every y chart in every data point.
        :param x_legend: String, Legend for the X axis
        :param y_legends: String/Array of `n` Strings legend of the Y axis chart(s)
        :param scope: Scope type. Can be 'test', 'validation' or 'train', defaults to 'test'
        :param type: Chart type, currently only 'line' is supported.
        :param experiment_id: The id of the target experiment.
        :param model_weights_hash: a hexadecimal sha1 hash of the model's weights.

        :param throw_exceptions:
        :return:
        """
        chart_id = chart_name_to_id(name)

        def _read_norm_y_values(ys):
            res = []
            dimension_count = None

            for y in ys:
                if not isinstance(y, (list, tuple)):
                    y = [y]

                cur_dim = len(y)
                dimension_count = dimension_count or cur_dim
                if dimension_count != cur_dim:
                    raise Exception("All of the data values arrays must be of the same size")

                res.append(y)

            return res

        def _read_norm_x_values(xs):
            res = []
            for type in [float, six.integer_types, six.string_types]:
                for x in xs:
                    if not isinstance(x, type):
                        res = []
                        break
                    res.append(x)
                if len(res) == len(xs):
                    return res
            raise Exception('X values must be consistent')

        def _read_norm_legen_values(x_leg, y_leg):

            if not isinstance(y_leg, (list, tuple)):
                y_leg = [y_leg]
            return [x_leg] + y_leg

        if (experiment_id is None) == (model_weights_hash is None):  # XOR
            raise Exception("Please provide experiment_id or model_weights_hash")
        x = _read_norm_x_values(x_values)
        y = _read_norm_y_values(y_values)
        legends = _read_norm_legen_values(x_legend, y_legends)
        params = {
            'experiment_id': experiment_id,
            'model_weights_hash': model_weights_hash,
            'name': name,
            'scope': scope,
            'chart': type,
            'legends': legends,
            'x': x,
            'y': y
        }
        return self._post_and_retry('/callback/external_chart/{}'.format(chart_id), params, throw_exceptions=throw_exceptions)

    @classmethod
    def _prefix_external_metrics(cls, metrics):
        res = {}
        for k, v in metrics.items():
            key_name = k if k.startswith('ex_') else 'ex_{}'.format(k)
            res[key_name] = v
        return res

    @classmethod
    def _build_and_validate_metrics(cls, metrics):
        if isinstance(metrics, tuple):
            metrics = {metrics[0]: metrics[1]}

        if not isinstance(metrics, dict):
            raise AttributeError('`metrics can be only dict or (key,value) tuple')
        return cls._prefix_external_metrics(metrics)

    def update_metrics(self, metrics, experiment_id=None, model_weights_hash=None, throw_exceptions=False):
        if (experiment_id is None) == (model_weights_hash is None):  # XOR
            raise Exception("Please provide experiment_id or model_weights_hash")
        params = {
            'experiment_id': experiment_id,
            'model_weights_hash': model_weights_hash,
            'metrics': self._build_and_validate_metrics(metrics),
        }
        return self._post_and_retry('/callback/external_metrics', params, throw_exceptions=throw_exceptions)

    def update_metrics_per_iteration(self, metrics, model_weights_hash, throw_exceptions=False):
        if model_weights_hash is None:
            raise Exception("`model_weights_hash` is missing")
        params = {
            'model_weights_hash': model_weights_hash,
            'metrics': self._build_and_validate_metrics(metrics),
        }
        return self._post_and_retry('/callback/external_model_metrics', params, throw_exceptions=throw_exceptions)

    def send_commands(self, commands, throw_exceptions=False):
        if self.experiment_token is None:
            self.logger.debug('create experiment failed or not called')
            return {}

        self.packet_sequence += 1

        params = {
            'cmds': commands,
            'token': self.experiment_token,
            'sequence': self.packet_sequence,
        }

        return self._post_and_retry('/callback/step', params, throw_exceptions=throw_exceptions)

    def send_images(self, data):
        data['project_token'] = self.project_token

        return self._post_and_retry('/callback/images', data)

    def send_keep_alive(self):
        keep_alive_cmd = (KEEP_ALIVE_EVENT, None, datetime.datetime.utcnow().isoformat())
        params = {
            'cmds': [keep_alive_cmd],
            'token': self.experiment_token,
        }

        return self._post_and_retry('/callback/step', params)

    def call_new_experiment(self, params, throw_exceptions=None):
        if throw_exceptions is None:
            throw_exceptions = True

        res = self._post_and_retry('/callback/step/begin', params, throw_exceptions=throw_exceptions)

        return res or {}

    def create_new_experiment(self, keep_alive_interval, throw_exceptions=None, resume_token=None, resource_management=None):
        self.logger.info(
            'create new experiment for owner (%s), keep alive interval (%s) seconds',
            self.owner_id, keep_alive_interval)

        params = {
            'owner_id': self.owner_id,
            'token': self.project_token,
            'keep_alive': keep_alive_interval,
            'stoppable': self.stoppable,
        }

        if resume_token:
            params['resume_token'] = resume_token
        if resource_management:
            params['resource_management'] = resource_management
        res = self.call_new_experiment(params, throw_exceptions)

        self.experiment_token = res.get('token')
        self.project_id = res.get('project_id')
        self.experiment_id = res.get('experiment_id')
        self.__allow_source_tracking = res.get('allow_source_tracking', self.__allow_source_tracking)

        return res

    @property
    def allow_source_tracking(self):
        return self.__allow_source_tracking

    def _post_and_retry(self, endpoint, json_dictionary, throw_exceptions=False):
        headers = {'content-type': 'application/json'}
        data = json.dumps(json_dictionary, cls=MissingLinkJsonEncoder, sort_keys=True)

        if self.project_id is not None:
            params = {'project_id': self.project_id, 'experiment_id': self.experiment_id}
        else:
            params = {'owner_id': self.owner_id, 'project_token': self.project_token}

        self.logger.debug('post data. len: (%s) params (%s)', len(data), ','.join(json_dictionary.keys()))

        url = self.host + endpoint

        last_error = None

        for _ in range(self.max_retries):
            try:
                res = self.session.post(url, data=data, params=params, headers=headers)
                self.logger.debug("Got response from server with status %s", res.status_code)
                res.raise_for_status()

                result = json.loads(res.text)

                return result
            except Exception as e:
                if throw_exceptions:
                    raise

                self.logger.exception('failed to send missinglink request')
                last_error = e

            time.sleep(self.retry_interval)

        print('failed to communicate with missinglink server')
        print(last_error)

        self.logger.warning(
            'failed to communicate with missinglink server:\n%s\n', last_error)

        return {}


def get_post_requests(owner_id, project_token, host=None, on_create_dispatcher=None):
    def default_create_dispatch():
        return PostRequests(owner_id, project_token, host)

    on_create_dispatcher = on_create_dispatcher or default_create_dispatch

    return on_create_dispatcher()


def post_requests_for_experiment(owner_id, project_token, host=None, stoppable=False, requests_dispatcher=None):
    requests_dispatcher = requests_dispatcher or PostRequests

    def create_for_experiment():
        return requests_dispatcher(owner_id, project_token, host, stoppable=stoppable)

    return get_post_requests(owner_id, project_token, host, on_create_dispatcher=create_for_experiment)
