# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Support for the gRPC-based Ledger API.
"""
from asyncio import gather
from datetime import datetime
from threading import Thread, Event
from typing import Awaitable, Iterable, Optional, Sequence

# noinspection PyPackageRequirements
from grpc import Channel, secure_channel, insecure_channel, ssl_channel_credentials, RpcError

from ... import LOG
from .._base import LedgerClient, _LedgerConnection, _LedgerConnectionContext
from .grpc_time import maybe_grpc_time_stream
from .pb_parse_event import serialize_request, to_transaction_events, \
    BaseEventDeserializationContext
from .pb_parse_metadata import parse_daml_metadata_pb, parse_archive_payload, find_dependencies
from ...model.core import Party
from ...model.ledger import LedgerMetadata, StaticTimeModel, RealTimeModel
from ...model.network import HTTPConnectionSettings
from ...model.reading import BaseEvent, TransactionFilter
from ...model.types_store import PackageStore, PackageProvider
from ...model.writing import CommandPayload
from ...util.io import read_file_bytes
from ...util.typing import safe_cast


class GRPCv1LedgerClient(LedgerClient):
    def __init__(self, connection: 'GRPCv1Connection', ledger: LedgerMetadata, party: Party):
        self.connection = safe_cast(GRPCv1Connection, connection)
        self.ledger = safe_cast(LedgerMetadata, ledger)
        self.party = safe_cast(str, party)  # type: Party

    def commands(self, commands: CommandPayload) -> None:
        serializer = self.ledger.serializer
        request = serializer.serialize_command_request(commands)
        return self.connection.context.run_in_background(
            lambda: self.connection.command_service.SubmitAndWait(request))

    def events(self, transaction_filter: TransactionFilter) \
            -> Awaitable[Sequence[BaseEvent]]:
        request = serialize_request(transaction_filter, self.party)

        import asyncio
        results_future = asyncio.get_event_loop().create_future()

        context = BaseEventDeserializationContext(
            None, self.ledger.store, self.party, transaction_filter.ledger_id)

        def on_events_done(fut):
            try:
                tx_stream, tt_stream = fut.result()
                events = to_transaction_events(
                    context, tx_stream, tt_stream, transaction_filter.destination_offset)
            except Exception as ex:
                LOG.exception('Failed to parse data coming back from an event!')
                results_future.set_exception(ex)
                return
            results_future.set_result(events)

        ts_future = self.connection.context.run_in_background(
            lambda: self.connection.transaction_service.GetTransactions(request))
        tst_future = self.connection.context.run_in_background(
            lambda: self.connection.transaction_service.GetTransactionTrees(request))
        t_fut = gather(ts_future, tst_future)
        t_fut.add_done_callback(on_events_done)

        return results_future


def grpc_set_time(connection: 'GRPCv1Connection', ledger_id: str, new_datetime: datetime) -> None:
    from . import model as G
    from .pb_ser_command import as_api_timestamp

    request = G.GetTimeRequest(ledger_id=ledger_id)
    response = connection.time_service.GetTime(request)
    ts = next(iter(response))

    request = G.SetTimeRequest(
        ledger_id=ledger_id,
        current_time=ts.current_time,
        new_time=as_api_timestamp(new_datetime))
    connection.time_service.SetTime(request)
    LOG.info('Time on the server changed by the local client to %s.', new_datetime)


def grpc_detect_ledger_id(stub: 'GRPCv1Connection') -> Optional[str]:
    """
    Return the ledger ID from the remote server when it becomes available, or ``None`` if the
    Ledger Identity API is not supported.
    """
    from . import model as G
    LOG.debug("Starting a monitor thread for stubs: %s", stub)
    try:
        response = stub.ledger_identity_service.GetLedgerIdentity(G.GetLedgerIdentityRequest())
    except RpcError as ex:
        if ex.details().startswith('Received http2 header with status'):
            LOG.info("No gRPC Ledger Identity Service found!")
            return None
        LOG.exception('An unexpected error occurred when trying to fetch the ledger identity.')
        raise

    return response.ledger_id


def grpc_main_thread(connection: 'GRPCv1Connection', ledger_id: str) -> Iterable[LedgerMetadata]:
    from . import model as G
    from .pb_ser_command import ProtobufSerializer

    store = PackageStore.empty()
    request = G.GetLedgerEndRequest(ledger_id=ledger_id)

    package_provider = GRPCPackageProvider(connection, ledger_id)

    request = G.GetLedgerEndRequest(ledger_id=ledger_id)
    offset = connection.transaction_service.GetLedgerEnd(request).offset.absolute

    grpc_package_sync(package_provider, store)

    time_iter = maybe_grpc_time_stream(connection.time_service, ledger_id)
    time_model = StaticTimeModel(next(time_iter)) if time_iter is not None else RealTimeModel()

    yield LedgerMetadata(
        ledger_id=ledger_id,
        offset=offset,
        store=store,
        time_model=time_model,
        serializer=ProtobufSerializer(store),
        protocol_version="v1")

    # oh man, another thread...
    def time_sync_thread():
        try:
            # keep the network open as long as we keep getting time updates
            for ts in time_iter:
                time_model.current_time = ts
            LOG.debug('The time stream has completed.')
        except:
            pass

    if time_iter is not None:
        time_thread = Thread(name='time-sync-thread', target=time_sync_thread, daemon=True)
        time_thread.start()

    LOG.debug('There is no time service, so we will merely wait for the underlying transaction '
              'stream to die.')
    while True:
        grpc_package_sync(package_provider, store)
        if connection._closed.wait(1):
            break

    LOG.debug('The gRPC monitor thread is now shutting down.')
    yield None


class GRPCPackageProvider(PackageProvider):
    def __init__(self, connection: 'GRPCv1Connection', ledger_id: str):
        self.connection = connection
        self.ledger_id = ledger_id

    def get_package_ids(self) -> 'Sequence[str]':
        from . import model as G
        request = G.ListPackagesRequest(ledger_id=self.ledger_id)
        response = self.connection.package_service.ListPackages(request)
        return response.package_ids

    def fetch_package(self, package_id: str) -> bytes:
        from . import model as G
        request = G.GetPackageRequest(ledger_id=self.ledger_id, package_id=package_id)
        package_info = self.connection.package_service.GetPackage(request)
        return package_info.archive_payload


def grpc_package_sync(package_provider: PackageProvider, store: 'PackageStore') -> 'None':
    all_package_ids = package_provider.get_package_ids()
    loaded_package_ids = [a.hash for a in store.archives()]

    metadatas_pb = {}
    for package_id in all_package_ids:
        if package_id not in loaded_package_ids:
            archive_payload = package_provider.fetch_package(package_id)
            metadatas_pb[package_id] = parse_archive_payload(archive_payload)

    metadatas_pb = find_dependencies(metadatas_pb, loaded_package_ids)
    for package_id, archive_payload in metadatas_pb.items():
        store.register_all(parse_daml_metadata_pb(package_id, archive_payload))


def grpc_create_channel(settings: HTTPConnectionSettings) -> Channel:
    target = f'{settings.host}:{settings.port}'
    options = [('grpc.max_send_message_length', -1),
               ('grpc.max_receive_message_length', -1)]

    if settings.oauth:
        # noinspection PyPackageRequirements
        from google.auth.transport.grpc import secure_authorized_channel
        # noinspection PyPackageRequirements
        from google.auth.transport.requests import Request as RefreshRequester
        # noinspection PyPackageRequirements
        from google.oauth2.credentials import Credentials as OAuthCredentials

        LOG.debug('Using a secure gRPC connection over OAuth:')

        credentials = OAuthCredentials(
            token=settings.oauth.token,
            refresh_token=settings.oauth.refresh_token,
            id_token=settings.oauth.id_token,
            token_uri=settings.oauth.token_uri,
            client_id=settings.oauth.client_id,
            client_secret=settings.oauth.client_secret)
        return secure_authorized_channel(credentials, RefreshRequester(), target, options=options)

    if settings.ssl_settings:
        cert_chain = read_file_bytes(settings.ssl_settings.cert_file)
        cert = read_file_bytes(settings.ssl_settings.cert_key_file)
        ca_cert = read_file_bytes(settings.ssl_settings.ca_file)

        LOG.debug('Using a secure gRPC connection:')
        LOG.debug('    target: %s', target)
        LOG.debug('    root_certificates: contents of %s', settings.ssl_settings.ca_file)
        LOG.debug('    private_key: contents of %s', settings.ssl_settings.cert_key_file)
        LOG.debug('    certificate_chain: contents of %s', settings.ssl_settings.cert_file)

        credentials = ssl_channel_credentials(
            root_certificates=ca_cert,
            private_key=cert,
            certificate_chain=cert_chain)
        return secure_channel(target, credentials, options)
    else:
        LOG.debug('Using an insecure gRPC connection...')
        return insecure_channel(target, options)


class GRPCv1Connection(_LedgerConnection):
    def __init__(self,
                 context: _LedgerConnectionContext,
                 settings: HTTPConnectionSettings,
                 context_path: Optional[str]):
        super(GRPCv1Connection, self).__init__(context, settings, context_path)
        from . import model as G

        self._closed = Event()
        self._channel = grpc_create_channel(settings)
        self.command_service = G.CommandServiceStub(self._channel)
        self.transaction_service = G.TransactionServiceStub(self._channel)
        self.package_service = G.PackageServiceStub(self._channel)
        self.ledger_identity_service = G.LedgerIdentityServiceStub(self._channel)
        self.time_service = G.TimeServiceStub(self._channel)

    def close(self):
        try:
            self._closed.set()
            self._channel.close()
        except:
            LOG.warning('An exception was thrown when trying to close down connections.')
        finally:
            super().close()

