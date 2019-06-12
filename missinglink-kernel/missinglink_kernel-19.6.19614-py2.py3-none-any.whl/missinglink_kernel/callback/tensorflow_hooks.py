# -*- coding: utf-8 -*-
import tensorflow as tf

try:
    from contextlib import contextmanager, ExitStack
except ImportError:
    # noinspection PyUnresolvedReferences
    from contextlib2 import contextmanager, ExitStack


class TensorFlowRunHook(tf.train.SessionRunHook):
    def __init__(self, context_generator):
        self._experiment = None
        self._loop_iter = None
        self._context_generator = context_generator
        self._stacks = ExitStack()

    def begin(self):
        pass

    # pylint: disable=unused-argument
    def end(self, session):
        self._stacks.close()

    # pylint: disable=unused-argument
    def after_create_session(self, session, coord):
        for cm in self._context_generator(session):
            value = self._stacks.enter_context(cm)

            try:
                is_iter = iter(value) is not None
            except TypeError:
                is_iter = False

            if is_iter:
                self._loop_iter = value

    def before_run(self, run_context):
        pass

    def after_run(self, run_context, run_values):
        if self._loop_iter is not None:
            next(self._loop_iter)


class EstimatorsHooks(object):
    def __init__(
            self,
            project,
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
        self._stacks = ExitStack()
        self._project = project

        experiment_cm = self._project.create_experiment(
            display_name,
            description,
            class_mapping,
            optimizer,
            hyperparams,
            monitored_metrics,
            custom_metrics,
            stopped_callback,
            every_n_iter=every_n_iter,
            every_n_secs=every_n_secs,
        )

        self._experiment = self._stacks.enter_context(experiment_cm)

    def create_test_hook(
            self, monitored_metrics=None, custom_metrics=None,
            expected=None, predicted=None):
        def after_create_session_for_test(session):
            yield self._experiment.test(
                expected, predicted, monitored_metrics,
                custom_metrics, session_instance=session)

        return TensorFlowRunHook(after_create_session_for_test)

    def create_validation_hook(self, monitored_metrics=None, custom_metrics=None):
        def after_create_session_for_validation(session):
            yield self._experiment.validation(monitored_metrics, custom_metrics, session)

        return TensorFlowRunHook(after_create_session_for_validation)

    def create_train_hook(self, train_steps, monitored_metrics=None, custom_metrics=None):
        def after_create_session_for_train(session):
            yield self._experiment.loop_context(max_iterations=train_steps)
            yield self._experiment.train(
                monitored_metrics=monitored_metrics, custom_metrics=custom_metrics,
                session_instance=session)

        return TensorFlowRunHook(after_create_session_for_train)
