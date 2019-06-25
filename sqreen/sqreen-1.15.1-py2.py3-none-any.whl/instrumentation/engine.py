# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Instrumentation helper responsible for adding dynamic callback
"""
import logging
import sys

from ..remote_exception import RemoteException
from ..utils import HAS_ASYNCIO
from .import_hook import ModuleFinder
from .strategies import (
    DBApi2Strategy,
    DjangoStrategy,
    FlaskStrategy,
    ImportHookStrategy,
    Psycopg2Strategy,
    PyramidStrategy,
)

if HAS_ASYNCIO:
    from .strategies import (
        AioHTTPHookStrategy,
        AioHTTPInstallStrategy,
        AsyncEventLoopStrategy,
        AsyncImportHookStrategy,
    )

LOGGER = logging.getLogger(__name__)


class Instrumentation(object):
    """ The instrumentation class is the exposed face of the
    instrumentation engine. It dispatchs to the right strategy,
    the default one is set_attr.

    The instrumentation class takes attack queue and observation queue as parameters.

    The instrument class dispatch to different strategies based on strategy
    name defined in callback. It ask stategy for an unique id based on hook path
    infos and ensure to have only one strategy instance per id. It's needed
    for DBApi2 strategy where every sqlite3 callbacks will be stored in the same
    strategy to avoid double-instrumentation.

    It also instantiate a global ImportHook that strategy will register
    against when hooking.

    TODO:
        - Store callbacks in a single callback tree
        - Transform the remaining strategies into stateless patchers
    """

    def __init__(self, observation_queue, queue, before_hook_point=None):
        self.observation_queue = observation_queue
        self.queue = queue
        self.strategies = {}
        self.before_hook_point = before_hook_point
        self.import_hook = ModuleFinder()
        self.enabled = False

    def add_callback(self, callback):
        """ Add a callback. The callback defines itself where it should
        hook to and the strategy use for hooking (set_attr or DBApi2)
        """
        try:
            strategy_class = self._get_strategy_class(callback.strategy)

            # Get the strategy id
            strategy_id = strategy_class.get_strategy_id(callback)

            # Check if we already have a strategy
            if strategy_id in self.strategies:
                strategy_instance = self.strategies[strategy_id]
                LOGGER.debug(
                    "Reusing strategy %s for id %s",
                    strategy_instance,
                    strategy_id,
                )
            else:
                strategy_instance = strategy_class(
                    strategy_id,
                    self.observation_queue,
                    self.queue,
                    self.import_hook,
                    self.before_hook_point,
                )
                LOGGER.debug(
                    "Instantiate strategy %s for id %s -> %s",
                    strategy_class,
                    strategy_id,
                    strategy_instance,
                )
                self.strategies[strategy_id] = strategy_instance

            strategy_instance.add_callback(callback)
        except Exception:
            # If the strategy fails to hook either at instantiation
            # or hook method, catch the exception and log it
            LOGGER.exception(
                "Callback %r fails to hook", callback, exc_info=True
            )

            # And send the exception back to the backend
            infos = {"callback": callback.__dict__}
            remote_exception = RemoteException(sys.exc_info(), infos)
            self.queue.put(remote_exception)

    def deinstrument(self, callback):
        """ Deactive instrumentation on the callback endpoint
        """
        strategy_class = self._get_strategy_class(callback.strategy)

        # Get the strategy id
        strategy_id = strategy_class.get_strategy_id(callback)

        self.strategies[strategy_id].deinstrument(callback)

    def deinstrument_all(self):
        """ Deactive instrumentation on all callbacks by calling
        deinstrument_all on all strategies
        """
        for strategy in self.strategies.values():
            strategy.deinstrument_all()
        self.enabled = False

    def hook_all(self):
        """ First, inject the import hook in sys.meta if not present.
        Then hook all strategies, must be called after all the callbacks has
        been added. The call to strategies.hook will register patcher
        to the actual hook.
        Then call import_hook.apply_patchers that will apply patcher on
        modules already imported.
        """
        self.import_hook.inject()
        for strategy in self.strategies.values():
            strategy.hook()
        self.import_hook.apply_patchers()
        self.enabled = True

    @staticmethod
    def _get_strategy_class(strategy):
        """ Return a strategy class depending on the strategy name passed
        in parameter.
        Raise a NotImplementedError if the strategy is unknown.
        """
        if strategy == "import_hook":
            return ImportHookStrategy
        elif strategy == "DBApi2":
            return DBApi2Strategy
        elif strategy == "django":
            return DjangoStrategy
        elif strategy == "psycopg2":
            return Psycopg2Strategy
        elif strategy == "flask":
            return FlaskStrategy
        elif strategy == "pyramid":
            return PyramidStrategy
        elif HAS_ASYNCIO and strategy == "async_event_loop":
            return AsyncEventLoopStrategy
        elif HAS_ASYNCIO and strategy == "async_import_hook":
            return AsyncImportHookStrategy
        elif HAS_ASYNCIO and strategy == "aiohttp_install":
            return AioHTTPInstallStrategy
        elif HAS_ASYNCIO and strategy == "aiohttp_hook":
            return AioHTTPHookStrategy
        else:
            err_msg = "Unknown hooking_strategy {}"
            raise NotImplementedError(err_msg.format(strategy))
