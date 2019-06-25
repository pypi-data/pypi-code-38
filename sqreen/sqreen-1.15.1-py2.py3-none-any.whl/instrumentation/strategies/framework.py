# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Base framework strategy
"""
import logging

from .import_hook import BaseStrategy

LOGGER = logging.getLogger(__name__)


class HookpointMismatchError(Exception):
    """ Raised when a callback is trying to be added for a strategy and their
    hookpoint are not the same
    """

    pass


class FrameworkStrategy(BaseStrategy):
    """ Specific strategy for framework instrumentation. They hook on atrributes
    defined in the class, MODULE_NAME, HOOK_CLASS, HOOK_METHOD. They wrap the
    resulting object with self.wrapper by passing original as first argument and
    a middleware for the correct framework as second argument
    """

    MODULE_NAME = None
    HOOK_CLASS = None
    HOOK_METHOD = None

    def __init__(
        self,
        strategy_key,
        observation_queue,
        queue,
        import_hook,
        before_hook_point=None,
    ):
        super(FrameworkStrategy, self).__init__(
            observation_queue, queue, import_hook, before_hook_point
        )
        self.strategy_key = strategy_key

        # These values should be defined by subclasses
        self.middleware = None
        self.wrapper = None

    def add_callback(self, callback):
        """ Add a callback on a specific endpoint defined by the couple
        (hook_module, hook_name) embedded in callback
        """

        # Check that callback hookpoint and strategy hookpoint match
        strategy_module = "{}::{}".format(self.MODULE_NAME, self.HOOK_CLASS)
        mismatch_module = callback.hook_module != strategy_module
        mismatch_method = callback.hook_name != self.HOOK_METHOD
        if mismatch_module or mismatch_method:
            err_msg = "Callback hookpoint ({}, {}) doesn't match strategy callback ({}, {})"
            msg = err_msg.format(
                callback.hook_module,
                callback.hook_name,
                strategy_module,
                self.HOOK_METHOD,
            )
            raise HookpointMismatchError(msg)

        super(FrameworkStrategy, self).add_callback(callback)

    def hook(self):
        """
        Once hooked, the middleware will call the callbacks at the right moment.
        """

        # Check if we already hooked at
        if not self.hooked:
            self.import_hook.register_patcher(
                self.MODULE_NAME,
                self.HOOK_CLASS,
                self.HOOK_METHOD,
                self.import_hook_callback,
            )

            self.hooked = True

    def import_hook_callback(self, original):
        """ Monkey-patch the object located at hook_class.hook_name on an
        already loaded module
        """
        return self.wrapper(original, self.middleware)

    @classmethod
    def get_strategy_id(cls, callback):
        """ This strategy only hook on
        (cls.MODULE_NAME::cls.HOOK_CLASS, cls.HOOK_METHOD)
        """
        return (
            "{}::{}".format(cls.MODULE_NAME, cls.HOOK_CLASS),
            cls.HOOK_METHOD,
        )

    def _restore(self):
        """ The hooked module will always stay hooked
        """
        pass
