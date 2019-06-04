# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from asyncio import ensure_future, gather, get_event_loop, Future, InvalidStateError
from functools import wraps

from dataclasses import replace, dataclass, field, fields
from datetime import datetime, timedelta
from io import StringIO
from typing import Any, Awaitable, Callable, Collection, List, Optional, Sequence, Set, Tuple, \
    TypeVar
import reprlib
import uuid

from .. import LOG
from .config import NetworkConfig, PartyConfig
from ._writer_verify import ValidateSerializer
from ..client.state import ActiveContractSet
from ..metrics import MetricEvents
from ..model.core import ContractMatch, ContractsState, ContractId, ContractData, \
    CommandTimeoutError, Party, ContractContextualData, ContractContextualDataCollection
from ..model.ledger import LedgerMetadata
from ..model.network import connection_settings
from ..model.reading import BaseEvent, TransactionStartEvent, TransactionEndEvent, OffsetEvent, \
    TransactionFilter, EventKey, ContractCreateEvent, ContractArchiveEvent, \
    sortable_offset_height, InitEvent
from ..model.writing import CommandBuilder, CommandDefaults, CommandPayload, \
    EventHandlerResponse, Command
from ..protocols import LedgerNetwork, LedgerClient
from ..util.asyncio_util import ServiceQueue, await_then, completed, propagate, \
    safe_create_future, named_gather, failed, Invoker
from ..util.events import CallbackManager
from ..util.prim_natural import n_things
from ..util.typing import safe_cast

T = TypeVar('T')


