# -*- coding: utf-8 -*-
from collections import defaultdict
import copy
import datetime
import hashlib
import logging
import os
import platform
import random
import uuid
import warnings
import numpy as np

from .data_generator_factory import MLDataGeneratorFactory
from .queries import QueriesStore
from .phase import Phase, PhaseTest, PhaseEpoch
from .auth_params import AuthParams
from .base_callback_images import BaseCallbackImages
from .ml_env_vars import MlEnvironmentVariables
from .exceptions import ExperimentStopped
from .exceptions import MissingLinkException
from .logger_wrapper import LoggerWrapper
from .settings import EventTypes, HyperParamTypes, MetricPhasePrefixes
from .utilities.source_tracking import GitRepoSyncer
from contextlib import contextmanager


class AverageMetric(object):
    def __init__(self, metric, old_metric=None):
        if not old_metric:
            self.count = 1
            self.value = float(metric)
        else:
            self.count = old_metric.count + 1
            self.value = old_metric.value * (float(old_metric.count) / self.count) + float(metric) / self.count

    def to_json(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, AverageMetric):
            return self.value == other.value and self.count == other.count

        rel_tol = 1e-09
        abs_tol = 0.0
        return abs(self.value - other) <= max(rel_tol * max(abs(self.value), abs(other)), abs_tol)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.value)


