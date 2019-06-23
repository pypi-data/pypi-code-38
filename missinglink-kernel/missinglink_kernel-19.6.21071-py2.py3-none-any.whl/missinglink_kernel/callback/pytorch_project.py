# -*- coding: utf-8 -*-
import copy

from .phase import ExperimentCounters, GeneratorDone
from .base_callback import BaseCallback, BaseContextValidator, Context
from .exceptions import MissingLinkException, ExperimentStopped
from .interfaces import ModelHashInterface
from .settings import HyperParamTypes
from contextlib import contextmanager
from .utilities.utils import ZeroIndexedGenerators, get_nested_attribute_if_exists
import numpy as np


class PyTorchProject(BaseCallback, ModelHashInterface):
    def __init__(self, owner_id=None, project_token=None, host=None, **kwargs):
        super(PyTorchProject, self).__init__(owner_id, project_token, host=host, framework='pytorch', **kwargs)
        self._context_validator = ContextValidator(self.logger)

    def variable_to_value(self, variable):
        import torch

        if isinstance(variable, torch.Tensor):
            return variable.item()

        return super(PyTorchProject, self).variable_to_value(variable)

    def _hyperparams_from_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'Adadelta': ['rho', 'eps', 'lr', 'weight_decay'],
            'Adagrad': ['lr', 'lr_decay', 'weight_decay'],
            'Adam': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'Adamax': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'ASGD': ['lr', 'lambd', 'alpha', 't0', 'weight_decay'],
            'LBFGS': ['lr', 'max_iter', 'max_eval', 'tolerance_grad', 'tolerance_change', 'history_size'],
            'RMSprop': ['lr', 'alpha', 'eps', 'weight_decay'],
            'Rprop': ['lr', 'etaminus', 'etaplus', 'minimum_step_size', 'maximum_step_size'],
            'SGD': ['lr', 'dampening', 'weight_decay'],
        }
        attr_to_hyperparam = {
            'lr': 'learning_rate',
            'lr_decay': 'learning_rate_decay',
            'eps': 'epsilon',
            'lambd': 'lambda',
            'max_iter': 'max_iteration',
            'max_eval': 'max_evaluation',
            'tolerance_grad': 'tolerance_gradient',
        }

        optimizer_type = optimizer.__class__.__name__
        params_groups = optimizer.param_groups

        if len(params_groups) < 1:
            return

        hyperparams = copy.copy(params_groups[0])

        expansions = {
            'betas': ['beta_1', 'beta_2'],
            'etas': ['etaminus', 'etaplus'],
            'step_sizes': ['minimum_step_size', 'maximum_step_size']
        }

        for name, names in expansions.items():
            values = hyperparams.get(name)
            if values is not None and len(values) == len(names):
                for key, val in zip(names, values):
                    hyperparams[key] = val

        self.set_hyperparams(optimizer_algorithm=optimizer_type)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, hyperparams, optimizer_to_attrs,
                                  attr_to_hyperparam, object_type=optimizer_type)

    def _hyperparams_from_data_object(self, data_object):
        if data_object is None:
            return

        iterator_attributes = ['train', 'repeat', 'shuffle', 'sort', 'sort_within_batch', 'device']
        object_to_attributes = {
            'DataLoader': ['num_workers', 'pin_memory', 'drop_last'],
            'Iterator': iterator_attributes,
            'BucketIterator': iterator_attributes,
            'BPTTIterator': iterator_attributes,
        }

        object_type = data_object.__class__.__name__
        if object_type not in object_to_attributes:
            return

        attribute_to_hyperparam = {}  # hyperparams will have the same names as the attributes

        self._extract_hyperparams(HyperParamTypes.CUSTOM, data_object, object_to_attributes, attribute_to_hyperparam)

        hyperparams = {'data_object': object_type}

        # maps hyperparams names to the attribute that holds their value
        extraction_map = {
            'dataset': ['dataset', '__class__', '__name__'],
            'batch_size': ['batch_size']
        }

        if object_type == 'DataLoader':
            extraction_map['collate_function'] = ['collate_fn', '__name__']
            extraction_map['sampler'] = ['sampler', '__class__', '__name__']

        elif object_type in object_to_attributes:
            extraction_map['batch_size_function'] = ['batch_size_fn', '__name__']

        for hyperparam_name, attributes_path in extraction_map.items():
            hyperparam_value = get_nested_attribute_if_exists(data_object, attributes_path)
            if hyperparam_value is not None:
                hyperparams[hyperparam_name] = hyperparam_value

        if hasattr(data_object, '__len__'):
            hyperparams['epoch_size'] = len(data_object)

        try:
            hyperparams['samples_count'] = len(data_object.dataset)
        except (TypeError, AttributeError):
            pass

        self.set_hyperparams(**hyperparams)

    def _begin_experiment(self, experiment):
        structure_hash = self._get_structure_hash(experiment.model)
        self.train_begin({}, structure_hash=structure_hash)

    @contextmanager
    def create_experiment(self, model,
                          display_name=None,
                          description=None,
                          class_mapping=None,
                          optimizer=None,
                          train_data_object=None,
                          hyperparams=None,
                          metrics=None,
                          stopped_callback=None):
        if metrics is None:
            metrics = {}

        self.set_properties(display_name=display_name, description=description, class_mapping=class_mapping)
        if optimizer:
            self._hyperparams_from_optimizer(optimizer)

        self._hyperparams_from_data_object(train_data_object)

        if hyperparams is not None:
            self.set_hyperparams(**hyperparams)

        self.stopped_callback = stopped_callback

        experiment = PyTorchExperiment(self, model, metrics)

        try:
            with self._context_validator.context(Context.EXPERIMENT):
                self._begin_experiment(experiment)

                yield experiment
        except ExperimentStopped:
            # noinspection PyProtectedMember
            experiment._on_train_ended()

            self._handle_stopped()

    @ModelHashInterface.wrap_all_get_structure_hash_exceptions
    def _get_structure_hash(self, net):
        layers = []
        for m in net.modules():
            layers.append(str(m))
        layers = tuple(layers)
        hash_string = self._hash(layers)
        return hash_string

    def get_weights_hash(self, net):
        from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine

        hashes = list()
        for m in net.modules():
            layer_hashes = [hasharray(i.data.cpu().numpy()) for i in m.parameters()]
            hashes.extend(layer_hashes)

        hash_key = hashcombine(*hashes)
        return self._WEIGHTS_HASH_PREFIX + hash_key

    def calculate_weights_hash(self, net):
        return self.get_weights_hash(net)