class _PartyClientImpl:
    def __init__(self, metrics: 'MetricEvents', invoker: 'Invoker', party: 'Party'):
        self.metrics = metrics
        self.invoker = invoker
        self.party = party

        self._config_values = dict()
        self._config = None  # type: Optional[NetworkConfig]
        self._pool = None  # type: Optional[LedgerNetwork]
        self._pool_fut = None  # type: Optional[Awaitable[LedgerNetwork]]
        self._client_fut = None  # type: Optional[Awaitable[LedgerClient]]
        self._ready_fut = safe_create_future()

        self._acs = ActiveContractSet()
        self._reader = _PartyClientReaderState()
        self._writer = _PartyClientWriterState()

        self._callbacks = CallbackManager()

    def connect_in(self, pool: LedgerNetwork, base_config: dict) -> Future:
        config_names = {f.name for f in fields(PartyConfig)}
        all_config = {**base_config, **self._config_values}

        self._config = config = PartyConfig(**{k: v for k, v in all_config.items() if k in config_names})
        settings, url_prefix = connection_settings(
            config.url,
            self.party,
            verify_ssl=config.verify_ssl,
            ca_file=config.ca_file,
            cert_file=config.cert_file,
            cert_key_file=config.cert_key_file)

        self._pool = pool
        self._client_fut = ensure_future(pool.connect(
            self.party, settings, url_prefix, config.admin_url))
        return self._client_fut

    def set_config(self, **kwargs):
        self._config_values.update(kwargs)

    def initialize(self, current_time: datetime, metadata: LedgerMetadata) -> Awaitable[None]:
        """
        Initialize the state of the ledger.

        :param current_time:
            The ledger time to publish as part of the :class:`InitEvent`.
        :param metadata:
            Information about the connected ledger.
        :return:
        """
        self._acs.metadata_future.set_result(metadata.store)
        evt = InitEvent(self, self.party, current_time, metadata.ledger_id, metadata.store)
        return self.emit_event(evt)

    def ready(self) -> Awaitable[None]:
        return self._ready_fut

    def get_time(self) -> Awaitable[datetime]:
        return await_then(self._pool.ledger(), lambda metadata: metadata.time_model.get_time())

    def set_time(self, new_datetime) -> Awaitable[None]:
        return await_then(self._pool, lambda pool: pool.set_time(new_datetime))

    # region Event Handler Management

    # noinspection PyShadowingBuiltins
    def add_event_handler(self, key, handler, filter, context):
        from copy import copy
        from functools import wraps

        @wraps(handler)
        def rewritten_event(event):
            new_event = copy(event)
            new_event.client = context
            return handler(new_event)

        h = wrap_as_command_submission(self.write_commands, rewritten_event, filter)
        self._callbacks.add_listener(key, h)

    def emit_event(self, data: BaseEvent) -> Awaitable[Any]:
        """
        Emit an event.

        :param data:
            The event to raise.
        :return:
            An Awaitable that is resolved when the commands that resulted from event callbacks
            have been completed either successfully or unsuccessfully.
        """
        futures = [ensure_future(fut)
                   for key in EventKey.from_event(data)
                   for fut in self._callbacks.for_listeners(key)(data)]
        LOG.debug('The event %s yielded futures %s', data, futures)
        if len(futures) == 0:
            return completed(None)
        elif len(futures) == 1:
            return futures[0]
        else:
            return named_gather(repr(data), *futures, return_exceptions=True)

    # endregion

    # region Active/Historical Contract Set management

    def find_by_id(self, cid: ContractId) -> ContractContextualData:
        return self._acs.get(cid)

    def find(self,
             template: Any,
             match: ContractMatch = None,
             include_archived: bool = False) \
            -> ContractContextualDataCollection:
        return self._acs.read_full(template, match, include_archived=include_archived)

    def find_active(self, template: Any, match: ContractMatch = None) -> ContractsState:
        return self._acs.read_active(template, match)

    def find_historical(self, template: Any, match: ContractMatch = None) \
            -> ContractContextualDataCollection:
        return self._acs.read_full(template, match, include_archived=True)

    def find_nonempty(self, template: Any, match: ContractMatch, min_count: int = 1,
                      timeout: float = 30):
        return self._acs.read_async(template, match, min_count=min_count)

    # endregion

    # region Read Path

    async def read_transactions(self, until_offset: Optional[str], raise_events: bool) \
            -> Tuple[str, Future]:
        """
        Main processing method of events from the read side. Only one instance of this coroutine
        should be active at a time.

        :param until_offset:
            The destination ledger offset to read up until to. If not included, then the client
            attempts to read as many transactions as is currently available.
        :param raise_events:
            ``True`` to raise transaction- and contract-related events to event handlers;
            ``False`` to suppress this behavior and only update local state within the client
            (offset information and active contract set).
        :return:
            The ledger offset that the reader ended at and a Future that is resolved when all event
            handlers' follow-ups have either successfully or unsuccessfully completed.
        """
        LOG.verbose('  read_transactions(%s, %s) with party %s | (groups %s), reader offset %s',
                    until_offset, raise_events, self.party, self._config.party_groups,
                    self._reader.offset)
        client = await self._client_fut
        metadata = await self._pool.ledger()

        initial_offset = self._reader.offset
        event_count = 0

        futs = []

        while (until_offset is None or
               self._reader.offset is None or
               self._reader.offset != until_offset):
            LOG.verbose('  read_transactions(%s, %s) with party %s | current offset: %s; '
                        'destination offset: %s',
                        until_offset, raise_events, self.party, self._reader.offset, until_offset)

            # prepare a call to /events
            transaction_filter = TransactionFilter(
                ledger_id=metadata.ledger_id,
                current_offset=self._reader.offset,
                destination_offset=until_offset,
                templates=None,
                max_blocks=None,
                party_groups=self._config.party_groups)

            transaction_events = await client.events(transaction_filter)
            for event in transaction_events:
                futs.append(self._process_transaction_stream_event(event, raise_events))
            event_count += len(transaction_events)

            # if a destination offset is not specified, then only read one pass of transaction
            # events before exiting
            if until_offset is None:
                break

        self.metrics.party_offset(self.party, self._reader.offset)
        LOG.verbose('  read_transactions(%s, %s) with party %s | reader offset %s',
                    until_offset, raise_events, self.party, self._reader.offset)
        futs = [fut for fut in futs if not fut.done()]
        if len(futs) == 0:
            return self._reader.offset, completed(None)
        elif len(futs) == 1:
            return self._reader.offset, futs[0]
        else:
            return self._reader.offset, gather(*futs, return_exceptions=True)

    def _process_transaction_stream_event(self, event: Any, raise_events: bool) -> Future:
        """

        :param event:
        :param raise_events:
        """
        if isinstance(event, TransactionStartEvent):
            # Update the ACS before sharing this information with interested parties
            LOG.info('Processing transaction: %s, %s, %s', event.offset, event.workflow_id, event.command_id)
            for contract_event in event.contract_events:
                if isinstance(contract_event, ContractCreateEvent):
                    self._acs.handle_create(contract_event)
                elif isinstance(contract_event, ContractArchiveEvent):
                    self._acs.handle_archive(contract_event)

        elif isinstance(event, TransactionEndEvent):
            # Notify anything waiting on commands to complete that some of them will have
            # completed as a consequence of this transaction.
            for cmd in self._writer.inflight_commands:
                cmd.notify_read_done(event.command_id, event.time)

            LOG.debug('evt recv: party %s, BIM %r (%s events)',
                      self.party, event.command_id[0:7], len(event.contract_events))

        if raise_events:
            fut = self.emit_event(event)
        else:
            fut = completed(None)

        if isinstance(event, OffsetEvent):
            self._reader.offset = event.offset

        return fut

    # endregion

    # region Write path

    def write_commands(self, commands: EventHandlerResponse, ignore_errors: bool = False,
                       workflow_id: Optional[str] = None) \
            -> Awaitable[None]:
        """
        Submit a command or list of commands.

        :param commands:
            The commands to send to the server.
        :param ignore_errors:
            Whether errors should be ignored for purposes of terminating the client. If ``True``,
            then a failure to send this command does not necessarily end the client.
        :return:
            An ``asyncio.Future`` that is resolved right before the corresponding side effects have
            hit the event stream for this party. Synchronous errors are reported back immediately
            and not failed through this mechanism.
        """
        if workflow_id is None:
            workflow_id = uuid.uuid4().hex
        cb = CommandBuilder.coerce(commands, atomic_default=True)
        cb.defaults(workflow_id=workflow_id)

        p = _PendingCommand(cb)
        p.future.add_done_callback(lambda _: self._process_command_finished(p, ignore_errors))
        self._writer.pending_commands.put(p)
        LOG.debug('write_commands(%s)', p)
        return p.future

    def _process_command_finished(self, pending_command, ignore_errors):
        try:
            if pending_command.future.exception() is None:
                LOG.debug('Command finished: %s', pending_command)
            self._writer.inflight_commands.remove(pending_command)
        except ValueError:
            LOG.warning('Tried to remove %s even though it was already removed.', pending_command)

        if pending_command.future.exception() is not None:
            # TODO: more with this; maybe let the user respond to this
            LOG.exception('A command submission failed!',
                          exc_info=pending_command.future.exception())

    async def main_writer(self):
        """
        Main coroutine for submitting commands.
        """
        LOG.info('Writer loop for party %s is starting...', self.party)
        ledger_fut = ensure_future(self._pool.ledger())

        client = self._client_fut.result()  # type: LedgerClient
        metadata = ledger_fut.result()  # type: LedgerMetadata
        validator = ValidateSerializer(metadata.store)

        self._writer.pending_commands.start()

        # Asynchronously iterate over all pending commands that a user has (or will) send.
        # This asynchronous loop "blocks" when pending_commands is empty and is "woken up"
        # immediately when new data is added to it. The loop terminates when the pending_commands
        # ServiceQueue is stopped.
        async for p in self._writer.pending_commands:
            LOG.debug('Sending a command: %s', p)
            ledger_effective_time = metadata.time_model.get_time()
            command_payloads = []  # type: List[Tuple[_PendingCommand, Sequence[CommandPayload]]]

            self._writer.inflight_commands.append(p)
            try:
                defaults = CommandDefaults(
                    default_party=self.party,
                    default_ledger_id=metadata.ledger_id,
                    default_workflow_id=None,
                    default_application_id=self._config.application_name,
                    default_command_id=None,
                    default_ttl=timedelta(seconds=30))
                cps = p.command.build(defaults, ledger_effective_time)
                if cps:
                    commands = [replace(cp, commands=validator.serialize_commands(cp.commands))
                                for cp in cps]  # type: Sequence[CommandPayload]
                    command_payloads.append((p, commands))
                    await submit_command_async(client, p, commands)
                else:
                    # This is a "null command"; don't even bother sending to the server. Immediately
                    # resolve the future successfully and discard
                    p.future.set_result(None)
            except Exception as ex:
                LOG.exception("Tried to send a command and failed!")
                p.notify_read_fail(ex)

        LOG.info('Writer loop for party %s is winding down.', self.party)

        # After the pending command list is fully empty (and never to be filled again), wait for
        # all outstanding commands.
        await gather(*(pc.future for pc in self._writer.inflight_commands), return_exceptions=True)

        LOG.info('Writer loop for party %s is finished.', self.party)

    def writer_idle(self):
        return not bool(self._writer.pending_commands) and not self._writer.inflight_commands

    def stop_writer(self):
        """
        Prohibit future command submissions from being accepted.
        """
        self._writer.pending_commands.stop()

    # endregion


