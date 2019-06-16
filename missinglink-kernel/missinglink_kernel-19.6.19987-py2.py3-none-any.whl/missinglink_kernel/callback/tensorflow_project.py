# -*- coding: utf-8 -*-
from __future__ import absolute_import
import warnings
import logging
from collections import defaultdict

try:
    from contextlib import contextmanager
except ImportError:
    # noinspection PyUnresolvedReferences
    from contextlib2 import contextmanager

import numpy as np
import six

from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine, hash_value, calc_tf_variable_value
from .base_callback import BaseCallback, BaseContextValidator, Context
from .exceptions import MissingLinkException, ExperimentStopped
from .interfaces import ModelHashInterface, GradCAMInterface, ImageDimOrdering, VisualBackPropInterface
from .settings import HyperParamTypes, AlgorithmTypes
from .utilities.utils import ZeroIndexedGenerators
from .phase import ExperimentCounters, GeneratorDone


class TensorFlowProject(BaseCallback):
    """A class for communicating with MissingLinkAI backend.

    A TensorFlowProject instance corresponds to a project created in the backend. This instance
    is used to create new experiments and send the data to the backend.
    """

    def __init__(self, owner_id=None, project_token=None, host=None, **kwargs):
        """Construct an new instance.

        # Arguments:
            owner_id: The owner's ID which can be obtained from the web dashboard
            project_token: The project's token which can be obtained from the web dashboard
            host: (Optional.) The backend endpoint
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise MissingLinkException('Please install TensorFlow library')

        super(self.__class__, self).__init__(owner_id, project_token, host=host, framework='tensorflow', **kwargs)

    def estimator_hooks(
            self,
            display_name=None,
            description=None,
            class_mapping=None,
            optimizer=None,
            hyperparams=None,
            monitored_metrics=None,
            custom_metrics=None,
            stopped_callback=None,
            every_n_iter=100,
            every_n_secs=None):

        from .tensorflow_hooks import EstimatorsHooks

        return EstimatorsHooks(
            self,
            display_name=display_name,
            description=description,
            class_mapping=class_mapping,
            optimizer=optimizer,
            hyperparams=hyperparams,
            monitored_metrics=monitored_metrics,
            custom_metrics=custom_metrics,
            stopped_callback=stopped_callback,
            every_n_iter=every_n_iter,
            every_n_secs=every_n_secs
        )

    @contextmanager
    def create_experiment(self,
                          display_name=None,
                          description=None,
                          class_mapping=None,
                          optimizer=None,
                          hyperparams=None,
                          monitored_metrics=None,
                          custom_metrics=None,
                          stopped_callback=None,
                          every_n_iter=None,
                          every_n_secs=None):
        """Create an experiment context.

        This context defines a new experiment and allows the SDK to monitor the progress of the experiment.

        ```python
            # Setup the model

            # Add the optimizer op
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
            train_op = optimizer.minimize(loss)

            project = TensorFlowProject(owner_id='owner_id', project_token='project_token')

            with project.create_experiment(
                display_name='MNIST multilayer perception',
                description='Two fully connected hidden layers',
                class_mapping={0: 'zero', 1: 'one', 2: 'two'},
                optimizer=optimizer,
                hyperparams={'batch_size': 100},
                monitored_metrics={'loss': loss},
                custom_metrics={'custom_loss': custom_loss_func}) as experiment:

                # Run the training loop
        ```

        # Arguments:
            display_name: (Optional.) The display name of the experiment
            description: (Optional.) The description of the experiment
            class_mapping: (Optional.) The class mapping of the experiment
            optimizer: (Optional.) The optimizer used to train the model. This should be an instance of
                `tf.Optimizer` or its subclasses.
            hyperparams: (Optional.) A dictionary of hyper-parameters whose keys are the parameter names. The
                values are the parameter's values.
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            An experiment context manager
        """
        self.set_properties(display_name=display_name, description=description, class_mapping=class_mapping)

        if optimizer is not None:
            self._set_optimizer(optimizer)

        if hyperparams is not None:
            self.set_hyperparams(**hyperparams)

        self.stopped_callback = stopped_callback

        try:
            experiment = Experiment(
                self,
                monitored_metrics=monitored_metrics,
                custom_metrics=custom_metrics,
                logger=self.logger,
                every_n_iter=every_n_iter,
                every_n_secs=every_n_secs)

            # noinspection PyProtectedMember
            context_validator = experiment._context_validator
            with context_validator.context(Context.EXPERIMENT):
                yield experiment

        except ExperimentStopped:
            # noinspection PyProtectedMember
            experiment._on_train_ended()

            self._handle_stopped()

    def variable_to_value(self, variable):
        import tensorflow as tf

        # noinspection PyBroadException
        try:
            if isinstance(variable, tf.Variable):
                sess = tf.get_default_session()
                if sess is not None:
                    return sess.run(variable)
                else:
                    return variable.eval()
            elif isinstance(variable, tf.Tensor):
                return getattr(variable, "name")
        except Exception:
            warnings.warn("was not able to get variable %s" % variable.name)
            return calc_tf_variable_value(variable)

        return super(TensorFlowProject, self).variable_to_value(variable)

    # noinspection SpellCheckingInspection
    def _set_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'AdadeltaOptimizer': ['_lr', '_rho', '_epsilon'],
            'AdagradOptimizer': ['_learning_rate', '_initial_accumulator_value'],
            'AdagradDAOptimizer': ['_learning_rate', '_initial_gradient_squared_accumulator_value',
                                   '_l1_regularization_strength', '_l2_regularization_strength'],
            'AdamOptimizer': ['_lr', '_beta1', '_beta2', '_epsilon'],
            'FtrlOptimizer': ['_learning_rate', '_learning_rate_power', '_initial_accumulator_value',
                              '_l1_regularization_strength', '_l2_regularization_strength'],
            'GradientDescentOptimizer': ['_learning_rate'],
            'MomentumOptimizer': ['_learning_rate', '_momentum', '_use_nesterov'],
            'ProximalAdagradOptimizer': ['_learning_rate', '_initial_accumulator_value',
                                         '_l1_regularization_strength', '_l2_regularization_strength'],
            'ProximalGradientDescentOptimizer': ['_learning_rate', '_l1_regularization_strength',
                                                 '_l2_regularization_strength'],
            'RMSPropOptimizer': ['_learning_rate', '_decay', '_momentum', '_epsilon']
        }
        attr_to_hyperparams = {
            '_lr': 'learning_rate',
            '_decay': 'learning_rate_decay'
        }

        for attrs in optimizer_to_attrs.values():
            for attr in attrs:
                if attr not in attr_to_hyperparams and attr.startswith('_'):
                    hyperparam = attr[1:]
                    attr_to_hyperparams[attr] = hyperparam

        self.set_hyperparams(optimizer_algorithm=optimizer.get_name())
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, optimizer, optimizer_to_attrs, attr_to_hyperparams)


# noinspection PyAbstractClass
class Experiment(ModelHashInterface, GradCAMInterface, VisualBackPropInterface):
    """Context manager for an experiment."""

    def __init__(self, project, monitored_metrics=None, custom_metrics=None, logger=None, every_n_secs=None, every_n_iter=None):
        """Create the context manager for an experiment.

        This context manager should be created by a TensorFlowProject instance. Please see
        `TensorFlowProject.create_experiment()` for details.
        """
        self.logger = logger or logging.getLogger(__name__)

        self._validate_monitored_fetches(monitored_metrics)
        self._validate_custom_metrics(custom_metrics)

        self.callback = project
        self._monitored_fetches = monitored_metrics or {}
        self._custom_metrics = custom_metrics or {}
        self._context_validator = ContextValidator(self.logger)
        self._max_iterations = None
        self._has_started = False
        self._epochs = None
        self._train_session = None
        self._properties = {}
        self._class_mapping = None
        self._experiment_counters = ExperimentCounters(every_n_secs, every_n_iter)

    class AlwaysTriggerTimer(object):
        """Timer that never triggers."""

        @classmethod
        def should_trigger_for_step(cls, step):
            _ = step
            return True

        @classmethod
        def update_last_triggered_step(cls, step):
            _ = step
            return None, None

    @classmethod
    def _init_timer(cls, every_n_secs, every_n_iter):
        from tensorflow.python.training.basic_session_run_hooks import SecondOrStepTimer

        return SecondOrStepTimer(every_secs=every_n_secs, every_steps=every_n_iter) if every_n_secs or every_n_iter else cls.AlwaysTriggerTimer()

    def set_properties(self, **kwargs):
        self._class_mapping = kwargs.get("class_mapping")
        self._properties = kwargs

    def _assert_single_argument(self, args, error_message=''):
        # count arguments
        args_count = len([arg for arg in args if arg is not None])

        if args_count != 1:
            raise MissingLinkException('Bad Arguments: ' + error_message, self.logger)

    def _get_generator(self, max_iterations, condition, iterable):
        if max_iterations is not None:
            return ZeroIndexedGenerators.range_generator(max_iterations)

        if condition is not None:
            return ZeroIndexedGenerators.condition_generator(condition)

        if iterable is not None:
            return ZeroIndexedGenerators.iterable_generator(iterable)

        raise MissingLinkException('Provide max_iteration, condition or iterable to loop.', self.logger)

    def add_metric(self, name, value):
        self._phase.add_metric(name, value, is_custom=True)

    @property
    def _phase(self):
        return self._context_validator.last_phase

    @property
    def _is_iteration_with_validation(self):
        return self._context_validator.is_iteration_with_validation

    def _on_train_ended(self):
        # noinspection PyProtectedMember
        self.callback._train_end(iterations=self._iteration, metricData=self.get_average_metrics())

    @contextmanager
    def loop_context(self, max_iterations=None, condition=None, iterable=None, epoch_size=None):
        message = '`loop` should be called with one of max_iterations, condition, or iterable.' \
                  ' Called with: max_iterations=%s, condition=%s, iterable=%s instead.' % \
                  (max_iterations, condition, iterable)

        self._assert_single_argument((max_iterations, condition, iterable), message)

        with self._context_validator.context(Context.LOOP):
            self.callback.set_hyperparams(
                max_iterations=max_iterations, epoch_size=epoch_size,
                total_epochs=self._loop_total_epochs(max_iterations, epoch_size))

            generator = self._get_generator(max_iterations, condition, iterable)

            def post_data():
                should_calc_weights_hash = self._is_iteration_with_validation or self._experiment_counters.is_epoch_iteration(epoch_size)
                weights_hash = self.get_weights_hash(self._train_session) if should_calc_weights_hash else None

                batch_weights_hash = weights_hash if self._is_iteration_with_validation else None

                self.callback.batch_end(
                    self._batch, self._epoch, self._phase.get_average_metrics(), iteration=self._iteration,
                    is_test=self._is_iteration_with_validation, weights_hash=batch_weights_hash)

                should_increment_epoch = False

                if self._experiment_counters.is_epoch_iteration(epoch_size):
                    self.callback.epoch_end(self._epoch, self._phase.get_average_metrics(), weights_hash=weights_hash)
                    should_increment_epoch = True

                return should_increment_epoch

            try:
                yield self._experiment_counters.get_loop(self._context_validator, generator, post_data, self._on_train_ended)
            except GeneratorDone:
                pass

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
    def epoch_loop_context(self, epochs=None, condition=None, iterable=None):
        message = '`epoch_loop` should be called with one of epochs, condition, or iterable.' \
                  ' Called with: epochs=%s, condition=%s, iterable=%s instead.' % \
                  (epochs, condition, iterable)
        self._assert_single_argument((epochs, condition, iterable), message)

        with self._context_validator.context(Context.EPOCH_LOOP):
            self._epochs = self._epoch_batch_loop_total_iterations(epochs, iterable)
            self.callback.set_hyperparams(total_epochs=self._epochs)

            generator = self._get_generator(epochs, condition, iterable)

            def post_data():
                weights_hash = self.get_weights_hash(self._train_session)

                self.callback.epoch_end(self._epoch, self._phase.get_average_metrics(), weights_hash=weights_hash)

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

    @contextmanager
    def batch_loop_context(self, batches=None, condition=None, iterable=None):
        # count arguments
        message = '`batch_loop` should be called with one of batches, condition, or iterable.' \
                  ' Called with: batches=%s, condition=%s, iterable=%s instead.' % \
                  (batches, condition, iterable)
        self._assert_single_argument((batches, condition, iterable), message)

        with self._context_validator.context(Context.BATCH_LOOP):
            epoch_size = self._epoch_batch_loop_total_iterations(batches, iterable)
            max_iterations = self._batch_loop_max_iterations(self._epochs, epoch_size)
            self.callback.set_hyperparams(epoch_size=epoch_size, max_iterations=max_iterations)

            generator = self._get_generator(batches, condition, iterable)

            def post_data():
                weights_hash = self.get_weights_hash(self._train_session) if self._is_iteration_with_validation else None

                self.callback.batch_end(
                    self._batch, self._epoch, self._phase.get_average_metrics(),
                    iteration=self._iteration,
                    is_test=self._is_iteration_with_validation,
                    weights_hash=weights_hash)

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

    def _patch_tf_session_for_train(self):
        def after_session_run(session, monitored_results):
            self._train_session = session
            self._before_train_run(session)

            self._phase.add_metrics(monitored_results, is_custom=False)

        return after_session_run

    def _update_train_validation_params(self, monitored_metrics, custom_metrics):
        monitored_fetches = monitored_metrics or {}
        monitored_fetches.update(self._monitored_fetches)

        custom_metrics = custom_metrics or {}
        custom_metrics.update(self._custom_metrics)

        return monitored_fetches, custom_metrics

    def get_average_metrics(self):
        return self._phase.get_average_metrics()

    @contextmanager
    def train(self, monitored_metrics=None, custom_metrics=None, session_instance=None):
        from .tensorflow_patch_session import TfSessionRunPatchContext

        """Marks a training context.

        This context allows the SDK to patch the `tf.Session.run` and calculate training metrics if needed.
        As such, there must be only 1 `tf.Session.run` call within this context. Otherwise, the training
        iteration might be incorrectly incremented.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """
        with self._context_validator.context(Context.TRAIN):
            self._validate_monitored_fetches(monitored_metrics)
            self._validate_custom_metrics(custom_metrics)

            monitored_fetches, custom_metrics = self._update_train_validation_params(monitored_metrics, custom_metrics)

            with TfSessionRunPatchContext(self._patch_tf_session_for_train, monitored_fetches, session_instance):
                yield

            self._phase.add_metrics(custom_metrics, is_custom=True)

    def _on_test_end(self):
        # noinspection PyProtectedMember
        self.callback._test_end()

    def _on_test_begin(self, steps, model, name=None):
        # noinspection PyProtectedMember
        weights_hash = self.get_weights_hash(model)
        # noinspection PyProtectedMember
        self.callback._test_begin(steps, weights_hash, name=name)

    def _after_test_run(self, expected, predictions, probabilities):
        # noinspection PyProtectedMember
        self.callback._test_iteration_end(expected, predictions, probabilities)

    def _update_test_params(self, monitored_metrics=None, custom_metrics=None, expected=None, predicted=None):
        monitored_fetches = monitored_metrics or {}
        if expected is not None and predicted is not None:
            monitored_fetches['expected'] = expected
            monitored_fetches['predicted'] = predicted

        return self._update_train_validation_params(monitored_fetches, custom_metrics)

    @contextmanager
    def test(self, expected=None, predicted=None, test_iterations=None, monitored_metrics=None, custom_metrics=None, session_instance=None,
             name=None):
        """
        Marks a test context.

        This context allows the SDK to patch the `tf.Session.run` and calculate test metrics if needed.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as test metrics.

        :param predicted: a tensor for predictions
        :param expected: a tensor for expected values
        :param monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
        :param custom_metrics: (Optional.) A dictionary whose values are metric functions.
        :param name: (Optional.) a string representing the test display name
        :return None
        """
        from .tensorflow_patch_session import TfSessionRunPatchContext

        with self._context_validator.context(Context.TEST):
            self._validate_monitored_fetches(monitored_metrics)
            self._validate_custom_metrics(custom_metrics)

            monitored_fetches, custom_metrics = self._update_test_params(monitored_metrics, custom_metrics, expected, predicted)

            steps = test_iterations or -1  # calc test steps if possible

            self._on_test_begin(steps, session_instance or self._train_session, name=name)

            with TfSessionRunPatchContext(self._patch_tf_session_for_test, monitored_fetches, session_instance):
                yield

            self._on_test_end()

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

    @contextmanager
    def validation(self, monitored_metrics=None, custom_metrics=None, session_instance=None):
        from .tensorflow_patch_session import TfSessionRunPatchContext

        """Marks a validation context.

        This context allows the SDK to patch the `tf.Session.run` to calculate validation metrics.
        Unlike the `train` scope, you can include multiple runs e.g. by using a for-loop looping over a
        validation dataset by batches. The SDK will average out the validation metrics across these runs
        and collect the averaged value.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """
        with self._context_validator.context(Context.VALIDATION):
            # Validate but do not throw exceptions so the experiment is not suddenly interrupted.
            self._validate_monitored_fetches(monitored_metrics, raise_exception=False)
            self._validate_custom_metrics(custom_metrics, raise_exception=False)

            monitored_fetches, custom_metrics = self._update_train_validation_params(monitored_metrics, custom_metrics)

            with TfSessionRunPatchContext(self._patch_tf_session_for_validation, monitored_fetches, session_instance):
                yield

            self._phase.add_metrics(custom_metrics, is_custom=True)

    def _patch_tf_session_for_test(self):
        def after_session_run(session, monitored_results):
            if 'expected' in monitored_results and 'predicted' in monitored_results:
                expected, predicted = monitored_results['expected'], monitored_results['predicted']
                predicted_classes = predicted
                probabilities = predicted

                expected = expected.tolist()
                if len(predicted_classes.shape) == 1:
                    predicted_classes = predicted_classes.tolist()
                else:
                    predicted_classes = np.argmax(predicted_classes, axis=1).tolist()

                if len(probabilities.shape) == 1:
                    probabilities = probabilities.tolist()
                else:
                    probabilities = np.max(probabilities, axis=1).tolist()
            else:
                expected = []
                predicted_classes = []
                probabilities = []

            self._after_test_run(expected, predicted_classes, probabilities)

        return after_session_run

    def _patch_tf_session_for_validation(self):
        def after_session_run(_session, monitored_results):
            self._phase.add_metrics(monitored_results, is_custom=False)

        return after_session_run

    def _before_train_run(self, session):
        if not self._has_started:
            self._has_started = True
            structure_hash = self._get_structure_hash(session)
            self.callback.train_begin(structure_hash=structure_hash)

    @classmethod
    def _validate_monitored_item(cls, default_graph, name, fetch):
        if not isinstance(name, six.string_types):
            raise ValueError("monitored metrics key %s is not a string" % name)

        try:
            default_graph.as_graph_element(fetch, allow_operation=False)
        except TypeError as e:
            raise TypeError('Fetch %r has invalid type %r, must be a string or Tensor. (%s)'
                            % (fetch, type(fetch), str(e)))
        except ValueError as e:
            raise ValueError('Fetch %r cannot be interpreted as a Tensor. (%s)' % (fetch, str(e)))
        except KeyError as e:
            raise ValueError('Fetch %r cannot be found in the default graph. (%s)' % (fetch, str(e)))

    def _validate_monitored_fetches(self, monitored_fetches, raise_exception=True):
        import tensorflow as tf

        if monitored_fetches is None:
            return

        if not isinstance(monitored_fetches, dict):
            raise ValueError('Fetches %s must be a dictionary.' % monitored_fetches)

        default_graph = tf.get_default_graph()

        invalid_keys = []
        for name, fetch in monitored_fetches.items():
            try:
                self._validate_monitored_item(default_graph, name, fetch)
            except (ValueError, KeyError, TypeError) as ex:
                self.logger.warning(ex)

                if raise_exception:
                    raise

                invalid_keys.append(name)

        for invalid_key_name in invalid_keys:
            del monitored_fetches[invalid_key_name]

    @staticmethod
    def _validate_custom_metrics_dict(custom_metrics):
        if custom_metrics is None:
            return

        if not isinstance(custom_metrics, dict):
            raise ValueError('Custom metrics %s must be a dictionary.' % custom_metrics)

        for name, metric_func in custom_metrics.items():
            if not isinstance(name, six.string_types):
                raise ValueError("Custom metric's key %s is not a string" % name)

            if not callable(metric_func):
                raise ValueError('Custom metric function of %s must be callable' % name)

    def _validate_custom_metrics(self, custom_metrics, raise_exception=True):
        try:
            self._validate_custom_metrics_dict(custom_metrics)
        except Exception as ex:
            self.logger.warning(ex)
            if raise_exception:
                raise

    @staticmethod
    def _loop_total_epochs(max_iterations, epoch_size):
        if not max_iterations or not epoch_size:
            return None

        return max_iterations // epoch_size

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

    # region - ModelHashInterface
    @classmethod
    def calculate_weights_hash(cls, session):
        weights = cls._get_weights(session)

        weights_hashes = []
        for weight in weights:
            weight_hash = hasharray(weight)
            weights_hashes.append(weight_hash)

        hash_key = hashcombine(*weights_hashes)
        return BaseCallback._WEIGHTS_HASH_PREFIX + hash_key

    @classmethod
    def _get_weights(cls, session):
        import tensorflow as tf

        variables = tf.trainable_variables()

        return session.run(variables)

    # noinspection PyBroadException
    def get_weights_hash(self, session):
        try:
            if session is None:
                return None

            return self.calculate_weights_hash(session)
        except Exception:
            self.logger.exception("Was not able to calculate weights hash for new TF API")
            return None

    @ModelHashInterface.wrap_all_get_structure_hash_exceptions
    def _get_structure_hash(self, session):
        import tensorflow as tf

        variables = tf.trainable_variables()
        shapes = tuple([tuple(x.get_shape().as_list()) for x in variables])
        return hash_value(shapes)

    # endregion

    def __get_tensor_from_op(self, op):
        outputs = op.outputs
        if len(outputs) > 1:
            self.logger.warning("Length of outputs of 'op' is %s", len(outputs))
        elif len(outputs) == 0:
            raise MissingLinkException("Operation node has empty 'outputs'")
        return outputs[0]

    def _get_tensor_from_name(self, model, name, by_attr, expect_many=False, return_many=False, reverse_order=True):
        name = str(name).lower()
        operations = model.graph.get_operations()
        if reverse_order:
            operations = operations[::-1]  # will start seeking from the end
        ops = [op for op in operations if str(getattr(op, by_attr)).lower() == name]
        if len(ops) > 1 and not expect_many:
            self.logger.warning("Unexpected length of ops %s retrieved by op.%s=%s", len(ops), by_attr, name)
        elif len(ops) == 0:
            self.logger.warning("No op found by op.%s=%s", by_attr, name)
            return None
        if return_many:
            tensors = [self.__get_tensor_from_op(i) for i in ops]
            return tensors
        single_op = ops[0]
        tensor = self.__get_tensor_from_op(single_op)
        return tensor

    def _determine_input_placeholder(self, model):
        input_placeholder = self._properties.get("__input_placeholder")
        if input_placeholder is not None:
            return input_placeholder
        pl_name = self._properties.get("input_placeholder")
        if pl_name is not None:
            pl = self._get_tensor_from_name(model, pl_name, "name", reverse_order=False)
        else:
            pl = self._get_tensor_from_name(model, "placeholder", "type", reverse_order=False)
        if pl is None:
            message = "Cannot infer placeholder for input data. " \
                      "Please use 'set_properties' and specify 'input_placeholder'. " \
                      "e.g. experiment.set_properties(input_placeholder=X)"
            self.logger.error(message)
            raise MissingLinkException(message)
        self._properties["__input_placeholder"] = pl  # note: here we save a placeholder instance, not a name
        return pl

    def _get_input_dim(self, model):
        pl = self._determine_input_placeholder(model)
        try:
            shape = pl.shape.as_list()
        except ValueError as ex:
            self.logger.exception(ex)
            raise MissingLinkException("Was not able to determine input shape. Please set it via set_properties!")
        shape = shape[1:]  # excluding batch size
        h, w, d = shape
        shape = (d, h, w)  # shape has to be in format: depth, height, width regardless of framework ordering
        return shape

    def _get_prediction(self, model, image, shape=None):
        input_, depth, height, width = self._get_scaled_input(image, shape)
        output_layer_name = self._properties.get("output_layer")
        if output_layer_name is not None:
            output_layer = self._get_tensor_from_name(model, output_layer_name, "name")
        else:
            output_layer = self._get_tensor_from_name(model, "softmax", "type")
        if output_layer is None:
            raise MissingLinkException("Please provide output operation via set_properties. "
                                       "e.g. experiment.set_properties(output_layer='softmax')")
        self._properties["__output_layer"] = output_layer
        input_placeholder = self._determine_input_placeholder(model)
        probs = model.run(output_layer, feed_dict={input_placeholder: np.array([input_])})
        probs = np.squeeze(probs)
        return input_, probs

    def _get_activation_and_grad_for_last_conv(self, model, scores, input_=None):
        import tensorflow as tf

        last_conv_layer_name = self._properties.get("last_conv_layer")
        if last_conv_layer_name:
            last_conv = self._get_tensor_from_name(model, last_conv_layer_name, "name")
        else:
            last_conv = self._get_tensor_from_name(model, "conv2d", "type", expect_many=True)
        if last_conv is None:
            raise MissingLinkException("Cannot determine last convolutional layer. Try to provide name of last conv "
                                       "layer explicitly via set_properties. "
                                       "e.g. experiment.set_properties(last_conv_layer='conv5_3/conv2d')")
        output_layer = self._properties["__output_layer"]
        input_placeholder = self._determine_input_placeholder(model)

        signal = tf.multiply(output_layer, scores)
        loss = tf.reduce_mean(signal)
        grads = tf.gradients(loss, last_conv)[0]
        normalize_grads = tf.div(grads, tf.sqrt(tf.reduce_mean(tf.square(grads))) + tf.constant(1e-5))
        output, grads_val = model.run([last_conv, normalize_grads], feed_dict={input_placeholder: np.array([input_])})

        grads_val = grads_val[0]
        a_weights = np.mean(grads_val, axis=(0, 1))
        return output, a_weights

    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NHWC, expected_class=None, keep_origin=False, description=None):
        try:
            images_data, top = self._generate_grad_cam(
                model, uri=uri, input_array=input_array, top_classes=top_classes, top_images=top_images,
                class_mapping=class_mapping, dim_order=dim_order, logger=self.logger)
        except MissingLinkException:
            self.logger.exception("Was not able to produce GradCAM images because of internal error!")
        else:
            # noinspection PyProtectedMember
            images = self.callback._prepare_images_payload(images_data, keep_origin, uri)
            # noinspection PyProtectedMember
            meta = self.callback._get_toplevel_metadata(self.callback._test_token, AlgorithmTypes.GRAD_CAM, uri)
            extra = {
                "expected_class": expected_class,
                "top": top,
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.callback.upload_images(model_hash, images, meta, description=description)

    def _get_feature_maps(self, model, image, shape=None):
        input_, depth, height, width = self._get_scaled_input(image, shape)
        output_layer_name = self._properties.get("output_layer")
        if output_layer_name is None:
            raise MissingLinkException("Please provide 'output_layer' via set_properties.")
        output_layer = self._get_tensor_from_name(model, output_layer_name, "name")
        if output_layer is None:
            raise MissingLinkException("Was not able to find op named %s" % output_layer_name)

        all_conv = self._get_tensor_from_name(model, "conv2d", "type", expect_many=True, return_many=True,
                                              reverse_order=False)
        if len(all_conv) == 0:
            raise MissingLinkException("Was not able to determine Conv2D layers in the network. "
                                       "Make sure you have some.")
        input_placeholder = self._determine_input_placeholder(model)
        all_conv.append(output_layer)
        result = model.run(all_conv, feed_dict={input_placeholder: np.array([input_])})
        maps = result[:-1]
        output = result[-1]
        return maps, output

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NHWC,
                         expected_output=None, keep_origin=False, description=None):
        try:
            result = self._visual_back_prop(model, uri=uri, input_val=input_val, dim_order=dim_order,
                                            logger=self.logger)
        except MissingLinkException:
            self.logger.exception("Was not able to generate image with VisualBackProp because of internal error!")
        else:
            # noinspection PyProtectedMember
            images = self.callback._prepare_images_payload(result, keep_origin, uri)
            # noinspection PyProtectedMember
            meta = self.callback._get_toplevel_metadata(self.callback._test_token, AlgorithmTypes.VISUAL_BACKPROP, uri)
            extra = {
                "expected_output": expected_output
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.callback.upload_images(model_hash, images, meta, description=description)


class ContextValidator(BaseContextValidator):
    """
    This class validates if we can enter or exit a context.
    """

    def __init__(self, logger):
        super(ContextValidator, self).__init__(logger)

    def _validate_test_context(self):
        cant_enter_test_context = \
            not self._contexts or self.last_context not in [Context.EXPERIMENT, Context.LOOP, Context.EPOCH_LOOP,
                                                            Context.BATCH_LOOP]
        if cant_enter_test_context:
            self._logger.warning('cannot enter `test` context. Last context is %s', self.last_context)

    def _validate_train_context(self):
        if not self._contexts or self.last_context not in [Context.LOOP, Context.BATCH_LOOP]:
            raise MissingLinkException('`train` context must be nested immediately in an `loop` '
                                       'or `batch_loop` generator.')

    def _validate_validation_context(self):
        if not self._contexts or self.last_context not in [Context.LOOP, Context.EPOCH_LOOP, Context.BATCH_LOOP]:
            # Do not raise exception because we don't want to halt the experiment halfway
            self._logger.error('`validation` context must be nested immediately in a `loop` '
                               'or `epoch_loop` or `batch_loop` generator. This context is ignored')
