# -*- coding: utf-8 -*-
from __future__ import absolute_import
from contextlib import contextmanager

from .queries import QueriesStore
from .exceptions import MissingLinkException, ExperimentStopped
from .phase import ExperimentCounters, GeneratorDone, PhaseEpoch
from .utilities.utils import ZeroIndexedGenerators
from .base_callback import BaseCallback, BaseContextValidator, Context


class VanillaProject(BaseCallback):
    def __init__(self, owner_id=None, project_token=None, stopped_callback=None, **kwargs):
        super(VanillaProject, self).__init__(
            owner_id, project_token, stopped_callback=stopped_callback, framework='vanilla', **kwargs)
        self.token = project_token

    def _enter_experiment(self):
        pass

    @contextmanager
    def experiment(
            self,
            display_name=None,
            description=None,
            class_mapping=None,
            hyperparams=None,
            metrics=None,
            stopped_callback=None):

        if metrics is None:
            metrics = {}

        self.set_properties(display_name=display_name, description=description, class_mapping=class_mapping)
        self._enter_experiment()

        if hyperparams is not None:
            self.set_hyperparams(**hyperparams)

        self.stopped_callback = stopped_callback or self.stopped_callback

        contextless_queries = self.get_query_objects()

        with VanillaExperiment(self, metrics, queries=contextless_queries) as experiment:
            try:
                yield experiment
            except ExperimentStopped:
                experiment_queries = experiment.get_queries_data()

                # noinspection PyProtectedMember
                experiment._on_train_ended(queries=experiment_queries)

                self._handle_stopped()