@dataclass
class _PartyClientReaderState:
    offset: Optional[str] = field(default=None)


@dataclass
class _PartyClientWriterState:
    pending_commands: 'ServiceQueue[_PendingCommand]' = field(default_factory=ServiceQueue)
    inflight_commands: 'List[_PendingCommand]' = field(default_factory=list)


class _PendingCommand:
    """
    Track the status of a set of commands in-flight.
    """

    __slots__ = ('command', 'command_ids', 'max_record_time', 'future')

    def __init__(self, command: CommandBuilder):
        self.command = safe_cast(CommandBuilder, command)
        self.command_ids = None  # type: Optional[Set[str]]
        self.max_record_time = None  # type: Optional[datetime]
        self.future = get_event_loop().create_future()

    def notify_write(self, command_ids: Collection[str], max_record_time: datetime):
        if self.max_record_time is not None:
            raise Exception('cannot send an already in-progress command')
        self.command_ids = set(command_ids)
        self.max_record_time = max_record_time

    def notify_read_done(self, command_id: str, ledger_time: Optional[datetime]):
        """
        Trigger an appropriate response given the receipt of a transaction.
        """
        if self.command_ids is not None:
            if command_id not in self.command_ids:
                return

            self.command_ids.discard(command_id)
            if not self.command_ids:
                # the command is finished
                self.future.set_result(None)
                return

        if self.max_record_time is not None and ledger_time is not None and \
                self.max_record_time < ledger_time:
            self.future.set_exception(CommandTimeoutError())

    def notify_read_fail(self, ex: Exception):
        self.future.set_exception(ex)

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    def __repr__(self):
        with StringIO() as buf:
            buf.write('<_PendingCommand(command=')
            buf.write(format(self.command, 'c'))
            if self.command_ids is not None:
                buf.write(', command_ids=')
                buf.write(format(self.command_ids))
            if self.max_record_time is not None:
                buf.write(', max_record_time="')
                buf.write(format(self.max_record_time.isoformat()))
                buf.write('"')
            buf.write(', future=')
            buf.write(format(self.future))
            buf.write('>')
            return buf.getvalue()


