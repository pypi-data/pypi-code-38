# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
This module contains the public API for interacting with the ledger from the perspective of a
specific party.
"""

# NOTE TO IMPLEMENTORS
#
# This file contains only public API definitions, overloads, and documentation. (This file should
# be treated more like a C header file than anything else.) The bulk of the implementation is kept
# in _party_client.py.
#
# This file is repetitive and tedious, but written this way primarily so that static typing tools
# do the right thing. Python's ``typing`` library (and mypy) aren't quite expressive enough to allow
# for a more concise representation of the various flavors of the API. The unit test
# ``test_api_consistency.py`` verifies that these implementations are generally in sync with each
# other the way that the documentation says they are.
import signal
import warnings
from asyncio import get_event_loop
from contextlib import contextmanager, ExitStack
from datetime import datetime
from functools import wraps
from logging import INFO
from pathlib import Path
from uuid import uuid4
from threading import current_thread, main_thread
from typing import Any, Awaitable, Callable, Collection, ContextManager, List, Optional, Union, \
    Tuple
from urllib.parse import urlparse

from .. import LOG
from ..client.config import NetworkConfig
from ..damlsdk.sandbox import sandbox
from ..metrics import MetricEvents
from ..model.core import ContractId, Party, ContractData, ContractsState, ContractMatch, \
    RunLevel, ContractContextualData, ContractContextualDataCollection
from ..model.ledger import LedgerMetadata
from ..model.reading import InitEvent, ReadyEvent, ContractCreateEvent, ContractExercisedEvent, \
    ContractArchiveEvent, TransactionStartEvent, TransactionEndEvent, EventKey
from ..model.writing import EventHandlerResponse
from ..util.asyncio_util import await_then
from ..util.prim_types import TimeDeltaConvertible
from ._network_client_impl import _NetworkImpl
from ._party_client_impl import _PartyClientImpl
from ._run_level import RunState


DEFAULT_TIMEOUT_SECONDS = 30


InitEventHandler = Callable[[InitEvent], EventHandlerResponse]
AInitEventHandler = Callable[[InitEvent],
                             Union[EventHandlerResponse, Awaitable[EventHandlerResponse]]]

ReadyEventHandler = Callable[[ReadyEvent], EventHandlerResponse]
AReadyEventHandler = Callable[[ReadyEvent],
                              Union[EventHandlerResponse, Awaitable[EventHandlerResponse]]]

TransactionStartEventHandler = Callable[[TransactionStartEvent], EventHandlerResponse]
ATransactionStartEventHandler = Callable[[TransactionStartEvent],
                                         Union[EventHandlerResponse, Awaitable[EventHandlerResponse]]]

TransactionEndEventHandler = Callable[[TransactionEndEvent], EventHandlerResponse]
ATransactionEndEventHandler = Callable[[TransactionEndEvent],
                                       Union[EventHandlerResponse, Awaitable[EventHandlerResponse]]]

ContractCreateEventHandler = Callable[[ContractCreateEvent], EventHandlerResponse]
AContractCreateEventHandler = Callable[[ContractCreateEvent],
                                       Union[EventHandlerResponse, Awaitable[EventHandlerResponse]]]

ContractExercisedEventHandler = Callable[[ContractExercisedEvent], EventHandlerResponse]
AContractExercisedEventHandler = Callable[[ContractExercisedEvent],
                                          Union[EventHandlerResponse,
                                                Awaitable[EventHandlerResponse]]]

ContractArchiveEventHandler = Callable[[ContractArchiveEvent], EventHandlerResponse]
AContractArchiveEventHandler = Callable[[ContractArchiveEvent],
                                        Union[EventHandlerResponse,
                                              Awaitable[EventHandlerResponse]]]


@contextmanager
def simple_client(url: 'Optional[str]' = None, party: 'Union[None, str, Party]' = None,
                  log_level: 'Optional[int]' = INFO) \
        -> 'ContextManager[SimplePartyClient]':
    """
    Start up a single client connecting to a single specific party.

    :param url:
        The URL of the client to connect to. Defaults to the value of the ``DAML_LEDGER_URL``
        environment variable (if set).
    :param party:
        The party to connect as. Defaults to the value of the ``DAML_LEDGER_PARTY`` environment
        variable if it is set.
    :param log_level:
        If non-``None``, configure a default logger that logs output at the specified level. The
        default value is ``INFO``.
    :return:
        A :class:`SimplePartyClient` that can be used in a completely blocking, synchronous
        fashion.
    """
    if log_level is not None:
        from .. import setup_default_logger
        setup_default_logger(log_level)

    import os
    if url is None:
        url = os.getenv('DAML_LEDGER_URL')
    if party is None:
        party = os.getenv('DAML_LEDGER_PARTY') or uuid4().hex
    if not url:
        raise ValueError('url must be specified, or the DAML_LEDGER_URL environment variable '
                         'must be set')
    if not party:
        raise ValueError('party must be specified, or the DAML_LEDGER_PARTY environment variable '
                         'must be set')

    with ExitStack() as context_manager:
        LOG.info('Starting a simple_client with to %s with party %r...', url, party)
        parsed_url = urlparse(url)
        if parsed_url.scheme is not None and parsed_url.scheme == 'sandbox':
            # start a local in-memory sandbox first
            daml_path = Path(os.getenv('DAML_LEDGER_DAR_PATH', 'target'))

            daml_artifacts = []  # type: List[Path]
            daml_artifacts.extend(daml_path.glob('**/*.dar'))
            daml_artifacts.extend(daml_path.glob('**/*.dalf'))

            sandbox_proc = sandbox(daml_path=daml_artifacts)
            url = context_manager.enter_context(sandbox_proc).url

        network = Network()
        network.set_config(url=url)
        client = network.simple_party(party)

        network.start_in_background()

        yield client

        network.shutdown()
        network.join()


class Network:
    """
    Manages network connection/scheduling logic on behalf of one or more :class:`PartyClient`
    instances.
    """

    def __init__(self, metrics: 'Optional[MetricEvents]' = None):
        self._impl = _NetworkImpl(metrics)

    def set_config(
            self,
            *config: 'NetworkConfig',
            url: 'Optional[str]' = None,
            admin_url: 'Optional[str]' = None,
            **kwargs):
        self._impl.set_config(*config, url=url, admin_url=admin_url, **kwargs)

    # <editor-fold desc="Global/Party client creation">

    def simple_global(self) -> 'SimpleGlobalClient':
        """
        Return a :class:`GlobalClient` that exposes thread-safe, synchronous (blocking) methods for
        communicating with a ledger. Callbacks are dispatched to background threads.
        """
        return self._impl.global_impl(SimpleGlobalClient)

    def aio_global(self) -> 'AIOGlobalClient':
        """
        Return a :class:`GlobalClient` that works on an asyncio event loop.
        """
        return self._impl.global_impl(AIOGlobalClient)

    def simple_party(self, party: Union[str, Party]) -> 'SimplePartyClient':
        """
        Return a :class:`PartyClient` that exposes thread-safe, synchronous (blocking) methods for
        communicating with a ledger. Callbacks are dispatched to background threads.

        :param party: The party to get a client for.
        """
        return self._impl.party_impl(party, SimplePartyClient)

    def aio_party(self, party: Union[str, Party]) -> 'AIOPartyClient':
        """
        Return a :class:`PartyClient` that works on an asyncio event loop.

        :param party: The party to get a client for.
        """
        return self._impl.party_impl(party, AIOPartyClient)

    # </editor-fold>

    # <editor-fold desc="Daemon thread-based scheduling API">

    def start_in_background(
            self, daemon: bool = True, install_signal_handlers: Optional[bool] = None) -> None:
        """
        Connect to the ledger in a background thread.

        The current thread does NOT block. Operations on instances of :class:`SimplePartyClient`
        are allowed, and operations on instances of :class:`AIOPartyClient` are allowed as long as
        they are made from the correct thread.
        """
        if install_signal_handlers is None:
            if current_thread() is main_thread():
                install_signal_handlers = True
        elif install_signal_handlers:
            if current_thread() is not main_thread():
                raise RuntimeError('tried to install signal handlers when not on the main thread')

        run_state = RunState(RunLevel.RUN_FOREVER)
        if install_signal_handlers:
            # the main loop will be run from a background thread, so do NOT use asyncio directly
            signal.signal(signal.SIGINT, lambda *_: self._impl.shutdown())
            try:
                signal.signal(signal.SIGINT, lambda *_: self._impl.abort())
            except ValueError:
                # SIGQUIT is not supported on Windows.
                pass

        return self._impl.start(run_state, daemon)

    def shutdown(self) -> None:
        """
        Gracefully shut down all network connections and notify all clients that they are about to
        be terminated.

        The current thread does NOT block.
        """
        return self._impl.shutdown()

    def join(self, timeout: Optional[float] = None) -> None:
        """
        Block the current thread until the client is shut down.

        :param timeout:
            Number of seconds to wait before timing out the join, or ``None`` to wait indefinitely.
        """
        return self._impl.join(timeout=timeout)

    # </editor-fold>

    # <editor-fold desc="asyncio-based scheduling API">

    def _run(self, initial_run_level, *coroutines: Awaitable[None],
             install_signal_handlers: Optional[bool] = None) -> None:
        if install_signal_handlers is None:
            if current_thread() is main_thread():
                install_signal_handlers = True
        elif install_signal_handlers:
            if current_thread() is not main_thread():
                raise RuntimeError('tried to install signal handlers when not on the main thread')

        run_state = RunState(initial_run_level)
        loop = get_event_loop()
        if install_signal_handlers:
            loop.add_signal_handler(signal.SIGINT, run_state.handle_sigint)
            try:
                loop.add_signal_handler(signal.SIGQUIT, run_state.handle_sigquit)
            except ValueError:
                # SIGQUIT is not supported on Windows.
                pass

        loop.run_until_complete(self.aio_run(*coroutines, run_state=run_state))

    def run_until_complete(
            self, *coroutines: Awaitable[None], install_signal_handlers: Optional[bool] = None) \
            -> None:
        """
        Block the main thread and run the application in an event loop on the main thread. The loop
        terminates when the given (optional) coroutines terminate OR :meth:`shutdown` is called AND
        all active command submissions and event handlers' follow-ups have successfully returned.

        :param coroutines:
            Coroutines to run alongside event handlers and command submissions. When these
            coroutines are done running and the
        :param install_signal_handlers:
            ``True`` to install SIGINT and SIGQUIT event handlers (CTRL+C and CTRL+\\);
            ``False`` to skip installation. The default value is ``None``, which installs signal
            handlers only when called from the main thread (default). If signal handlers are
            requested to be installed and the thread is NOT the main thread, this method throws.
        """
        self._run(RunLevel.RUN_UNTIL_IDLE, *coroutines,
                  install_signal_handlers=install_signal_handlers)
        LOG.info('The internal run_until_complete event loop has now completed.')

    def run_forever(
            self, *coroutines: Awaitable[None], install_signal_handlers: Optional[bool] = None) \
            -> None:
        """
        Block the main thread and run the application in an event loop on the main thread. The loop
        terminates when :meth:`shutdown` is called AND all active command submissions and event
        handlers' follow-ups have successfully returned.
        """
        self._run(RunLevel.RUN_FOREVER, *coroutines,
                  install_signal_handlers=install_signal_handlers)
        LOG.info('The internal run_forever event loop has been shut down.')

    async def aio_run(self, *coroutines, run_state: Optional[RunState] = None) -> None:
        """
        Coroutine where all network activity is scheduled from. This coroutine exits when
        :meth:`shutdown` is called, and can be used directly as an asyncio-native alternative to
        :meth:`start_in_background` and :meth:`join`.

        You would normally call this method directly only if you are trying to incorporate
        the client into an already-running event loop. Prefer :meth:`run_until_complete` or
        :meth:`run_forever` if you can block the current thread, or :meth:`start_in_background`
        with :meth:`join` if you wish to run the entire client on background threads.
        """
        await self._impl.aio_run(*coroutines, run_state=run_state)
        LOG.info('The aio_run coroutine has completed.')

    # </editor-fold>

    def parties(self) -> Collection[Party]:
        """
        Return a snapshot of the set of parties that exist right now.
        """
        return self._impl.parties()


class GlobalClient:
    """
    Public interface for either an async-based or a thread-safe version of an API for interacting
    with a Ledger API implementation that manages global ledger data, such as package store
    management and current time.
    """

    def __init__(self, impl: '_NetworkImpl'):
        self._impl = impl


class AIOGlobalClient(GlobalClient):

    async def ensure_dar(
            self,
            contents: bytes,
            timeout: 'Optional[TimeDeltaConvertible]' = DEFAULT_TIMEOUT_SECONDS) -> None:
        """
        Validate that the ledger has the packages specified by the given contents (as a byte array).
        Throw an exception if the specified DARs do not exist within the specified timeout.

        :param contents: The DAR or DALF to ensure.
        :param timeout: The maximum length of time to wait before giving up.
        """
        return self._impl.ensure_dar(contents, timeout)

    async def ensure_packages(
            self,
            package_ids: 'Collection[str]',
            timeout: 'Optional[TimeDeltaConvertible]' = DEFAULT_TIMEOUT_SECONDS) -> None:
        """
        Validate that packages with the specified package IDs exist on the ledger. Throw an
        exception if the specified packages do not exist within the specified timeout.

        :param package_ids: The set of package IDs to check for.
        :param timeout: The maximum length of time to wait before giving up.
        """
        return self._impl.ensure_packages(package_ids, timeout)

    async def metadata(self) -> LedgerMetadata:
        """
        Return the current set of known packages.
        """
        return await self._impl.aio_metadata()

    async def get_time(self) -> datetime:
        return await self._impl.get_time()

    async def set_time(self, new_datetime: datetime) -> None:
        await self._impl.set_time(new_datetime)


class SimpleGlobalClient(GlobalClient):

    def ensure_dar(
            self,
            contents: bytes,
            timeout: 'Optional[TimeDeltaConvertible]' = DEFAULT_TIMEOUT_SECONDS) -> None:
        """
        Validate that the ledger has the packages specified by the given contents (as a byte array).
        Throw an exception if the specified DARs do not exist within the specified timeout.

        :param contents: The DAR or DALF to ensure.
        :param timeout: The maximum length of time to wait before giving up.
        """
        return self._impl.ensure_dar(contents, timeout)

    def ensure_packages(
            self,
            package_ids: 'Collection[str]',
            timeout: 'Optional[TimeDeltaConvertible]' = DEFAULT_TIMEOUT_SECONDS) -> None:
        """
        Validate that packages with the specified package IDs exist on the ledger. Throw an
        exception if the specified packages do not exist within the specified timeout.

        :param package_ids: The set of package IDs to check for.
        :param timeout: The maximum length of time to wait before giving up.
        """
        return self._impl.ensure_packages(package_ids, timeout)

    def metadata(
            self,
            timeout: 'Optional[TimeDeltaConvertible]' = DEFAULT_TIMEOUT_SECONDS) -> LedgerMetadata:
        """
        Return the current set of known packages.
        """
        return self._impl.simple_metadata(timeout)

    def get_time(self) -> datetime:
        return self._impl.run_in_loop_threadsafe(lambda: self._impl.get_time())

    def set_time(self, new_datetime: datetime) -> None:
        self._impl.run_in_loop_threadsafe(lambda: self._impl.set_time(new_datetime))


class PartyClient:
    """
    Public interface for either an async-based or a thread-safe version of an API for interacting
    with a Ledger API implementation from the perspective of a single client.
    """

    def __init__(self, impl: '_PartyClientImpl'):
        self._impl = impl


class AIOPartyClient(PartyClient):
    """
    Implementation of a :class:`PartyClient` that exposes an `async`/`await`-style API that runs on
    an event loop.
    """

    # <editor-fold desc="Event handler registration">

    def ledger_init(self) -> Callable[[AInitEventHandler], AInitEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` has been
        instructed to begin, but before any network activity is started.
        """
        def _register_init(cb: AInitEventHandler) -> AInitEventHandler:
            self.add_ledger_init(cb)
            return cb

        return _register_init

    def add_ledger_init(self, handler: AInitEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` has been instructed to
        begin, but before any network activity is started.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        for key in EventKey.init():
            self._impl.add_event_handler(key, handler, None, self)

    def ledger_ready(self) -> Callable[[AReadyEventHandler], AReadyEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` has caught
        up to the head of the ledger, but before any :meth:`ledger_create` or :meth:`ledger_archive`
        callbacks are invoked.
        """
        def _register_ready(cb: AReadyEventHandler) -> AReadyEventHandler:
            self.add_ledger_ready(cb)
            return cb

        return _register_ready

    def add_ledger_ready(self, handler: AReadyEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` has caught up to the head of
        the ledger, but before any :meth:`ledger_create` or :meth:`ledger_archive` callbacks are
        invoked.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        for key in EventKey.ready():
            self._impl.add_event_handler(key, handler, None, self)

    def ledger_transaction_start(self) \
            -> Callable[[ATransactionStartEventHandler], ATransactionStartEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` receives a
        new transaction. Called before individual :meth:`ledger_create` and :meth:`ledger_archive`
        callbacks.
        """
        def _register_transaction_start(cb: ATransactionStartEventHandler) \
                -> ATransactionStartEventHandler:
            self.add_ledger_transaction_start(cb)
            return cb

        return _register_transaction_start

    def add_ledger_transaction_start(self, handler: ATransactionStartEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` receives a new transaction.
        Called before individual :meth:`ledger_create` and :meth:`ledger_archive` callbacks.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        for key in EventKey.transaction_start():
            self._impl.add_event_handler(key, handler, None, self)

    def ledger_transaction_end(self) \
            -> Callable[[ATransactionEndEventHandler], ATransactionEndEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` receives a
        new transaction. Called after individual :meth:`ledger_create` and :meth:`ledger_archive`
        callbacks.
        """
        def _register_transaction_end(cb: ATransactionEndEventHandler) \
                -> ATransactionEndEventHandler:
            self.add_ledger_transaction_end(cb)
            return cb

        return _register_transaction_end

    def add_ledger_transaction_end(self, handler: ATransactionEndEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` receives a new transaction.
        Called after individual :meth:`ledger_create` and :meth:`ledger_archive` callbacks.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        for key in EventKey.transaction_end():
            self._impl.add_event_handler(key, handler, None, self)

    def ledger_create(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractCreateEventHandler], AContractCreateEventHandler]:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        warnings.warn('@ledger_create is deprecated. Use @ledger_created instead.',
                      DeprecationWarning)

        def _register_create(cb: AContractCreateEventHandler) -> AContractCreateEventHandler:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                # noinspection PyDeprecation
                self.add_ledger_create(template, match=match, handler=cb)
            return cb

        return _register_create

    def add_ledger_create(self, template: Any, handler: AContractCreateEventHandler,
                          match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        warnings.warn('add_ledger_create is deprecated. Use add_ledger_created instead.',
                      DeprecationWarning)
        for key in EventKey.contract_created(True, template):
            self._impl.add_event_handler(key, handler, match, self)

    def ledger_created(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractCreateEventHandler], AContractCreateEventHandler]:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        def _register_created(cb: AContractCreateEventHandler) -> AContractCreateEventHandler:
            self.add_ledger_created(template, match=match, handler=cb)
            return cb

        return _register_created

    def add_ledger_created(self, template: Any, handler: AContractCreateEventHandler,
                           match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        for key in EventKey.contract_created(True, template):
            self._impl.add_event_handler(key, handler, match, self)

    def ledger_exercised(self, template: Any, choice: str) \
            -> Callable[[AContractExercisedEventHandler], AContractExercisedEventHandler]:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters an exercised
        choice event.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param choice:
            The name of the choice to listen for exercises on.
        """
        def _register_exercised(cb: AContractExercisedEventHandler) \
                -> AContractExercisedEventHandler:
            self.add_ledger_exercised(template, choice, handler=cb)
            return cb

        return _register_exercised

    def add_ledger_exercised(
            self, template: Any, choice: str, handler: AContractExercisedEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters an exercised
        choice event.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param choice:
            The name of the choice to listen for exercises on.
        :param handler:
            The callback to invoke whenever a matching template is exercised.
        """
        for key in EventKey.contract_exercised(True, template, choice):
            self._impl.add_event_handler(key, handler, None, self)

    def ledger_archive(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractArchiveEventHandler], AContractArchiveEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` encounters
        a newly archived contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        warnings.warn('@ledger_archive is deprecated. Use @ledger_archived instead.',
                      DeprecationWarning)

        def _register_archive(cb: AContractArchiveEventHandler) -> AContractArchiveEventHandler:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                # noinspection PyDeprecation
                self.add_ledger_archive(template, match=match, handler=cb)
                return cb

        return _register_archive

    def add_ledger_archive(self, template: Any, handler: AContractArchiveEventHandler,
                           match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly archived
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        warnings.warn('add_ledger_archive is deprecated. Use add_ledger_archived instead.',
                      DeprecationWarning)
        for key in EventKey.contract_archived(True, template):
            self._impl.add_event_handler(key, handler, match, self)

    def ledger_archived(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractArchiveEventHandler], AContractArchiveEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` encounters
        a newly archived contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        def _register_archived(cb: AContractArchiveEventHandler) -> AContractArchiveEventHandler:
            self.add_ledger_archived(template, match=match, handler=cb)
            return cb

        return _register_archived

    def add_ledger_archived(self, template: Any, handler: AContractArchiveEventHandler,
                            match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly archived
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        for key in EventKey.contract_archived(True, template):
            self._impl.add_event_handler(key, handler, match, self)

    # </editor-fold>

    # <editor-fold desc="Command submission">

    def submit(self, commands: EventHandlerResponse, workflow_id: Optional[str] = None) \
            -> 'Awaitable[None]':
        """
        Submit commands to the ledger.

        :param commands:
            An object that can be converted to a command.
        :param workflow_id:
            The optional workflow ID to stamp on the outgoing command.
        :return:
            A future that resolves when the command has made it to the ledger _or_ an error
            occurred when trying to process them.
        """
        return self._impl.write_commands(commands, workflow_id=workflow_id)

    def submit_create(
            self,
            template_name: str,
            arguments: 'Optional[dict]' = None,
            workflow_id: 'Optional[str]' = None) \
            -> Awaitable[None]:
        """
        Submit a single create command. Equivalent to calling :meth:`submit` with a single
        ``create``.

        :param template_name:
            The name of the template.
        :param arguments:
            The arguments to the create (as a ``dict``).
        :param workflow_id:
            The optional workflow ID to stamp on the outgoing command.
        :return:
            A future that resolves when the command has made it to the ledger _or_ an error
            occurred when trying to process them.
        """
        from .. import create
        return self.submit(create(template_name, arguments), workflow_id=workflow_id)

    def submit_exercise(
            self,
            cid: 'ContractId',
            choice_name: str,
            arguments: 'Optional[dict]' = None,
            workflow_id: 'Optional[str]' = None) \
            -> Awaitable[None]:
        """
        Submit a single exercise choice. Equivalent to calling :meth:`submit` with a single
        ``exercise``.

        :param cid:
            The :class:`ContractId` on which a choice is being exercised.
        :param choice_name:
            The name of the choice to exercise.
        :param arguments:
            The arguments to the create (as a ``dict``). Can be omitted (``None``) for no-argument
            choices.
        :param workflow_id:
            The optional workflow ID to stamp on the outgoing command.
        :return:
            A future that resolves when the command has made it to the ledger _or_ an error
            occurred when trying to process them.
        """
        from .. import exercise
        return self.submit(exercise(cid, choice_name, arguments), workflow_id=workflow_id)

    # </editor-fold>

    # <editor-fold desc="Active contract set">

    def find_by_id(self, cid: Union[str, ContractId]) -> Optional[ContractContextualData]:
        return self._impl.find_by_id(cid)

    def find(self,
             template: Any,
             match: ContractMatch = None,
             include_archived: bool = False) \
            -> ContractContextualDataCollection:
        return self._impl.find(template, match, include_archived=include_archived)

    def find_active(self, template: Any, match: ContractMatch = None) -> ContractsState:
        """
        Immediately return data from the current active contract set.

        The contents of this ACS are guaranteed to be present (or removed) in the current
        transaction _before_ processing any corresponding ``on_created`` or ``on_archived``
        callbacks for this party. The ACS is populated _before_ processing any ``on_ready``
        callbacks.

        This method raises an error if ACS tracking has been disabled on this client.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :return:
            A ``dict`` whose keys are :class:`ContractId` and values are corresponding contract
            data that match the current query.
        """
        return self._impl.find_active(template, match)

    def find_historical(self, template: Any, match: ContractMatch = None) \
            -> ContractContextualDataCollection:
        """
        Immediately return data from the current active and historical contract set as
        a contextual data collection

        The contents of this set are guaranteed to be up-to-date in the current transaction _before_
        processing any corresponding ``on_created`` or ``on_archived`` callbacks for this party. The
        set is up-to-date _before_ processing any ``on_ready`` callbacks.

        This method raises an error if historical tracking has been disabled on this client.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :return:
            A ``ContractContextualDataCollection`` whose values correspond to the contract
            data for active and archived contracts matching the current query.
        """
        return self._impl.find_historical(template, match)

    def find_one(self, template: Any, match: ContractMatch = None,
                 timeout: float = DEFAULT_TIMEOUT_SECONDS) \
            -> Awaitable[Tuple[ContractId, ContractData]]:
        """
        Return data from the current active contract set when at least some amount of rows exist in
        the active contract set.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :param timeout:
            Number of seconds in which to time out the search.
        :return:
            A ``Future`` that is resolved with a ``dict`` whose keys are :class:`ContractId` and
            values are corresponding contract data that match the current query.
        """
        return await_then(
            self.find_nonempty(template, match, min_count=1, timeout=timeout),
            lambda state: next(iter(state.items())))

    def find_nonempty(self, template: Any, match: ContractMatch, min_count: int = 1,
                      timeout: float = DEFAULT_TIMEOUT_SECONDS) \
            -> Awaitable[ContractsState]:
        """
        Return data from the current active contract set when at least some amount of rows exist in
        the active contract set.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :param min_count:
            The minimum number of rows to return. The default value is 1.
        :param timeout:
            Number of seconds in which to time out the search.
        :return:
            A ``Future`` that is resolved with a ``dict`` whose keys are :class:`ContractId` and
            values are corresponding contract data that match the current query.
        """
        return self._impl.find_nonempty(template, match, min_count, timeout)

    # </editor-fold>

    # <editor-fold desc="Ledger/client metadata">

    @property
    def party(self) -> Party:
        """
        Return the party serviced by this client.
        """
        return self._impl.party

    def set_config(self, url: Optional[str], **kwargs):
        self._impl.set_config(url=url, **kwargs)

    def get_time(self) -> Awaitable[datetime]:
        """
        Return the current time on the remote server. Also advance the local notion of time if
        required.
        """
        return self._impl.get_time()

    def set_time(self, new_datetime: datetime) -> Awaitable[None]:
        """
        Set the current time on the ledger. This is only supported if the ledger supports time
        manipulation.
        """
        return self._impl.set_time(new_datetime)

    def ready(self) -> Awaitable[None]:
        """
        Block until the ledger client has caught up to the current head and is ready to send
        commands.
        """
        return self._impl.ready()

    # </editor-fold>


class SimplePartyClient(PartyClient):
    """
    Implementation of a :class:`PartyClient` that exposes blocking calls, but can be used from any
    thread.

    Use this implementation if any of these apply:
      * you wish to interact with libraries that do not natively support asyncio
      * you are comfortable with the trade-off of having to block threads in order to write code
    """

    # <editor-fold desc="Event handler registration">

    def ledger_init(self) -> Callable[[InitEventHandler], InitEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` has been
        instructed to begin, but before any network activity is started.
        """

        def _register_init(cb: InitEventHandler) -> InitEventHandler:
            self.add_ledger_init(cb)
            return cb

        return _register_init

    def add_ledger_init(self, handler: InitEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` has been instructed to
        begin, but before any network activity is started.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        @wraps(handler)
        def _background_ledger_init(event: InitEvent) -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.init():
            self._impl.add_event_handler(key, _background_ledger_init, None, self)

    def ledger_ready(self) -> Callable[[AReadyEventHandler], AReadyEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` has caught
        up to the head of the ledger, but before any :meth:`ledger_create` or :meth:`ledger_archive`
        callbacks are invoked.
        """

        def _register_ready(cb: AReadyEventHandler) -> AReadyEventHandler:
            self.add_ledger_ready(cb)
            return cb

        return _register_ready

    def add_ledger_ready(self, handler: AReadyEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` has caught up to the head of
        the ledger, but before any :meth:`ledger_create` or :meth:`ledger_archive` callbacks are
        invoked.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        @wraps(handler)
        def _background_ledger_ready(event: ReadyEvent) -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.ready():
            self._impl.add_event_handler(key, _background_ledger_ready, None, self)

    def ledger_transaction_start(self) \
            -> Callable[[ATransactionStartEventHandler], ATransactionStartEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` receives a
        new transaction. Called before individual :meth:`ledger_create` and :meth:`ledger_archive`
        callbacks.
        """

        def _register_transaction_start(cb: ATransactionStartEventHandler) \
                -> ATransactionStartEventHandler:
            self.add_ledger_transaction_start(cb)
            return cb

        return _register_transaction_start

    def add_ledger_transaction_start(self, handler: ATransactionStartEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` receives a new transaction.
        Called before individual :meth:`ledger_create` and :meth:`ledger_archive` callbacks.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        @wraps(handler)
        def _background_ledger_transaction_start(event: TransactionStartEvent) \
                -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.transaction_start():
            self._impl.add_event_handler(key, _background_ledger_transaction_start, None, self)

    def ledger_transaction_end(self) \
            -> Callable[[ATransactionEndEventHandler], ATransactionEndEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` receives a
        new transaction. Called after individual :meth:`ledger_create` and :meth:`ledger_archive`
        callbacks.
        """

        def _register_transaction_end(cb: ATransactionEndEventHandler) \
                -> ATransactionEndEventHandler:
            self.add_ledger_transaction_end(cb)
            return cb

        return _register_transaction_end

    def add_ledger_transaction_end(self, handler: ATransactionEndEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` receives a new transaction.
        Called after individual :meth:`ledger_create` and :meth:`ledger_archive` callbacks.

        :param handler:
            The handler to register. This can either be a coroutine or a normal function, and may
            return anything that can be successfully coerced into a :class:`CommandPayload`.
        """
        @wraps(handler)
        def _background_ledger_transaction_end(event: TransactionEndEvent) \
                -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.transaction_end():
            self._impl.add_event_handler(key, _background_ledger_transaction_end, None, self)

    def ledger_create(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractCreateEventHandler], AContractCreateEventHandler]:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        warnings.warn('@ledger_create is deprecated. Use @ledger_created instead.',
                      DeprecationWarning)

        def _register_create(cb: AContractCreateEventHandler) -> AContractCreateEventHandler:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                # noinspection PyDeprecation
                self.add_ledger_create(template, match=match, handler=cb)
                return cb

        return _register_create

    def add_ledger_create(self, template: Any, handler: AContractCreateEventHandler,
                          match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        @wraps(handler)
        def _background_ledger_contract_create(event: ContractCreateEvent) \
                -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.contract_created(True, template):
            self._impl.add_event_handler(key, _background_ledger_contract_create, match, self)

    def ledger_created(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractCreateEventHandler], AContractCreateEventHandler]:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """

        def _register_created(cb: AContractCreateEventHandler) -> AContractCreateEventHandler:
            self.add_ledger_created(template, match=match, handler=cb)
            return cb

        return _register_created

    def add_ledger_created(self, template: Any, handler: AContractCreateEventHandler,
                           match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly created
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        @wraps(handler)
        def _background_ledger_contract_create(event: ContractCreateEvent) \
                -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.contract_created(True, template):
            self._impl.add_event_handler(key, _background_ledger_contract_create, match, self)

    def ledger_exercised(self, template: Any, choice: str) \
            -> Callable[[AContractExercisedEventHandler], AContractExercisedEventHandler]:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters an exercised
        choice event.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param choice:
            The name of the choice to listen for exercises on.
        """

        def _register_exercised(cb: AContractExercisedEventHandler) \
                -> AContractExercisedEventHandler:
            self.add_ledger_exercised(template, choice, handler=cb)
            return cb

        return _register_exercised

    def add_ledger_exercised(self, template: Any, choice: str,
                             handler: AContractExercisedEventHandler) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters an exercised
        choice event.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param choice:
            The name of the choice to listen for exercises on.
        :param handler:
            The callback to invoke whenever a matching template is exercised.
        """
        @wraps(handler)
        def _background_ledger_contract_exercised(event: ContractExercisedEvent) \
                -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.contract_exercised(True, template, choice):
            self._impl.add_event_handler(key, _background_ledger_contract_exercised, None, self)

    def ledger_archive(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractArchiveEventHandler], AContractArchiveEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` encounters
        a newly archived contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        warnings.warn('@ledger_archive is deprecated. Use @ledger_created instead.',
                      DeprecationWarning)

        def _register_archive(cb: AContractArchiveEventHandler) -> AContractArchiveEventHandler:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                # noinspection PyDeprecation
                self.add_ledger_archive(template, match=match, handler=cb)
                return cb

        return _register_archive

    def add_ledger_archive(self, template: Any, handler: AContractArchiveEventHandler,
                           match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly archived
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        warnings.warn('add_ledger_archive is deprecated. Use add_ledger_archived instead.',
                      DeprecationWarning)

        @wraps(handler)
        def _background_ledger_contract_archive(event: ContractArchiveEvent) \
                -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.contract_archived(True, template):
            self._impl.add_event_handler(key, _background_ledger_contract_archive, match, self)

    def ledger_archived(self, template: Any, match: Optional[ContractMatch] = None) \
            -> Callable[[AContractArchiveEventHandler], AContractArchiveEventHandler]:
        """
        Decorator for registering a callback to be invoked when the :class:`PartyClient` encounters
        a newly archived contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """

        def _register_archived(cb: AContractArchiveEventHandler) -> AContractArchiveEventHandler:
            self.add_ledger_archived(template, match=match, handler=cb)
            return cb

        return _register_archived

    def add_ledger_archived(self, template: Any, handler: AContractArchiveEventHandler,
                            match: Optional[ContractMatch] = None) -> None:
        """
        Register a callback to be invoked when the :class:`PartyClient` encounters a newly archived
        contract instance of a template.

        :param template:
            A template name to subscribe to, or '*' to subscribe on all templates.
        :param handler:
            The callback to invoke whenever a matching template is created.
        :param match:
            An (optional) parameter that filters the templates to be received by the callback.
        """
        @wraps(handler)
        def _background_ledger_contract_archived(event: ContractArchiveEvent) \
                -> Awaitable[EventHandlerResponse]:
            return self._impl.invoker.run_in_executor(lambda: handler(event))

        for key in EventKey.contract_archived(True, template):
            self._impl.add_event_handler(key, _background_ledger_contract_archived, match, self)

    # </editor-fold>

    # region Command submission

    def submit_create(self,
                      template_name: str,
                      arguments: 'Optional[dict]' = None,
                      workflow_id: str = None) -> None:
        """
        Synchronously submit a single create command. Equivalent to calling :meth:`submit` with a
        single ``create``.

        :param template_name:
            The name of the template.
        :param arguments:
            The arguments to the create (as a ``dict``).
        :param workflow_id:
            The optional workflow ID to stamp on the outgoing command.
        """
        from .. import create
        return self.submit(create(template_name, arguments), workflow_id=workflow_id)

    def submit_exercise(self,
                        cid: 'ContractId',
                        choice_name: str,
                        arguments: 'Optional[dict]' = None,
                        workflow_id: str = None) \
            -> None:
        """
        Synchronously submit a single exercise choice. Equivalent to calling :meth:`submit` with a
        single ``exercise``.

        :param cid:
            The :class:`ContractId` on which a choice is being exercised.
        :param choice_name:
            The name of the choice to exercise.
        :param arguments:
            The arguments to the create (as a ``dict``). Can be omitted (``None``) for no-argument
            choices.
        :param workflow_id:
            The optional workflow ID to stamp on the outgoing command.
        """
        from .. import exercise
        return self.submit(exercise(cid, choice_name, arguments), workflow_id=workflow_id)

    # endregion

    # <editor-fold desc="Active contract set">

    def find_by_id(self, cid: 'Union[str, ContractId]') -> 'Optional[ContractContextualData]':
        return self._impl.invoker.run_in_loop(lambda: self._impl.find_by_id(cid))

    def find(self,
             template: Any,
             match: ContractMatch = None,
             include_archived: bool = False) \
            -> ContractContextualDataCollection:
        return self._impl.invoker.run_in_loop(
            lambda: self._impl.find(template, match, include_archived=include_archived))

    def find_active(self, template: Any, match: ContractMatch = None) -> ContractsState:
        """
        Immediately return data from the current active contract set.

        The contents of this ACS are guaranteed to be present (or removed) in the current
        transaction _before_ processing any corresponding ``on_created`` or ``on_archived``
        callbacks for this party. The ACS is populated _before_ processing any ``on_ready``
        callbacks.

        This method raises an error if ACS tracking has been disabled on this client.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :return:
            A ``dict`` whose keys are :class:`ContractId` and values are corresponding contract
            data that match the current query.
        :return:
            A ``dict`` whose keys are :class:`ContractId` and values are corresponding contract
            data that match the current query.
        """
        return self._impl.invoker.run_in_loop(lambda: self._impl.find_active(template, match))

    def find_historical(self, template: Any, match: ContractMatch = None) \
            -> ContractContextualDataCollection:
        """
        Immediately return data from the current active and historical contract set.

        The contents of this set are guaranteed to be up-to-date in the current transaction _before_
        processing any corresponding ``on_created`` or ``on_archived`` callbacks for this party. The
        set is up-to-date _before_ processing any ``on_ready`` callbacks.

        This method raises an error if historical tracking has been disabled on this client.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :return:
            A ``dict`` whose keys are :class:`ContractId` and values are corresponding contract
            data that match the current query.
        :return:
            A ``dict`` whose keys are :class:`ContractId` and values are corresponding contract
            data that match the current query.
        """
        return self._impl.invoker.run_in_loop(lambda: self._impl.find_historical(template, match))

    def find_one(self, template: Any, match: ContractMatch = None,
                 timeout: float = DEFAULT_TIMEOUT_SECONDS) \
            -> Tuple[ContractId, ContractData]:
        """
        Return data from the current active contract set when at least some amount of rows exist in
        the active contract set.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :param timeout:
            Number of seconds in which to time out the search.
        :return:
            A ``Future`` that is resolved with a ``dict`` whose keys are :class:`ContractId` and
            values are corresponding contract data that match the current query.
        """
        state = self.find_nonempty(template, match, min_count=1, timeout=timeout)
        return next(iter(state.items()))

    def find_nonempty(self, template: Any, match: ContractMatch, min_count: int = 1,
                      timeout: float = DEFAULT_TIMEOUT_SECONDS) \
            -> ContractsState:
        """
        Return data from the current active contract set when at least some amount of rows exist in
        the active contract set.

        :param template:
            The name of the template to fetch data from.
        :param match:
            An optional dictionary whose keys are matched against corresponding field values.
        :param min_count:
            The minimum number of rows to return. The default value is 1.
        :param timeout:
            Number of seconds in which to time out the search.
        :return:
            A ``Future`` that is resolved with a ``dict`` whose keys are :class:`ContractId` and
            values are corresponding contract data that match the current query.
        """
        return self._impl.invoker.run_in_loop(
            lambda: self._impl.find_nonempty(template, match, min_count=min_count, timeout=timeout))

    # </editor-fold>

    # <editor-fold desc="Ledger/client metadata">

    @property
    def party(self) -> Party:
        """
        Return the party serviced by this client.
        """
        return self._impl.party

    def set_config(self, url: Optional[str], **kwargs):
        self._impl.set_config(url=url, **kwargs)

    def get_time(self) -> datetime:
        return self._impl.invoker.run_in_loop(lambda: self._impl.get_time())

    def set_time(self, new_datetime: datetime) -> None:
        return self._impl.invoker.run_in_loop(lambda: self._impl.set_time(new_datetime))

    def submit(self, commands, workflow_id: str = None) -> None:
        return self._impl.invoker.run_in_loop(lambda: self._impl.write_commands(commands, workflow_id=workflow_id))

    def ready(self) -> None:
        """
        Block until the underlying infrastructure has connected to all necessary services.
        """
        # TODO: Improve on this implementation; this spin loop is unnecessarily ugly
        from time import sleep
        while self._impl.invoker.get_loop() is None:
            sleep(0.1)

        LOG.debug('Waiting for the underlying implementation to be ready...')
        return self._impl.invoker.run_in_loop(lambda: self._impl.ready())

    # </editor-fold>
