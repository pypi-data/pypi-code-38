# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Import hook strategy to prepare hooks for modules
"""
import logging

from ..hook_point import hook_point
from .base import BaseStrategy

LOGGER = logging.getLogger(__name__)


def parse_hook_module(hook_module):
    """ Parse a hook_module and split it into two parts

    >>> parse_hook_module('django.core.handlers.base::BaseHandler')
    ['django.core.handlers.base', 'BaseHandler']
    >>> parse_hook_module('django.core.handlers.base')
    ['django.core.handlers.base', None]
    """
    if "::" in hook_module:
        return hook_module.split("::", 1)
    else:
        return [hook_module, None]


class ImportHookStrategy(BaseStrategy):
    """ Simple strategy that calls setattr(hook_module, hook_name, callback)
    """

    def __init__(
        self,
        strategy_key,
        observation_queue,
        queue,
        import_hook,
        before_hook_point=None,
    ):
        super(ImportHookStrategy, self).__init__(
            observation_queue, queue, import_hook, before_hook_point
        )
        self.strategy_key = strategy_key

        self.hook_path = strategy_key[0]
        self.hook_module, self.hook_class = parse_hook_module(self.hook_path)
        self.hook_name = strategy_key[1]

    def hook(self):
        """ Insert the import hook
        """
        if self.hooked is False:
            self.import_hook.register_patcher(
                self.hook_module,
                self.hook_class,
                self.hook_name,
                self.import_hook_callback,
            )

            self.hooked = True
        else:
            LOGGER.warning(
                "Trying to hook several times the module %s", self.hook_module
            )

    def import_hook_callback(self, original):
        """ Monkey-patch the object located at hook_class.hook_name on an
        already loaded module. Called by ImportHook
        """
        return hook_point(self, self.hook_path, self.hook_name, original)

    @staticmethod
    def get_strategy_id(callback):
        """ Return the tuple (callback.hook_module, callback.hook_name) as
        identifier for this strategy
        """
        return (callback.hook_module, callback.hook_name)

    def _restore(self):
        """ The hooked module will always stay hooked
        """
        pass