def submit_command_async(
        client: LedgerClient, p: '_PendingCommand', commands: Sequence[CommandPayload]) \
        -> Awaitable[None]:
    """
    Submit a command asynchronously.

    The returned future is resolved when all commands have successfully completed their network
    operations, but not necessarily when the ledger has committed the results of that command to the
    ledger.

    :param client:
    :param p:
    :param commands:
    :return:
    """
    coros = []
    command_ids = []
    maximum_record_time = commands[0].maximum_record_time

    for payload in commands:
        coro = None
        command_ids.append(payload.command_id)
        try:
            coro = ensure_future(client.commands(payload))

            LOG.info('cmd submit: party %s, workflow_id %r, command_id %r, %s: %r',
                     payload.party, payload.workflow_id[0:7], payload.command_id[0:7],
                     n_things(len(payload.commands), 'commands'), reprlib.repr(payload.commands))
        except Exception as ex:
            # TODO: consider what to do in this case
            p.notify_read_fail(ex)

        if coro is not None:
            coros.append(coro)

    p.notify_write(command_ids, maximum_record_time)
    if len(coros) == 0:
        return completed(None)
    elif len(coros) == 1:
        return coros[0]
    else:
        return named_gather('SubmitCommandAsync()', *coros, return_exceptions=True)