class VanillaExperiment(object):
    def __init__(self, project, every_n_secs=None, every_n_iter=None, queries=None):
        self._project = project
        self._current_epoch = 0
        self._params = {}
        self._context_validator = ContextValidator(self._project.logger)
        self._experiment_counters = ExperimentCounters(every_n_secs, every_n_iter)
        self._epochs = None
        self._queries = QueriesStore()

        if queries is not None:
            self._queries.add_query_objects(queries)

    def __enter__(self):
        self._context_validator.enter(Context.EXPERIMENT)

        # noinspection PyNoneFunctionAssignment
        structure_hash = self._get_structure_hash()
        self._project.train_begin({}, structure_hash=structure_hash)

        return self

    def __exit__(self, *exc):
        self._context_validator.exit(Context.EXPERIMENT)

        return False

    def log_metric(self, name, value):
        self._phase.add_metric(name, value, is_custom=True)

    def get_average_metrics(self):
        return self._context_validator.get_average_metrics()

    def __start_new_xp_if_needed(self):
        if not self._project.has_experiment:
            self._project.new_experiment()

    @contextmanager
    def train(self):
        self.__start_new_xp_if_needed()

        with self._context_validator.context(Context.TRAIN, queries=self._queries.get_all_query_obj()):

            try:
                yield self._phase
            finally:
                self._queries.add_query_objects(self._phase.get_query_objects())

            queries_data = self._phase.get_queries_data()

            # noinspection PyProtectedMember
            self._project._train_end(data_management=queries_data)

    @contextmanager
    def validation(self):
        with self._context_validator.context(Context.VALIDATION):
            yield

    @contextmanager
    def test(self, steps=None, name=None):
        self.__start_new_xp_if_needed()

        with self._context_validator.context(Context.TEST):
            self._on_test_begin(steps, name)

            yield self._phase

            query_data = self._phase.get_query_data()
            self._on_test_end(self._phase.labels, query_data=query_data)

    def _on_enter_loop(self, iterable):
        pass

    # noinspection PyMethodMayBeStatic
    def _get_weights_hash(self):
        return None

    # noinspection PyMethodMayBeStatic
    def _get_structure_hash(self):
        return None

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
        self.__assert_single_argument((max_iterations, condition, iterable), message)

        with self._context_validator.context(Context.LOOP):
            self._project.set_hyperparams(
                max_iterations=max_iterations,
                epoch_size=epoch_size,
                total_epochs=self._total_epochs(max_iterations, epoch_size))

            self._on_enter_loop(iterable)

            # In the case of multiple loops on the same experiment,
            # you might expect index to start at `self._iteration - 1`,
            # so the index of the loops keeps incrementing from loop to loop.
            # However, we decided to keep it this way, to keep on consistency with the `range` function.
            generator = self._choose_generator(max_iterations, condition, iterable)

            def post_data():
                is_epoch_iteration = self._experiment_counters.is_epoch_iteration(epoch_size)

                weights_hash = self._get_weights_hash() \
                    if self._is_iteration_with_validation or is_epoch_iteration else None

                batch_weights_hash = weights_hash if self._is_iteration_with_validation else None

                self._project.batch_end(
                    self._batch, self._epoch,
                    self.get_average_metrics(),
                    iteration=self._iteration,
                    weights_hash=batch_weights_hash,
                    is_test=self._is_iteration_with_validation)

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
        self.__assert_single_argument((batches, condition, iterable), message)

        with self._context_validator.context(Context.BATCH_LOOP):
            epoch_size = self._epoch_batch_loop_total_iterations(batches, iterable)
            max_iterations = self._batch_loop_max_iterations(self._epochs, epoch_size)
            self._project.set_hyperparams(epoch_size=epoch_size, max_iterations=max_iterations)

            # noinspection PyProtectedMember
            self._on_enter_loop(iterable)

            generator = self._choose_generator(batches, condition, iterable)

            def post_data():
                weights_hash = self._get_weights_hash() if self._is_iteration_with_validation else None

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
    def epoch(self, epoch):
        with self._context_validator.context(Context.EPOCH_LOOP, epoch=epoch):
            # noinspection PyNoneFunctionAssignment
            yield
            weights_hash = self._get_weights_hash()

            self._project.epoch_end(
                epoch,
                self.get_average_metrics(),
                weights_hash=weights_hash)

    @contextmanager
    def batch(self, iteration, batch=None, epoch=None):
        epoch = self._phase.epoch if isinstance(self._phase, PhaseEpoch) else epoch

        with self._context_validator.context(Context.BATCH_LOOP):
            yield
            self._project.batch_end(
                batch or iteration,
                epoch or 1,
                self.get_average_metrics(),
                iteration=iteration)

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
        self.__assert_single_argument((epochs, condition, iterable), message)

        with self._context_validator.context(Context.EPOCH_LOOP):
            self._epochs = self._epoch_batch_loop_total_iterations(epochs, iterable)
            self._project.set_hyperparams(total_epochs=self._epochs)

            self._on_enter_loop(iterable)

            generator = self._choose_generator(epochs, condition, iterable)

            def post_data():
                # noinspection PyNoneFunctionAssignment
                weights_hash = self._get_weights_hash()

                self._project.epoch_end(self._epoch, self.get_average_metrics(), weights_hash=weights_hash)

            try:
                yield self._experiment_counters.get_epoch_loop(self._context_validator, generator, post_data, self._on_train_ended)
            except GeneratorDone:
                pass

    def _on_train_ended(self, queries=None):
        data = {
            'iterations': self._iteration,
            'metricData': self.get_average_metrics(),
        }

        if queries is not None:
            data['data_management'] = queries

        # noinspection PyProtectedMember
        self._project._train_end(**data)

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

    def _is_last_batch(self, batch):
        if 'samples' not in self._params or 'batch_size' not in self._params:
            return False

        batches = self._params['samples'] / self._params['batch_size']
        return batch == batches - 1

    def _is_last_epoch(self, epoch):
        return epoch == self._params['epochs'] - 1

    @staticmethod
    def _total_epochs(max_iterations, epoch_size):
        if not max_iterations or not epoch_size:
            return None

        return max_iterations // epoch_size

    def _on_test_begin(self, steps, name=None):
        # noinspection PyNoneFunctionAssignment
        weights_hash = self._get_weights_hash()

        # noinspection PyProtectedMember
        self._project._test_begin(steps, weights_hash, name=name)

    def _on_test_end(self, labels, query_data=None):
        # noinspection PyProtectedMember
        self._project._test_iteration_end(
            self._phase.y_test, self._phase.y_pred, None, is_finished=True, metric_data=self.get_average_metrics(),
            class_mapping=self._project._convert_class_mapping(labels), query_data=query_data)

    @staticmethod
    def _choose_generator(iterations, condition, iterable):
        if iterations is not None:
            return ZeroIndexedGenerators.range_generator(iterations)

        if condition is not None:
            return ZeroIndexedGenerators.condition_generator(condition)

        if iterable is not None:
            return ZeroIndexedGenerators.iterable_generator(iterable)

        raise MissingLinkException('Provide batches, condition or iterable to batch_loop.')

    @property
    def _phase(self):
        return self._context_validator.last_phase

    @staticmethod
    def _batch_loop_max_iterations(epochs, epoch_size):
        try:
            return epochs * epoch_size
        except TypeError:
            return None

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

    @classmethod
    def __assert_single_argument(cls, args, error_message=''):
        # count arguments
        args_count = len([arg for arg in args if arg is not None])

        if args_count != 1:
            raise MissingLinkException('Bad Arguments: ' + error_message)

    @property
    def _is_iteration_with_validation(self):
        return self._context_validator.is_iteration_with_validation

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

    def get_queries_data(self):
        return self._queries.get_all()


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
