# -*- coding: utf-8 -*-
import threading
import types
import copy
from .base_callback import BaseCallback

_TF_PATCHED_RUN = {}


class TfSessionRunPatchContext(object):
    def __init__(self, patcher_method, monitored_fetches, session_instance):
        self._patcher_method = patcher_method
        self._monitored_fetches = monitored_fetches
        self._session_instance = session_instance
        self._patched_thread = threading.currentThread()

    @classmethod
    def _generate_unique_key(cls, existing_keys):
        while True:
            key = BaseCallback.generate_tag()
            if key not in existing_keys:
                return key

    @classmethod
    def _run_session(cls, monitored_fetches, session, fetches, feed_dict=None, options=None, run_metadata=None):
        all_fetches = copy.copy(monitored_fetches)

        key_for_unmonitored_fetches = cls._generate_unique_key(all_fetches.keys())
        all_fetches[key_for_unmonitored_fetches] = fetches

        monitored_results = cls._run_session_original_method(session, all_fetches, feed_dict, options, run_metadata)

        unmonitored_results = monitored_results.pop(key_for_unmonitored_fetches, {})

        return monitored_results, unmonitored_results

    @classmethod
    def _run_session_original_method(cls, session, fetches, feed_dict=None, options=None, run_metadata=None):
        patched_method = _TF_PATCHED_RUN.get(session)
        if patched_method is not None:
            return patched_method(fetches, feed_dict, options, run_metadata)

        patched_method = _TF_PATCHED_RUN.get(type(session))
        if patched_method is not None:
            return patched_method(session, fetches, feed_dict, options, run_metadata)

        raise KeyError('Session not patched')

    @classmethod
    def _patch_run_classes(cls, check_calling_thread):
        import tensorflow as tf

        for klass in (tf.Session, tf.InteractiveSession):
            _TF_PATCHED_RUN[klass] = klass.run
            klass.run = check_calling_thread

    @classmethod
    def _patch_run_instance(cls, session_instance, check_calling_thread):
        if session_instance in _TF_PATCHED_RUN:
            return

        _TF_PATCHED_RUN[session_instance] = session_instance.run
        session_instance.run = types.MethodType(check_calling_thread, session_instance)

    def _unpatch_run(self, klasses):
        for klass in klasses:
            if klass not in _TF_PATCHED_RUN:
                continue

            klass.run = _TF_PATCHED_RUN[klass]
            del _TF_PATCHED_RUN[klass]

        if self._session_instance is not None:
            self._session_instance.run = _TF_PATCHED_RUN[self._session_instance]

    def __enter__(self):
        after_session_run_method = self._patcher_method()

        def check_calling_thread(session, fetches, feed_dict=None, options=None, run_metadata=None):
            if self._patched_thread != threading.currentThread():
                return self._run_session_original_method(session, fetches, feed_dict, options, run_metadata), None

            monitored_results, unmonitored_results = self._run_session(self._monitored_fetches, session, fetches, feed_dict, options, run_metadata)
            after_session_run_method(session, monitored_results)

            return unmonitored_results

        if self._session_instance is None:
            self._patch_run_classes(check_calling_thread)
        else:
            self._patch_run_instance(self._session_instance, check_calling_thread)

        return self

    def __exit__(self, *exc):
        self._reset_tf_session()

    def _reset_tf_session(self):
        import tensorflow as tf

        if self._session_instance is None:
            self._unpatch_run((tf.Session, tf.InteractiveSession))
        else:
            self._unpatch_run(())
