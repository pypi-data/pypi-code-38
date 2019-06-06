# -*- coding: utf-8 -*-
import time
import warnings

import numpy as np

from .settings import MetricTypePrefixes
from .queries import QueriesStore
from .logger_wrapper import LoggerWrapper


class Phase(object):
    def __init__(self, prefix, queries=None):
        self._metrics = {}
        self._prefix = prefix
        self._queries = QueriesStore()
        self._logger = LoggerWrapper()

        if queries is not None:
            self._queries.add_query_objects(queries)

    @property
    def prefix(self):
        return self._prefix

    @property
    def metrics_raw(self):
        return self._metrics

    def __add_metric_raw(self, name, value, total=1, apply_prefix=True):
        prefixed_name = self.prefixed_metric(name) if apply_prefix else name
        total_val, total_count = self._metrics.setdefault(prefixed_name, (0, 0))

        if callable(value):
            value = value()

        self._metrics[prefixed_name] = (total_val + value, total_count + total)

    def add_metric(self, name, value, is_custom=True):
        if is_custom:
            name = MetricTypePrefixes.CUSTOM + name

        self.__add_metric_raw(name, value, 1)

    def update_metrics_from_phase(self, phase):
        for name, total_count in phase.metrics_raw.items():
            val, total = total_count
            self.__add_metric_raw(name, val, total, apply_prefix=False)

    def update_queries_from_phase(self, phase):
        phase_query_objects = phase.get_query_objects()
        if len(phase_query_objects) > 0:
            self._queries.add_query_objects(phase_query_objects)

    def add_metrics(self, metrics, is_custom=True):
        for name, value in metrics.items():
            self.add_metric(name, value, is_custom)

    def prefixed_metric(self, name):
        if not self._prefix:
            return name

        return self._prefix + name

    def get_average_metrics(self):
        def div_(a, b):
            if b == 1:
                return a

            return a / b

        return {name: div_(*total_count) for name, total_count in self._metrics.items()}

    def reset(self):
        self._metrics = {}

    def use_data_generator(self, ml_data_generator):
        self._queries.add_query(ml_data_generator.query, ml_data_generator.volume_id)

    def get_queries_data(self):
        return self._queries.get_all()

    def get_query_objects(self):
        return self._queries.get_all_query_obj()


class PhaseEpoch(Phase):
    def __init__(self, prefix, epoch=None):
        super(PhaseEpoch, self).__init__(prefix)
        self.epoch = epoch


class PhaseTest(Phase):
    def __init__(self, prefix):
        super(PhaseTest, self).__init__(prefix)

        self.y_test = []
        self.y_pred = []
        self.labels = []

    @classmethod
    def _make_list(cls, name, lst):
        if lst is None:
            return lst

        if isinstance(lst, np.ndarray):
            lst = lst.tolist()

        if not isinstance(lst, (tuple, list)):
            raise ValueError('not supported type for %s %s' % (name, lst))

        return lst

    def set_test_data(self, y_test, y_pred, labels):
        warnings.warn("This method is deprecated use add_test_data instead", DeprecationWarning)
        self.labels = labels
        return self.add_test_data(y_test, y_pred)

    def set_labels(self, labels):
        self.labels = labels

    def add_test_data(self, y_test, y_pred):
        self.y_test.extend(self._make_list('y_test', y_test))
        self.y_pred.extend(self._make_list('y_pred', y_pred))

    def get_query_data(self):
        return self._queries.get_first()

    def use_data_generator(self, ml_data_generator):
        if not self._queries.is_empty:
            self._logger.warning("More than one iterator was used in a single test scope. "
                                 "Only the first iterator's query will be associated with the test")

        super(PhaseTest, self).use_data_generator(ml_data_generator)