# noinspection PyShadowingBuiltins
def wrap_as_command_submission(submit_fn, callback, filter) \
        -> Callable[[ContractId, ContractData], Awaitable[Any]]:
    """
    Normalize a callback to something that takes a single contract ID and contract data, and
    return an awaitable that is resolved when the underlying command has been fully submitted.
    """
    import inspect

    @wraps(callback)
    def implementation(*args, **kwargs):
        if filter is not None and not filter(*args, **kwargs):
            return completed(None)

        try:
            ret = callback(*args, **kwargs)
        except BaseException as exception:
            LOG.exception('The callback %r threw an exception!', callback)
            return failed(exception)

        if ret is None:
            return completed(None)
        elif isinstance(ret, (CommandBuilder, Command, list, tuple)):
            try:
                ret_fut = submit_fn(ret)
            except BaseException as exception:
                LOG.exception('The callback %r returned commands that could not be submitted! (%s)',
                              callback, ret)
                return failed(exception)
            return ret_fut
        elif inspect.isawaitable(ret):
            # the user-provided callback returned an Awaitable
            cmd_fut = ensure_future(ret)
            if cmd_fut.done():
                if cmd_fut.cancelled() or cmd_fut.exception() is not None:
                    # a cancelled or failed user-provided callback Future is the same as the
                    # command submission itself failing
                    return cmd_fut

                # functionally equivalent to the non-Awaitable case if the Awaitable has already
                # completed
                return submit_fn(cmd_fut.result())
            else:
                # create `fut`, which we'll give to the user; wait for `cmd_fut` to finish, then
                # take the result of that awaitable and try to submit a command with that result
                fut = get_event_loop().create_future()

                def cmd_future_finished(_):
                    ret = cmd_fut.result()
                    if ret is None:
                        fut.set_result(None)
                    elif isinstance(ret, (CommandBuilder, Command, list, tuple)):
                        propagate(ensure_future(submit_fn(ret)), fut)
                    elif inspect.isawaitable(ret):
                        LOG.error('A callback cannot return an Awaitable of an Awaitable')
                        raise InvalidStateError(
                            'A callback cannot return an Awaitable of an Awaitable')

                cmd_fut.add_done_callback(cmd_future_finished)

                return fut
        else:
            LOG.error('the callback %r returned a value of an unexpected type: %s', callback, ret)
            raise ValueError('unexpected return type from a callback')

    return implementation


async def read_transactions(
        party_impls: Collection[_PartyClientImpl],
        until_offset: Optional[str],
        raise_events: bool) -> Tuple[Collection[str], Future]:
    """
    Read transactions from a collection of PartyImpls.

    :param party_impls:
    :param until_offset:
    :param raise_events:
    :return:
        A tuple containing:
         * a set of the offsets returned from all readers, and
         * a Future that is resolved when all events across all readers have resolved either
           successfully or unsuccessfully.
    """
    tuples = await gather(*(pi.read_transactions(until_offset, raise_events) for pi in party_impls))
    offsets = sorted({t[0] for t in tuples}, key=sortable_offset_height)
    futures = [ensure_future(t[1]) for t in tuples]
    futures = [fut for fut in futures if not fut.done()]
    if not futures:
        return offsets, completed(None)
    elif len(futures):
        return offsets, futures[0]
    else:
        return offsets, named_gather(repr(futures), *futures, return_exceptions=True)