class BaseCallback(BaseCallbackImages):
    _DISPATCH_INTERVAL = 5
    _MAX_BATCHES_PER_EPOCH = 1000
    _SEND_EPOCH_CANDIDATES = False
    _FIRST_ITERATION = 1
    _WEIGHTS_HASH_PREFIX = 'v1_'
    _COMPUTED_METRICS_METHODS = {
        'max': max,
        'min': min,
        'avg': AverageMetric
    }
    _TRACKED_SPECIAL = {
        'max',
        'min'
    }

    SHOULD_USE_INFINITE_GENERATOR = False

    def __init__(self, owner_id=None, project_token=None, stopped_callback=None, framework='none', **kwargs):
        from missinglink_kernel import get_version

        self.logger = LoggerWrapper()
        stoppable = True
        project_id = kwargs.pop('project', kwargs.pop('project_id', None))

        self._config_prefix = self._prop_from_env_or_data('config_prefix', 'ML_CONFIG_PREFIX', kwargs)
        resume_token = kwargs.pop('resume_token', None)

        kwargs_host = kwargs.pop('host', None)
        owner_id, project_token, host = self._validate_auth_params(
            owner_id=owner_id, project_token=project_token,
            project_id=project_id, host=kwargs_host)

        self.experiment_args = {
            'owner_id': owner_id,
            'project_token': project_token,
            'host': host,
            'stoppable': stoppable,
        }

        self._requests_dispatcher = kwargs.pop('requests_dispatcher', None)

        if stopped_callback and not callable(stopped_callback):
            self.logger.warning('stopped_callback is not callable, will be ignored')
            stopped_callback = None

        self.stopped_callback = stopped_callback
        self.rm_properties = MlEnvironmentVariables.get_rm_env()
        self.properties = {
            'env': {
                'framework': framework,
                'missinglink_version': get_version(),
                'node': platform.node(),
                'platform': platform.platform(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
            },
            'source_tracking': {
                'error': 'disabled'
            },
            'callback_tag': self.generate_tag(),
            'stoppable': stoppable,
        }

        self._update_properties = True

        if resume_token is not None:
            self.properties['resume_token'] = resume_token

        self._post_requests = None

        self.batches_queue = []
        self.points_candidate_indices = {}
        self._batch_special_points = {}  # Batch points that we don't want to drop out
        self._epoch_special_points = {}  # Epoch points that we don't want to drop out
        self.iteration = 0
        self._test_iteration = 0
        self.ts_start = 0
        self.epoch_addition = 0
        self.has_ended = False
        self.tests_counter = 0
        self.stopped = False
        self.dispatch_interval = self._DISPATCH_INTERVAL
        self._found_classes = None
        self._has_test_context = False
        self._test_iter = -1
        self._test_iteration_count = 0
        self._test_token = None
        self._class_mapping = None
        self._latest_metrics = {}
        self._computed_metrics = defaultdict(dict)
        self._queries = QueriesStore()

        self._set_experiment_query_from_resource_management()

        if self._SEND_EPOCH_CANDIDATES:
            self.epoch_candidate_indices = {}

        warnings.filterwarnings("once", "was not able to get variable.*")
        warnings.filterwarnings("once", "skipped MissingLinkJsonEncoder because of TypeError")

    @classmethod
    def _prop_from_env_or_data(cls, name, env_name, params):
        return os.environ.get(env_name, params.get(name))

    @classmethod
    def get_batch_sampling_size(cls):
        _BATCH_SAMPLING_SIZE = 1000
        return _BATCH_SAMPLING_SIZE

    @classmethod
    def get_epoch_sampling_size(cls):
        _EPOCH_SAMPLING_SIZE = 5000
        return _EPOCH_SAMPLING_SIZE

    def _validate_auth_params(self, owner_id, project_token, project_id, host):
        ml_env = MlEnvironmentVariables.get_ml_env()
        owner_id = ml_env.get('ML_OWNER_ID', owner_id)
        project_token = ml_env.get('ML_PROJECT_TOKEN', project_token)
        host = ml_env.get('ML_API_HOST', host)

        auth_params = AuthParams(config_prefix=self._config_prefix)

        if owner_id is None:
            owner_id = auth_params.get_user_id()

        if project_token is None:
            project_token = auth_params.get_project_token(project_id)

        if host is None:
            host = auth_params.api_host

        if owner_id is None:
            raise ValueError('owner id is not provided and `ML_OWNER_ID` environment variable not present')

        if project_token is None:
            raise ValueError('project token is not provided and `ML_OWNER_ID` environment variable not present')

        return owner_id, project_token, host

    @property
    def rm_data_iterator_settings(self):
        rm_data = self.rm_properties.get('data', {})
        if rm_data.get('use_iterator', 'false').lower() != 'true':
            return None

        return rm_data['volume'], rm_data['query']

    @property
    def rm_active(self):
        return self.rm_properties is not None and self.rm_properties.get('in_context', '').lower() == 'true'

    def _set_experiment_query_from_resource_management(self):
        resource_management = self.rm_properties
        if resource_management is None:
            return

        query_data = resource_management.get('data') or {}
        if 'volume' not in query_data or 'query' not in query_data:
            return

        query = query_data['query']
        volume_id = query_data['volume']
        self._queries.add_query(query, volume_id)

        self._install_needed_dependencies(volume_id)

        return self._set_experiment_queries()

    def _set_experiment_queries(self):
        self.properties['data_management'] = self._queries.get_all()
        return self.properties['data_management']

    def _get_volume_bucket_moniker(self, volume_id):
        from ..data_management.query_data_generator import QueryDataGenerator
        from missinglink.legit.data_volume import with_repo_dynamic
        from missinglink.legit.gcs_utils import gcs_moniker
        from missinglink.legit.path_utils import get_moniker

        ctx = QueryDataGenerator.build_context(config_prefix=self._config_prefix)

        with with_repo_dynamic(ctx, volume_id) as repo:
            bucket_name = repo.data_volume_config.object_store_config.get('bucket_name', '')

            return get_moniker(bucket_name, gcs_moniker)

    def _install_needed_dependencies(self, volume_id):
        s3_moniker = 's3://'

        from missinglink_kernel.data_management.dynamic_import import install_dependencies, COMMON_DEPENDENCIES, S3_DEPENDENCIES, GCS_DEPENDENCIES

        install_dependencies(COMMON_DEPENDENCIES)

        local_dependencies = []

        if self._get_volume_bucket_moniker(volume_id) == s3_moniker:
            local_dependencies.extend(S3_DEPENDENCIES)
        else:
            local_dependencies.extend(GCS_DEPENDENCIES)

        install_dependencies(local_dependencies)

    def get_data_generator(
            self, query, data_callback,
            volume_id=None, cache_directory=None, batch_size=32, use_threads=None, processes=-1, shuffle=True, cache_limit=None, drop_last=False, disable_caching=False, is_infinite=True):

        ml_data_generator = MLDataGeneratorFactory(query=query, data_callback=data_callback, volume_id=volume_id,
                                                   cache_directory=cache_directory, batch_size=batch_size,
                                                   use_threads=use_threads, processes=processes, shuffle=shuffle,
                                                   cache_limit=cache_limit, drop_last=drop_last,
                                                   disable_caching=disable_caching, is_infinite=is_infinite).create()

        ml_data_generator.set_config_prefix(self._config_prefix)

        volume_id = ml_data_generator.volume_id
        self._install_needed_dependencies(volume_id)
        self._queries.add_query(query, volume_id)
        self._set_experiment_queries()

        return ml_data_generator

    def bind_data_generator(
            self, volume_id, query, data_callback,
            cache_directory=None, batch_size=32, use_threads=None, processes=-1, shuffle=True, cache_limit=None, drop_last=False, disable_caching=False, is_infinite=True):

        return self.get_data_generator(
            query, data_callback, volume_id, cache_directory, batch_size, use_threads, processes, shuffle, cache_limit, drop_last, disable_caching,
            is_infinite=is_infinite)

    def bind_framework_data_generator(self, volume_id, query, data_callback, cache_directory=None, batch_size=32,
                                      use_threads=None, processes=-1, shuffle=True, cache_limit=None, drop_last=False,
                                      disable_caching=False, is_infinite=None):
        """
        This method initiates the data generator with configurations that are suitable for the framework,
        in order to avoid breaking changes to `bind_data_generator` and `get_data_generator`.
        In this stage, it will set is_infinite according to the default behavior of the framework.
        """

        is_infinite = self._should_use_infinite_generator(is_infinite)

        return self.get_data_generator(
            query, data_callback, volume_id, cache_directory, batch_size, use_threads, processes, shuffle, cache_limit,
            drop_last, disable_caching, is_infinite=is_infinite)

    def _should_use_infinite_generator(self, is_infinite):
        return self.SHOULD_USE_INFINITE_GENERATOR if is_infinite is None else is_infinite

    def get_query_objects(self):
        return self._queries.get_all_query_obj()

    @property
    def _is_first_iteration(self):
        return self.iteration == 1

    def _update_test_token(self):
        self._test_token = uuid.uuid4().hex

    def close(self):
        if self._post_requests is not None:
            self._post_requests.close()

        if self.logger is not None:
            self.logger.close()

    def __set_properties_names(self, **kwargs):
        for key, val in kwargs.items():
            if val is None:
                continue

            self.properties[key] = val

    @staticmethod
    def _convert_class_mapping(class_mapping):
        if class_mapping is None:
            return

        if isinstance(class_mapping, (list, tuple, np.ndarray)):
            class_mapping = {k: v for k, v in enumerate(class_mapping)}

        if not isinstance(class_mapping, dict):
            raise ValueError('class_mapping type not supported %s' % type(class_mapping))

        return class_mapping

    def __set_class_mapping(self, class_mapping):
        self._class_mapping = self._convert_class_mapping(class_mapping)

    def set_properties(self, display_name=None, description=None, class_mapping=None, **kwargs):
        self._update_properties = True
        self.__set_properties_names(display=display_name, description=description)
        self.__set_class_mapping(class_mapping)

        if len(kwargs) > 0:
            self.set_hyperparams(**kwargs)
            self.logger.warning(
                'passing hyper parameters using the set_properties method is deprecated.'
                'please use the set_hyperparams method instead')

    def set_hyperparams(self, total_epochs=None, batch_size=None, epoch_size=None, max_iterations=None,
                        optimizer_algorithm=None, learning_rate=None, total_batches=None, learning_rate_decay=None,
                        samples_count=None, **kwargs):
        self._set_hyperparams(HyperParamTypes.RUN, total_epochs=total_epochs, batch_size=batch_size,
                              epoch_size=epoch_size, total_batches=total_batches, max_iterations=max_iterations,
                              samples_count=samples_count)

        self._set_hyperparams(HyperParamTypes.OPTIMIZER, algorithm=optimizer_algorithm,
                              learning_rate=learning_rate, learning_rate_decay=learning_rate_decay)

        self._set_hyperparams(HyperParamTypes.CUSTOM, **kwargs)

        self._update_properties = True

    def _set_hyperparams(self, hp_type, **kwargs):
        hyperparams = self.get_hyperparams()

        for key, val in kwargs.items():
            if val is None:
                continue

            hyperparams.setdefault(hp_type, {})[key] = val

        self.properties['hyperparams'] = hyperparams

    def get_hyperparams(self):
        return self.properties.get('hyperparams', {})

    def _create_remote_logger_if_needed(self, create_experiment_result):
        create_experiment_result = create_experiment_result or {}

        if os.environ.get('ML_DISABLE_REMOTE_LOGGER', os.environ.get('MISSINGLINKAI_DISABLE_REMOTE_LOGGER')) is not None:
            return

        remote_logger = create_experiment_result.get('remote_logger')

        if remote_logger is not None:
            session_id = remote_logger['session_id']
            endpoint = remote_logger['endpoint']
            log_level = remote_logger.get('log_level', logging.INFO)
            log_filter = remote_logger.get('log_filter')
            terminate_endpoint = remote_logger.get('terminate_endpoint')

            self.logger.activate_remote_logging(session_id, endpoint, log_level, log_filter, terminate_endpoint)

    def _call_new_experiment(self, throw_exceptions=None):
        one_hour_seconds = int(datetime.timedelta(hours=1).total_seconds())

        keep_alive_interval = int(os.environ.get('ML_KEEP_ALIVE_INTERVAL', one_hour_seconds))
        res = self._post_requests.create_new_experiment(
            keep_alive_interval, throw_exceptions=throw_exceptions, resume_token=self.properties.get('resume_token'), resource_management=self.rm_properties)

        self._create_remote_logger_if_needed(res)

        if getattr(self._post_requests, 'allow_source_tracking', False):
            self.properties['source_tracking'], repo = GitRepoSyncer.source_tracking_data()
            self.properties['repository_tracking'] = GitRepoSyncer.sync_working_dir_if_needed(repo, self.rm_properties.get('in_context', False))

        self.properties['resource_management'] = self.rm_properties

    @property
    def has_experiment(self):
        return self._post_requests is not None

    def new_experiment(self, throw_exceptions=None):
        self._post_requests = self.__create_post_requests()

        self._call_new_experiment(throw_exceptions=throw_exceptions)

        self.batches_queue = []
        self.points_candidate_indices = {}
        self._special_points = {}
        self.iteration = 0
        self._test_iteration = 0
        self.ts_start = 0
        self.epoch_addition = 0
        self.has_ended = False
        self.stopped = False

        if self._SEND_EPOCH_CANDIDATES:
            self.epoch_candidate_indices = {}

    @classmethod
    def _get_toplevel_metadata(cls, test_token, algo, uri):
        meta = {
            "algo": algo,
            "test_token": test_token,
            "path": uri,
            "prediction_id": uuid.uuid4().hex,
        }
        return meta

    def upload_images(self, model_hash, images, meta, description=None):
        from .dispatchers.missinglink import get_post_requests

        post_requests = get_post_requests(
            self.experiment_args['owner_id'],
            self.experiment_args['project_token'],
            host=self.experiment_args['host'],
            requests_dispatcher=self._requests_dispatcher)

        data = {
            'model_hash': model_hash,
            'images': images,
            'meta': meta,
            'description': description
        }

        post_requests.send_images(data)

    def __create_post_requests(self):
        from .dispatchers.missinglink import post_requests_for_experiment

        return post_requests_for_experiment(requests_dispatcher=self._requests_dispatcher, **self.experiment_args)

    # noinspection PyShadowingBuiltins
    def send_chart(self, name, x_values, y_values, x_legend=None, y_legends=None, scope='test', type='line', experiment_id=None, model_weights_hash=None):
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
        :return:
        """
        self.logger.activate_if_needed()

        post_r = self.__create_post_requests()
        post_r.send_chart(name, x_values, y_values, x_legend, y_legends, scope, type, experiment_id, model_weights_hash, throw_exceptions=True)

    def __post_requests_property_wrapper(self, name):
        if self.has_experiment:
            return getattr(self._post_requests, name)

        self.logger.warning('%s is only available after train_begin is called.', name)

        return None

    def update_metrics_per_iteration(self, metrics, model_weights_hash):
        """
        Send external metrics for a specific iteration.
        Using this option you can create a graph of the metrics for each iteration.
        The experiment and iterations are obtained from the weighted hash.
        :param metrics: Dictionary of metric_name => metric_value or (metric_name, metric_value) tuple. Metrics will be automatically prefixed with ex_ when it is not already present.
        :param model_weights_hash: a hexadecimal sha1 hash of the model's weights.
        :return:
        """
        self.logger.activate_if_needed()

        post_r = self.__create_post_requests()

        post_r.update_metrics_per_iteration(metrics, model_weights_hash=model_weights_hash, throw_exceptions=True)

    def update_metrics(self, metrics, experiment_id=None, model_weights_hash=None):
        """
        Send external metrics in the experiment level.
        The experiment can be obtained either from the weighted hash or directly by providing the project_id and the experiment_id.
        :param metrics: Dictionary of metric_name => metric_value or (metric_name, metric_value) tuple. Metrics will be automatically prefixed with ex_ when it is not already present.
        :param experiment_id: The id of the target experiment.
        :param model_weights_hash: a hexadecimal sha1 hash of the model's weights.
        :return:
        """
        self.logger.activate_if_needed()

        post_r = self.__create_post_requests()

        post_r.update_metrics(metrics, experiment_id=experiment_id, model_weights_hash=model_weights_hash, throw_exceptions=True)

    @property
    def experiment_id(self):
        return self.__post_requests_property_wrapper('experiment_id')

    @property
    def experiment_token(self):
        return self.__post_requests_property_wrapper('experiment_token')

    @property
    def resume_token(self):
        experiment_id = self.experiment_id
        if experiment_id is None:
            return None

        return self.experiment_token

    def batch_command(self, event, data, flush=False):
        self.logger.activate_if_needed()

        if self._post_requests is None:
            self.logger.warning(
                'missinglink callback cannot send data before train_begin is called.\n'
                'please access the instruction page for proper use')
            return

        if self.stopped:
            self.logger.debug('experiment stopped, discarding data')
            return

        command = (event, data, datetime.datetime.utcnow().isoformat())

        if event == EventTypes.BATCH_END:
            if self._SEND_EPOCH_CANDIDATES and data.get('epoch_candidate') in self.epoch_candidate_indices:
                i = self.epoch_candidate_indices[data['epoch_candidate']]
            elif data.get('points_candidate') in self.points_candidate_indices:
                i = self.points_candidate_indices[data['points_candidate']]
            else:
                i = len(self.batches_queue)
                self.batches_queue.append(None)

            self.batches_queue[i] = command

            if self._SEND_EPOCH_CANDIDATES and 'epoch_candidate' in data:
                self.epoch_candidate_indices[data['epoch_candidate']] = i

            if 'points_candidate' in data:
                self.points_candidate_indices[data['points_candidate']] = i
        else:
            self.batches_queue.append(command)

        if self._SEND_EPOCH_CANDIDATES and event == EventTypes.EPOCH_END:
            self.epoch_candidate_indices = {}

        if len(self.batches_queue) == 1:
            self.ts_start = datetime.datetime.utcnow()

        ts_end = datetime.datetime.utcnow()
        queue_duration = ts_end - self.ts_start

        if queue_duration.total_seconds() > self.dispatch_interval or flush:
            response = self._post_requests.send_commands(self.batches_queue) or {}
            self.batches_queue = []
            self.epoch_candidate_indices = {}
            self.points_candidate_indices = {}

            if response.get('stopped'):
                self._handle_stopped()

    def _handle_stopped(self):
        self.stopped = True
        if self.stopped_callback:
            self.stopped_callback()
        else:
            raise ExperimentStopped('Experiment was stopped.')

    def train_begin(self, params=None, throw_exceptions=None, **kwargs):
        self.logger.info('train begin params: %s, %s', params, kwargs)

        params = params or {}
        self.new_experiment(throw_exceptions=throw_exceptions)
        data = copy.copy(self.properties)
        data['resource_management'] = self.rm_properties
        data['params'] = params
        data.update(kwargs)
        self.batch_command(EventTypes.TRAIN_BEGIN, data, flush=True)

        self.properties = {}
        self._update_properties = False

    def _train_end(self, **kwargs):
        if not self.has_ended:
            self.logger.info('train end %s', kwargs)

            # Use `iterations` if it is passed. As we move forward, we want to reduce the
            # responsibility of this class. The experiment's state should be managed by another class
            # e.g. Experiment in TensorFlowProject.
            iterations = int(kwargs.get('iterations', self.iteration))

            data = {'iterations': iterations}
            data.update(kwargs)
            self.batch_command(EventTypes.TRAIN_END, data, flush=True)
            self.has_ended = True

    def train_end(self, **kwargs):
        warnings.warn("This method is deprecated", DeprecationWarning)
        self._train_end(**kwargs)

    # noinspection PyUnusedLocal
    def epoch_begin(self, epoch, **kwargs):
        epoch = int(epoch)

        if epoch == 0:
            self.epoch_addition = 1

    def epoch_end(self, epoch, metric_data=None, **kwargs):
        self.logger.info('epoch %s ended %s', epoch, metric_data)

        epoch = int(epoch)

        metric_data = copy.deepcopy(metric_data)

        computed_values, updated_metrics = self._update_computed_metrics(metric_data, 'epoch')
        metric_data.update(computed_values)

        for metric_name in updated_metrics:
            if metric_name in self._epoch_special_points:
                del self._epoch_special_points[metric_name]

        data = {
            'epoch': epoch + self.epoch_addition,
            'results': metric_data,
        }

        # Filter Epochs
        if epoch <= self.get_epoch_sampling_size():
            data['points_candidate'] = epoch + self.epoch_addition
        else:
            # Converse initial location
            self.set_points_candidate(data, epoch, 0, updated_metrics, self.get_epoch_sampling_size(), self._epoch_special_points)

        send = 'points_candidate' in data
        if send:
            for metric_name in updated_metrics:
                self._epoch_special_points[metric_name] = data['points_candidate']

            data.update(kwargs)
            self.batch_command(EventTypes.EPOCH_END, data, flush=data['epoch'] == 1)

    def batch_begin(self, batch, epoch, **_kwargs):
        self.iteration += 1

    def batch_end(self, batch, epoch, metric_data, update_hyperparams=False, **kwargs):
        batch = int(batch)
        epoch = int(epoch)
        is_test = kwargs.get('is_test', False)
        metric_data = copy.deepcopy(metric_data)

        # Use `iteration` if it is passed into `batch_end`. As we move forward, we want to reduce the
        # responsibility of this class. The experiment's state should be managed by another class
        # e.g. Experiment in TensorFlowProject.
        iteration = int(kwargs.get('iteration', self.iteration))
        computed_values, updated_metrics = self._update_computed_metrics(metric_data, 'batch')
        self._latest_metrics = copy.deepcopy(metric_data)
        metric_data.update(computed_values)

        data = {
            'batch': batch,
            'epoch': epoch,
            'iteration': iteration,
            'metricData': metric_data,
        }
        if update_hyperparams or self._update_properties:
            data['params'] = self.properties
            self.properties = {}
        self._update_properties = False

        if is_test:
            self._test_iteration += 1

        starting_offset = self.get_batch_sampling_size() if is_test else 0
        iteration = self._test_iteration if is_test else iteration

        for metric_name in updated_metrics:
            if metric_name in self._batch_special_points:
                del self._batch_special_points[metric_name]

        # Filter batch
        if iteration <= self.get_batch_sampling_size():
            if self._SEND_EPOCH_CANDIDATES:
                data['epoch_candidate'] = batch

            data['points_candidate'] = starting_offset + iteration
        else:
            # Conserve initial location
            self.set_points_candidate(data, iteration, starting_offset, updated_metrics, self.get_batch_sampling_size(), self._batch_special_points)

            if self._SEND_EPOCH_CANDIDATES:
                if batch < self._MAX_BATCHES_PER_EPOCH:
                    data['epoch_candidate'] = batch
                else:
                    epoch_candidate = random.randint(0, batch - 1)
                    if epoch_candidate < self._MAX_BATCHES_PER_EPOCH:
                        data['epoch_candidate'] = epoch_candidate

        send = 'points_candidate' in data or 'epoch_candidate' in data

        if 'points_candidate' in data:
            for metric_name in updated_metrics:
                self._batch_special_points[metric_name] = data['points_candidate']

        if send:
            data.update(kwargs)
            self.batch_command(EventTypes.BATCH_END, data, flush=iteration == 1)

    def set_points_candidate(self, data, iteration, starting_offset, updated_metrics, sampling_size, special_points):
        points_candidate = self._get_point_candidate(iteration, sampling_size, special_points)
        while not points_candidate and len(updated_metrics) > 0:
            points_candidate = self._get_point_candidate(iteration, sampling_size, special_points)

        if points_candidate:
            data['points_candidate'] = starting_offset + points_candidate

    def _get_point_candidate(self, iteration, sampling_size, special_points):
        points_candidate = random.randint(self._FIRST_ITERATION + 1, iteration)
        if points_candidate <= sampling_size and points_candidate not in special_points.values():
            return points_candidate

    def _update_computed_metrics(self, metric_data, phase):
        computed_values = {}
        updated_metrics = set()
        for func_name, func in self._COMPUTED_METRICS_METHODS.items():
            for metric_name, metric_value in metric_data.items():
                if self._update_computed_metric(computed_values, func, func_name, metric_name, metric_value, phase):
                    updated_metrics.add(func_name)
        self._computed_metrics[phase].update(computed_values)
        return computed_values, updated_metrics

    def _update_computed_metric(self, computed_values, func, func_name, metric_name, metric_value, phase):
        computed_name = self._build_computed_metric_name(func_name, metric_name)
        try:
            if computed_name in self._computed_metrics[phase]:
                new_value = func(metric_value, self._computed_metrics[phase][computed_name])
                if self._computed_metrics[phase][computed_name] != new_value:
                    computed_values[computed_name] = new_value
                    return func_name in self._TRACKED_SPECIAL
            elif isinstance(func, type):
                computed_values[computed_name] = func(metric_value)
                return func_name in self._TRACKED_SPECIAL
            else:
                computed_values[computed_name] = metric_value
                return func_name in self._TRACKED_SPECIAL
        except (ValueError, TypeError):
            pass

    def _build_computed_metric_name(self, func_name, metric_name):
        return 'computed|' + func_name + '|' + metric_name

    def _test_begin(self, steps, weights_hash, name=None):
        if self._has_test_context:
            self.logger.warning('test begin called twice without calling end')
            return

        self._test_iteration_count = 0
        self._test_samples_count = 0
        self._has_test_context = True
        self._test_iter = steps
        self._update_test_token()
        self._found_classes = set()

        data = {
            'test_token': self._test_token,
            'test_data_size': self._test_iter or 0,
        }

        if weights_hash is not None:
            data['weights_hash'] = weights_hash

        if name is not None:
            data['name'] = name

        self.batch_command(EventTypes.TEST_BEGIN, data, flush=True)

    def _send_test_iteration_end(self, expected, predictions, probabilities, partial_class_mapping,
                                 partial_found_classes, is_finished=False, **kwargs):
        data = {
            'test_token': self._test_token,
            'predicted': predictions,
            'expected': expected,
            'probabilities': probabilities,
            'iteration': self._test_iteration_count,
            'partial_class_mapping': partial_class_mapping,
            'total_classes': len(self._found_classes) if self._found_classes is not None else 0,
            'partial_found_classes': partial_found_classes
        }

        data.update(kwargs)
        event = EventTypes.TEST_END if is_finished else EventTypes.TEST_ITERATION_END
        flush = is_finished
        self.batch_command(event, data, flush=flush)

    def _test_iteration_end(self, expected, predictions, probabilities, **kwargs):
        is_finished = kwargs.get('is_finished', False)

        if not is_finished:
            self._test_iteration_count += 1

        partial_class_mapping = {}
        partial_found_classes = []

        class_mapping = kwargs.pop('class_mapping', self._class_mapping)

        unique_ids = list(set(expected) | set(predictions))
        for class_id in unique_ids:
            if self._found_classes is None or class_id in self._found_classes:
                continue

            self._found_classes.add(class_id)
            partial_found_classes.append(class_id)
            if not class_mapping:
                continue

            if class_id in class_mapping:
                partial_class_mapping[class_id] = class_mapping[class_id]
                continue

            self.logger.warning('no class mapping for class id %d', class_id)

        self._send_test_iteration_end(expected, predictions, probabilities, partial_class_mapping, partial_found_classes, **kwargs)

    def _test_end(self, **kwargs):
        self._test_iteration_end([], [], [], is_finished=True, **kwargs)

        self._has_test_context = False
        self._test_iteration_count = 0
        self._test_token = None

    @staticmethod
    def generate_tag(length=4):
        chars = '1234567890_-abcdefghijklmnopqrstuvwxyz'
        tag = ''
        for _ in range(length):
            tag += random.choice(chars)

        return tag

    def _extract_hyperparams(self, hp_type, obj, object_type_to_attrs, attr_to_hyperparam, object_type=None):
        if isinstance(obj, dict):
            def has_attr(name):
                return name in obj

            def get_attr(name):
                return obj.get(name)
        else:
            def has_attr(name):
                return hasattr(obj, name)

            def get_attr(name):
                return getattr(obj, name)

        object_type = object_type or obj.__class__.__name__
        hyperparams = {}
        attrs = object_type_to_attrs.get(object_type, [])

        for param_name in attrs:
            if has_attr(param_name):
                value = self.variable_to_value(get_attr(param_name))
                param_name = attr_to_hyperparam.get(param_name, param_name)
                hyperparams[param_name] = value
        self._set_hyperparams(hp_type, **hyperparams)

    @classmethod
    def variable_to_value(cls, variable):
        return variable

    @classmethod
    def _hash(cls, value):
        str_repr = str(value).encode()
        h = hashlib.sha1(str_repr).hexdigest()
        return h


class BaseContextValidator(object):
    """
        This class validates if we can enter or exit a context.
        """

    def __init__(self, logger):
        self._contexts = []
        self._logger = logger
        self._is_iteration_with_validation = False

    @property
    def last_phase(self):
        try:
            return self._contexts[-1][1]
        except IndexError:
            return None

    def get_average_metrics(self):
        phase = self.last_phase

        if phase is None:
            return None

        return phase.get_average_metrics()

    @contextmanager
    def context(self, context, *args, **kwargs):
        self.enter(context, *args, **kwargs)
        try:
            yield
        finally:
            self.exit(context)

    @property
    def is_iteration_with_validation(self):
        return self._is_iteration_with_validation

    @property
    def in_test_context(self):
        return self.last_context == Context.TEST

    def enter(self, context, *args, **kwargs):
        if context == Context.TRAIN:
            metric_prefix = MetricPhasePrefixes.TRAIN
        elif context == Context.TEST:
            metric_prefix = MetricPhasePrefixes.TEST
        elif context == Context.VALIDATION:
            metric_prefix = MetricPhasePrefixes.VAL
        else:
            metric_prefix = MetricPhasePrefixes.TRAIN

        klass = PhaseTest if context == Context.TEST else PhaseEpoch if context == Context.EPOCH_LOOP else Phase
        phase = klass(metric_prefix, *args, **kwargs)

        map_context_to_validator = {
            Context.EXPERIMENT: self._validate_experiment_context,
            Context.LOOP: self._validate_loop_context,
            Context.EPOCH_LOOP: self._validate_epoch_loop_context,
            Context.BATCH_LOOP: self._validate_batch_loop_context,
            Context.TRAIN: self._validate_train_context,
            Context.VALIDATION: self._validate_validation_context,
            Context.TEST: self._validate_test_context
        }

        try:
            map_context_to_validator[context]()
        except KeyError:
            # This should never happen unless we mess up
            raise MissingLinkException('Unknown scope %s' % context)

        if context == Context.VALIDATION:
            self._is_iteration_with_validation = True

        self._contexts.append((context, phase))

    def exit(self, context):
        exit_context, exit_phase = self._contexts.pop()

        last_phase = self.last_phase

        if last_phase is not None:
            last_phase.update_metrics_from_phase(exit_phase)
            last_phase.update_queries_from_phase(exit_phase)

        if exit_context != context:
            # This should never happen unless we mess up
            raise MissingLinkException('Cannot exit %s scope because the current scope is %s' % (context, exit_context))

    def step_finished(self):
        self.last_phase.reset()
        self._is_iteration_with_validation = False

    @property
    def last_context(self):
        try:
            return self._contexts[-1][0]
        except IndexError:
            raise MissingLinkException("Outside of experiment context. Please use the project to create an experiment.")

    def _validate_experiment_context(self):
        if self._contexts:
            raise MissingLinkException('Experiment context must be outermost')

    def __validate_last_context(self, context_name, contexts):
        if not self._contexts or self.last_context not in contexts:
            raise MissingLinkException('`%s` must be nested immediately in an `%s` context.' % (context_name, ','.join(contexts)))

    def _validate_loop_context(self):
        self.__validate_last_context(Context.LOOP, (Context.EXPERIMENT, Context.TRAIN))

    def _validate_epoch_loop_context(self):
        self.__validate_last_context(Context.EPOCH_LOOP, (Context.EXPERIMENT, Context.TRAIN))

    def _validate_batch_loop_context(self):
        self.__validate_last_context(Context.BATCH_LOOP, (Context.EPOCH_LOOP, Context.TRAIN, Context.TEST, Context.VALIDATION))

    def _validate_train_context(self):
        pass

    def _validate_validation_context(self):
        pass

    def _validate_test_context(self):
        pass


class Context(object):
    EXPERIMENT = 'experiment'
    LOOP = 'loop'
    EPOCH_LOOP = 'epoch_loop'
    BATCH_LOOP = 'batch_loop'
    TRAIN = 'train'
    TEST = 'test'
    VALIDATION = 'validation'