class _HookTimer(object):
    """Base timer for determining when Hooks should trigger.

    Should not be instantiated directly.
    """

    def __init__(self):
        pass

    def reset(self):
        """Resets the timer."""
        pass

    def should_trigger_for_step(self, step):
        """Return true if the timer should trigger for the specified step."""
        raise NotImplementedError

    def update_last_triggered_step(self, step):
        """Update the last triggered time and step number.

        Args:
          step: The current step.

        Returns:
          A pair `(elapsed_time, elapsed_steps)`, where `elapsed_time` is the number
          of seconds between the current trigger and the last one (a float), and
          `elapsed_steps` is the number of steps between the current trigger and
          the last one. Both values will be set to `None` on the first trigger.
        """
        raise NotImplementedError

    def last_triggered_step(self):
        """Returns the last triggered time step or None if never triggered."""
        raise NotImplementedError


class SecondOrStepTimer(_HookTimer):
    """Timer that triggers at most once every N seconds or once every N steps.
    """

    def __init__(self, every_secs=None, every_steps=None):
        self.reset()
        self._every_secs = every_secs
        self._every_steps = every_steps
        self._last_triggered_step = None
        self._last_triggered_time = None

        if self._every_secs is None and self._every_steps is None:
            raise ValueError("Either every_secs or every_steps should be provided.")
        if (self._every_secs is not None) and (self._every_steps is not None):
            raise ValueError("Can not provide both every_secs and every_steps.")

        super(SecondOrStepTimer, self).__init__()

    def reset(self):
        self._last_triggered_step = None
        self._last_triggered_time = None

    def should_trigger_for_step(self, step):
        """Return true if the timer should trigger for the specified step.

        Args:
          step: Training step to trigger on.

        Returns:
          True if the difference between the current time and the time of the last
          trigger exceeds `every_secs`, or if the difference between the current
          step and the last triggered step exceeds `every_steps`. False otherwise.
        """
        if self._last_triggered_step is None:
            return True

        if self._last_triggered_step == step:
            return False

        if self._every_secs is not None:
            if time.time() >= self._last_triggered_time + self._every_secs:
                return True

        if self._every_steps is not None:
            if step >= self._last_triggered_step + self._every_steps:
                return True

        return False


class GeneratorDone(Exception):
    pass


class ExperimentCounters(object):
    def __init__(self, every_n_secs=None, every_n_iter=None):
        self._iteration = 0
        self._batch = 0
        self._epoch = 0
        self._timer = self._init_timer(every_n_secs, every_n_iter)

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
        return SecondOrStepTimer(every_secs=every_n_secs, every_steps=every_n_iter) if every_n_secs or every_n_iter else cls.AlwaysTriggerTimer()

    def is_epoch_iteration(self, epoch_size):
        if epoch_size is None:
            return False

        return self._iteration % epoch_size == 0

    def get_loop(self, context_validator, generator, post_data, loop_finished):
        should_increment_epoch = True
        # when the loop finishes we don't want it to be reset just yet
        # as we want that loop_finished will have access to the metrics
        should_reset = False

        for result in generator:
            if should_reset:
                context_validator.step_finished()

            self._iteration += 1
            self._batch += 1
            if should_increment_epoch:
                self._epoch += 1
                self._batch = 1
                should_increment_epoch = False

            yield result

            if self._timer.should_trigger_for_step(self._iteration):
                should_increment_epoch = post_data()
                self._timer.update_last_triggered_step(self._iteration)

            should_reset = True

        if loop_finished is not None:
            loop_finished()

        context_validator.step_finished()

        raise GeneratorDone()

    def get_epoch_loop(self, context_validator, generator, post_data, loop_finished):
        should_reset = False

        for result in generator:
            if should_reset:
                context_validator.step_finished()

            self._epoch += 1
            self._batch = 0

            yield result

            post_data()

            should_reset = True

        loop_finished()
        context_validator.step_finished()

        raise GeneratorDone()

    def get_batch_loop(self, context_validator, generator, post_data):
        should_reset = False

        for result in generator:
            if should_reset:
                context_validator.step_finished()

            self._iteration += 1
            self._batch += 1

            yield result

            if self._timer is None or self._timer.should_trigger_for_step(self._iteration):
                post_data()

            should_reset = True

        raise GeneratorDone()