class PyTorchExperiment(object):
    def __init__(self, project, model, metrics=None, every_n_secs=None, every_n_iter=None):
        self._project = project

        metrics = metrics or {}
        self._wrapped_metrics = {}
        self.wrap_metrics(metrics)

        self.model = model
        self._epochs = None
        self._experiment_counters = ExperimentCounters(every_n_secs, every_n_iter)

    @property
    def _logger(self):
        return self._project.logger

    @property
    def _context_validator(self):
        # noinspection PyProtectedMember
        return self._project._context_validator

    def get_average_metrics(self):
        return self._context_validator.get_average_metrics()

    def _on_train_ended(self):
        # noinspection PyProtectedMember
        self._project._train_end(iterations=self._iteration, metricData=self.get_average_metrics())

    @property
    def metrics(self):
        return self._wrapped_metrics

    def _get_metric_data(self, result):
        variable = result.data.item() if hasattr(result.data, 'item') else result.data[0]
        return self._project.variable_to_value(variable)

    def _wrap(self, key, base):
        def wrapped(*args, **kwargs):
            result = base(*args, **kwargs)

            # Do not monitor metrics if inside test context
            if self._context_validator.in_test_context:
                return result

            is_custom_metric = not (hasattr(result, 'data') and hasattr(result.data, '__getitem__'))

            metric_data = result if is_custom_metric else self._get_metric_data(result)

            self.add_metric(key, metric_data)

            return result

        return wrapped

    def _wrap_metrics_dict(self, metrics_dict):
        wrapped = copy.copy(metrics_dict)

        for key, base in wrapped.items():
            wrapped[key] = self._wrap(key, base)

        self._wrapped_metrics.update(wrapped)

        return wrapped

    def _wrap_metrics_list(self, metrics_list):
        wrapped = []

        for base in metrics_list:
            key = base.__name__
            wrapped_function = self._wrap(key, base)

            wrapped.append(wrapped_function)
            self._wrapped_metrics[key] = wrapped_function

        return wrapped

    def _wrap_metric(self, base):
        key = base.__name__
        wrapped = self._wrap(key, base)
        self._wrapped_metrics[key] = wrapped

        return wrapped

    def wrap_metrics(self, metrics):
        """
        :param metrics: Single, list or dictionary of pytorch functionals
        """
        wrapped = None
        if isinstance(metrics, dict):
            wrapped = self._wrap_metrics_dict(metrics)
        elif isinstance(metrics, (list, tuple)):
            wrapped = self._wrap_metrics_list(metrics)
        elif metrics is not None:
            wrapped = self._wrap_metric(metrics)

        return wrapped

    @staticmethod
    def _total_epochs(max_iterations, epoch_size):
        if not max_iterations or not epoch_size:
            return None

        return max_iterations // epoch_size

    @classmethod
    def _assert_single_argument(cls, args, error_message=''):
        # count arguments
        args_count = len([arg for arg in args if arg is not None])

        if args_count != 1:
            raise MissingLinkException('Bad Arguments: ' + error_message)

    @staticmethod
    def _epoch_batch_loop_total_iterations(iterations, iterable):
        # This function is called by:
        #   `epoch_loop` to calculate the number of total epochs
        #   `batch_loop` to calculate the epoch size (= batches per epoch)
        if iterable is None:
            return iterations

        if hasattr(iterable, '__len__'):
            return len(iterable)

        return None

    @staticmethod
    def _batch_loop_max_iterations(epochs, epoch_size):
        try:
            return epochs * epoch_size
        except TypeError:
            return None

    @staticmethod
    def _choose_generator(iterations, condition, iterable):
        if iterations is not None:
            return ZeroIndexedGenerators.range_generator(iterations)

        if condition is not None:
            return ZeroIndexedGenerators.condition_generator(condition)

        if iterable is not None:
            return ZeroIndexedGenerators.iterable_generator(iterable)

        raise MissingLinkException('Provide batches, condition or iterable to batch_loop.')

    def add_metric(self, name, value):
        self._phase.add_metric(name, value, is_custom=True)

    @property
    def _phase(self):
        return self._context_validator.last_phase

    @property
    def _is_iteration_with_validation(self):
        return self._context_validator.is_iteration_with_validation

    @contextmanager
    def loop_context(self, max_iterations=None, condition=None, iterable=None, epoch_size=None):
        """Provides a training loop generator.

        This generator allows the MissingLinkAI SDK to correctly track each training iteration and its
        corresponding metrics.

        You would normally write the training loop as
        ```python
            for step in range(1000):
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step in experiment.loop(max_iterations=1000):
                # Perform a training step
        ```

        If you wants to run the training steps while a condition is satisfied, a while loop is preferred.
        ```python
            threshold = 10
            step = 0
            while loss > threshold:
                # Perform a training step
                step += 1
        ```

        This can be converted to
        ```python
            threshold = 10
            for step in experiment.loop(condition=lambda _: loss > threshold):
                # Perform a training step
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for sample in data:
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step, sample in experiment.loop(iterable=data):
                # Perform a training step
        ```

        If you want to collect and analyze metrics with respect to epochs, specify the `epoch_size` param with
        the number of iterations per epoch.

        # Arguments:
            max_iterations: The maximum number of training iterations to be run. Cannot be provided
                together with `condition` or `iterable`.
            condition: The condition function to run the training steps. Once the condition fails, the
                training will terminate immediately. This function takes 1 parameter: a 0-based index
                indicating how many iterations have been run.
                Cannot be provided together with `max_iterations` or `iterable`.
            iterable: The iterable to iterate over in the loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `max_iterations` or `condition`.
            epoch_size: (Optional.) The number of iterations per epoch.

        # Yields:
            A 0-based index, if provided with `max_iterations` or with `condition`.
            A tuple of 0-based index and a sample, if provided with `iterable`.
        """
        message = '`loop` should be called with one of max_iterations, condition, or iterable.' \
                  ' Called with: max_iterations=%s, condition=%s, iterable=%s instead.' % \
                  (max_iterations, condition, iterable)
        self._assert_single_argument((max_iterations, condition, iterable), message)

        with self._context_validator.context(Context.LOOP):
            self._project.set_hyperparams(max_iterations=max_iterations, epoch_size=epoch_size,
                                          total_epochs=self._total_epochs(max_iterations, epoch_size))

            self._project._hyperparams_from_data_object(iterable)

            # In the case of multiple loops on the same experiment,
            # you might expect index to start at `self._iteration - 1`,
            # so the index of the loops keeps incrementing from loop to loop.
            # However, we decided to keep it this way, to keep on consistency with the `range` function.
            generator = self._choose_generator(max_iterations, condition, iterable)

            def post_data():
                is_epoch_iteration = self._experiment_counters.is_epoch_iteration(epoch_size)

                weights_hash = self._project.get_weights_hash(self.model) \
                    if self._is_iteration_with_validation or is_epoch_iteration else None

                batch_weights_hash = weights_hash if self._is_iteration_with_validation else None

                self._project.batch_end(
                    self._batch, self._epoch, self.get_average_metrics(), iteration=self._iteration,
                    weights_hash=batch_weights_hash, is_test=self._is_iteration_with_validation)

                should_increment_epoch = False

                if is_epoch_iteration:
                    should_increment_epoch = True

                    self._project.epoch_end(self._epoch, self.get_average_metrics(), weights_hash=weights_hash)

                return should_increment_epoch

            try:
                yield self._experiment_counters.get_loop(self._context_validator, generator, post_data, self._on_train_ended)
            except GeneratorDone:
                pass

    @contextmanager
    def batch_loop_context(self, batches=None, condition=None, iterable=None):
        """Provides a batch loop generator.

        This generator should be nested in a `epoch_loop` generator. Please see `epoch_loop` for more details.

        This generator can be used like the `range` function:
        ```python
        for batch_index in experiment.batch_loop(batches):
            # Preform training on a single batch
        ```

        Also, this generator can be used to iterate over an iterable, like so:
        ```python
        for batch_index, batch_data in experiment.bath_loop(iterable=data):
            # Preform training on a single batch
        ```

        # Arguments:
            batches: The total number of batches. Cannot be provided with `iterable`.
            iterable: The iterable to iterate over in the batch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `batches`.
        # Yields:
            A 0-based index, if provided with `batches`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """
        message = '`batch_loop` should be called with one of batches, condition, or iterable.' \
                  ' Called with: batches=%s, condition=%s, iterable=%s instead.' % \
                  (batches, condition, iterable)
        self._assert_single_argument((batches, condition, iterable), message)

        with self._context_validator.context(Context.BATCH_LOOP):
            epoch_size = self._epoch_batch_loop_total_iterations(batches, iterable)
            max_iterations = self._batch_loop_max_iterations(self._epochs, epoch_size)
            self._project.set_hyperparams(epoch_size=epoch_size, max_iterations=max_iterations)

            # noinspection PyProtectedMember
            self._project._hyperparams_from_data_object(iterable)

            generator = self._choose_generator(batches, condition, iterable)

            def post_data():
                weights_hash = self._project.get_weights_hash(
                    self.model) if self._is_iteration_with_validation else None

                self._project.batch_end(
                    self._batch, self._epoch, self.get_average_metrics(),
                    iteration=self._iteration, weights_hash=weights_hash, is_test=self._is_iteration_with_validation)

            try:
                yield self._experiment_counters.get_batch_loop(self._context_validator, generator, post_data)
            except GeneratorDone:
                pass

    def batch_loop(self, batches=None, condition=None, iterable=None):
        """Provides a batch loop generator.

        This generator should be nested in a `epoch_loop` generator. Please see `epoch_loop` for more details.

        This generator can be used like the `range` function:
        ```python
        for batch_index in experiment.batch_loop(batches):
            # Preform training on a single batch
        ```

        This generator can be used like a `while` loop:
        ```python
        threshold = 10
        for batch_index in experiment.batch_loop(condition=lambda _: loss > threshold):
            # Preform training on a single batch
        ```

        This generator can be used to iterate over an iterable, like so:
        ```python
        for batch_index, batch_data in experiment.bath_loop(iterable=data):
            # Preform training on a single batch
        ```
        # Arguments:
            batches: The total number of batches. Cannot be provided with `iterable` or with `condition`.
            condition: The condition function to run the training batches.
                The condition is evaluated every batch. If the condition is false, the loop terminates.
                This function takes 1 parameter: a 0-based index indicating how many batches have been run.
                Cannot be provided together with `batches` or with `iterable`.
            iterable: The iterable to iterate over in the batch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `batches` or with `condition`.
        # Yields:
            A 0-based index, if provided with `batches` or with `condition`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """

        with self.batch_loop_context(batches, condition, iterable) as loop:
            for result in loop:
                yield result

    @contextmanager
    def epoch_loop_context(self, epochs=None, condition=None, iterable=None):
        """Provides a epoch loop generator.

        This generator is used together with the `batch_loop` generator to run your training with
        epochs and batches using nested loops.

        You would normally write your training loops as
        ```python
        for epoch in range(epochs):
            for batch in range(batches):
                # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
        for epoch in experiment.epoch_loop(epochs):
            for batch in experiment.batch_loop(batches):
                # Perform a training step on a batch of data
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for epoch_data in data:
                # Perform an epoch
        ```

        This can be converted to
        ```python
            for step, epoch_data in experiment.epoch_loop(iterable=data):
                for batch in experiment.batch_loop(batches):
                    # Perform a training step on a batch of data
        ```

        # Arguments:
            epochs: The total number of epochs
            iterable: The iterable to iterate over in the epoch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `epochs`.
        # Yields:
            A 0-based index, if provided with `epochs`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """
        message = '`epoch_loop` should be called with one of epochs, condition, or iterable.' \
                  ' Called with: epochs=%s, condition=%s, iterable=%s instead.' % \
                  (epochs, condition, iterable)
        self._assert_single_argument((epochs, condition, iterable), message)

        with self._context_validator.context(Context.EPOCH_LOOP):
            self._epochs = self._epoch_batch_loop_total_iterations(epochs, iterable)
            self._project.set_hyperparams(total_epochs=self._epochs)

            self._project._hyperparams_from_data_object(iterable)

            generator = self._choose_generator(epochs, condition, iterable)

            def post_data():
                weights_hash = self._project.get_weights_hash(self.model)

                self._project.epoch_end(self._epoch, self.get_average_metrics(), weights_hash=weights_hash)

            try:
                yield self._experiment_counters.get_epoch_loop(self._context_validator, generator, post_data, self._on_train_ended)
            except GeneratorDone:
                pass

    def epoch_loop(self, epochs=None, condition=None, iterable=None):
        """Provides a epoch loop generator.

        This generator is used together with the `batch_loop` generator to run your training with
        epochs and batches using nested loops.

        You would normally write your training loops as
        ```python
        for epoch in range(epochs):
            for batch in range(batches):
                # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
        for epoch in experiment.epoch_loop(epochs):
            for batch in experiment.batch_loop(batches):
                # Perform a training step on a batch of data
        ```

        If you want to loop while a condition is satisfied:
        ```python
            threshold = 10
            while loss > threshold:
                for batch in range(batches):
                    # Perform a training step on a batch of data
        ```

        This can be converted to:
        ```python
            for epoch in experiment.epoch_loop(condition=lambda _: loss > threshold):
                for batch in experiment.batch_loop(batches):
                    # Perform a training step on a batch of data
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for epoch_data in data:
                for batch in range(batches):
                    # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
            for step, epoch_data in experiment.epoch_loop(iterable=data):
                for batch in experiment.batch_loop(batches):
                    # Perform a training step on a batch of data
        ```
        # Arguments:
            epochs: The total number of epochs.
                Cannot be provided together with `condition` or with `iterable`.
            condition: The condition function to run the training epochs.
                The condition is evaluated every epoch. If the condition is false, the loop terminates.
                This function takes 1 parameter: a 0-based index indicating how many epochs have been run.
                Cannot be provided together with `epochs` or with `iterable`.
            iterable: The iterable to iterate over in the epoch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `epochs` or with `condition`.
        # Yields:
            A 0-based index, if provided with `epochs` or with `condition`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """

        with self.epoch_loop_context(epochs, condition, iterable) as loop:
            for result in loop:
                yield result

    def loop(self, max_iterations=None, condition=None, iterable=None, epoch_size=None):
        """Provides a training loop generator.

        This generator allows the MissingLinkAI SDK to correctly track each training iteration and its
        corresponding metrics.

        You would normally write the training loop as
        ```python
            for step in range(1000):
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step in experiment.loop(max_iterations=1000):
                # Perform a training step
        ```

        If you wants to run the training steps while a condition is satisfied, a while loop is preferred.
        ```python
            threshold = 10
            step = 0
            while loss > threshold:
                # Perform a training step
                step += 1
        ```

        This can be converted to
        ```python
            threshold = 10
            for step in experiment.loop(condition=lambda _: loss > threshold):
                # Perform a training step
        ```
        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for sample in data:
                # Perform a training step
        ```
        This can be converted to
        ```python
            for step, sample in experiment.loop(iterable=data):
                # Perform a training step
        ```
        If you want to collect and analyze metrics with respect to epochs, specify the `epoch_size` param with
        the number of iterations per epoch.

        # Arguments:
            max_iterations: The maximum number of training iterations to be run. Cannot be provided
                together with `condition` or `iterable`.
            condition: The condition function to run the training steps. Once the condition fails, the
                training will terminate immediately. This function takes 1 parameter: a 0-based index
                indicating how many iterations have been run.
                Cannot be provided together with `max_iterations` or `iterable`.
            iterable: The iterable to iterate over in the loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `max_iterations` or `condition`.
            epoch_size: (Optional.) The number of iterations per epoch.

        # Yields:
            A 0-based index, if provided with `max_iterations` or with `condition`.
            A tuple of 0-based index and a sample, if provided with `iterable`.
        """

        with self.loop_context(max_iterations, condition, iterable, epoch_size) as loop:
            for result in loop:
                yield result

    @contextmanager
    def train(self):
        with self._context_validator.context(Context.TRAIN):
            yield

    @contextmanager
    def validation(self):
        with self._context_validator.context(Context.VALIDATION):
            yield

    @contextmanager
    def test(self, model=None, test_data_object=None, target_attribute_name='label', test_iterations=None):
        """
        `test` context for generating a confusion matrix.

        if you use a `DataLoader`, use like so:

            with test(model, test_data_object=test_loader):
                # test code

        if you use a `Iterator`, a `BucketIterator`, or a `BPTTIterator`, use like so:

            with test(model, test_data_object=test_iterator, target_attribute_name='label'):
                # test code

        Otherwise, test manually, like so:

            with test(model, test_iterations=1000):
                # call here `test_iterations` times to `confusion_matrix`

        :param model: The tested model. If not specified, defaults to the experiment's model.
        :param test_data_object: A `DataLoader` or a `Iterator` that provides the test data.
        :param target_attribute_name: The attribute name of the target of every batch,
            so that `batch.target_attribute_name` is the target. Defaults to 'label'.
        :param test_iterations: For manual test. number of test iterations.
            Should be equal to the amount of times `confusion_matrix` will be called.
        :return: None
        """

        with self._context_validator.context(Context.TEST):
            if model is None:
                model = self.model

            if test_data_object:
                with self._test_with_patched_object(model, test_data_object, target_attribute_name) as result:
                    yield result

            elif test_iterations:
                with self._test_manually(model, test_iterations) as result:
                    yield result

            else:
                self._logger.warning("Failed to test: Not provided `test_data_object` nor with `test_iterations`")
                yield

    @contextmanager
    def _test_with_patched_object(self, model, object_to_patch, target_attribute_name=None):
        map_type_to_patch_function = {
            'Iterator': self._patch_torchtext_iterator,
            'BPTTIterator': self._patch_torchtext_iterator,
            'BucketIterator': self._patch_torchtext_iterator,
            'DataLoader': self._patch_data_loader,
        }

        object_type = type(object_to_patch).__name__

        try:
            patch_function = map_type_to_patch_function[object_type]
        except KeyError:
            message = "TypeError: object of type %s is not supported for test. Please use manual test."
            self._logger.warning(message)
            yield
        else:
            weights_hash = self._project.get_weights_hash(model)
            test_iterations = len(object_to_patch)

            # noinspection PyProtectedMember
            self._project._test_begin(steps=test_iterations, weights_hash=weights_hash)

            # this is just to access the variables from the inner scopes
            # noinspection PyClassHasNoInit
            class OuterScope:
                target = []

            map_patch_function_to_arguments = {
                self._patch_torchtext_iterator: [object_to_patch, target_attribute_name, OuterScope, self._logger],
                self._patch_data_loader: [object_to_patch, OuterScope]
            }

            patch_function_args = map_patch_function_to_arguments[patch_function]
            unpatch_function = patch_function(*patch_function_args)

            def hook(_module, _input, output):
                # this is invoked after the model is forwarded
                self.confusion_matrix(output, OuterScope.target)

            handle = model.register_forward_hook(hook)

            yield

            handle.remove()
            unpatch_function()

    @staticmethod
    def _patch_data_loader(data_loader, outer_scope):
        base_iter = type(data_loader).__iter__

        def patched_iter(*args, **kwargs):
            data_loader_iter = base_iter(*args, **kwargs)
            base_next = type(data_loader_iter).__next__

            outer_scope.data_loader_iter = data_loader_iter
            outer_scope.base_next = base_next

            def patched_next(*args_, **kwargs_):
                outer_scope.data, outer_scope.target = base_next(*args_, **kwargs_)

                return outer_scope.data, outer_scope.target

            type(data_loader_iter).__next__ = type(data_loader_iter).next = patched_next

            return data_loader_iter

        type(data_loader).__iter__ = patched_iter

        def unpatch():
            type(data_loader).__iter__ = base_iter
            type(outer_scope.data_loader_iter).__next__ = type(
                outer_scope.data_loader_iter).next = outer_scope.base_next

        return unpatch

    @staticmethod
    def _patch_torchtext_iterator(iterator, target_attribute_name, outer_scope, logger):
        base_iter = type(iterator).__iter__

        def patched_iter(*args, **kwargs):
            for batch in base_iter(*args, **kwargs):
                outer_scope.target = getattr(batch, target_attribute_name, None)

                if outer_scope.target is None:
                    outer_scope.target = []
                    logger.warning(
                        "Could not find %s in batch. Make sure target_attribute_name is correct" % target_attribute_name
                    )

                yield batch

        type(iterator).__iter__ = patched_iter

        def unpatch():
            type(iterator).__iter__ = base_iter

        return unpatch

    @contextmanager
    def _test_manually(self, model, test_iterations):
        weights_hash = self._project.get_weights_hash(model)

        # noinspection PyProtectedMember
        self._project._test_begin(steps=test_iterations, weights_hash=weights_hash)

        yield

        # noinspection PyProtectedMember
        if self._project._has_test_context:
            # In case `confusion_matrix` was called less times than expected, end the test.
            self._logger.warning("`confusion_matrix` was called less times than expected")

            # noinspection PyProtectedMember
            self._project._send_test_iteration_end(
                expected=[], predictions=[], probabilities=[],
                partial_class_mapping={}, partial_found_classes=[], is_finished=True
            )
            # noinspection PyProtectedMember
            self._project._test_end()

    def confusion_matrix(self, output, target):
        """
        Explicit function to generate a confusion matrix. Call only inside a `test` context.
        :param output: A 2D `torch.autograd.Variable`. The output of the model for a single batch.
        :param target: A 1D `torch.autograd.Variable` or Array-Like. The targets (labels) of a single batch.
        :return: None
        """
        if not self._context_validator.in_test_context:
            self._logger.warning("Failed to generate confusion matrix: Not in `test` context")
            return

        if not self._project._has_test_context:
            self._logger.warning("`confusion_matrix` was called more times than expected. Future calls in this same test will be ignored")
            return

        try:
            target = target.data if type(target).__name__ == 'Variable' else target
            expected = [int(x) for x in target]
        except (ValueError, TypeError) as e:
            self._logger.warning("Failed to generate confusion matrix: `target` is not good: %s" % str(e))
            return

        try:
            output_numpy = output.cpu().data.numpy()

            predictions = np.argmax(output_numpy, axis=1).tolist() if len(output_numpy) > 0 else []
            probabilities = np.max(output_numpy, axis=1).tolist() if len(output_numpy) > 0 else []
        except (AttributeError, np.AxisError, TypeError) as e:
            self._logger.warning("Failed to generate confusion matrix: `output` is not good: %s" % str(e))
            return

        # noinspection PyProtectedMember
        self._project._test_iteration_end(expected, predictions, probabilities)
        # noinspection PyProtectedMember
        self._project._test_end()

    @property
    def _batch(self):
        # noinspection PyProtectedMember
        return self._experiment_counters._batch

    @property
    def _epoch(self):
        # noinspection PyProtectedMember
        return self._experiment_counters._epoch

    @property
    def _iteration(self):
        # noinspection PyProtectedMember
        return self._experiment_counters._iteration


class ContextValidator(BaseContextValidator):
    """
    This class validates if we can enter or exit a context.
    """
    def __init__(self, logger):
        super(ContextValidator, self).__init__(logger)

    def _validate_test_context(self):
        message = '`test` context cannot be inside `test` context or inside `validation` context, ' \
                  'and must be inside an `experiment` context. This context is ignored.'
        self._exclude_from_contexts([Context.VALIDATION, Context.TEST], message)

    def _validate_validation_context(self):
        message = '`validation` context cannot be inside `validation` context or inside `test` context, ' \
                  'and must be inside an `experiment` context. This context is ignored.'
        self._exclude_from_contexts([Context.VALIDATION, Context.TEST], message)

    def _validate_train_context(self):
        # Train context does nothing, so the user can do whatever he wants with it
        pass

    def _exclude_from_contexts(self, excluded, error_message=''):
        if not self._contexts or self.last_context in excluded:
            # Do not raise exception because we don't want to halt the experiment halfway
            self._logger.error(error_message)
