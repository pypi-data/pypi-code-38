#
#   Copyright 2018 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import asyncio
import logging

from typing import Any, TYPE_CHECKING

import aiopg  # type: ignore
import psycopg2  # type: ignore

from .session import Session

if TYPE_CHECKING:
    from .application import Application  # noqa


# Delay in seconds for polling to populate the monkey patched connection
# closure event
MONKEY_PATCHED_CONNECTION_CLOSURE_POLL_DELAY = 1

# Maximum delay in seconds between listener reconnection attempts
LISTENER_MAXIMUM_RECONNECT_DELAY = 64


class Endpoint:
    def __init__(self, application: 'Application', path: str) -> None:
        self.application = application
        self.path = path

        self.config = application.config[path]

        self.acceptable_schemas = [schema.strip() for schema in self.config['acceptable-schemas'].split(",")]

        self.logger = EndpointLoggerAdapter(
            logging.getLogger(), {'endpoint': self})

        self.sessions = []  # type: List[Session]

        self.database_listener = EndpointDatabaseListener(self)
        self.db_pool = None  # type: aiopg.Pool

    async def start(self) -> None:
        self.logger.debug("Endpoint starting")

        dsn = self.config['dsn'] + " application_name='wspg'"

        self.db_pool = await aiopg.create_pool(
            dsn, minsize=0, echo=self.application.args.verbose)

        await self.database_listener.start()

        self.logger.info("Endpoint started")

    async def websocket_handler(self, websocket: Any) -> None:
        session = Session(self, websocket)

        self.sessions.append(session)

        try:
            await session.websocket_handler()
        finally:
            asyncio.ensure_future(self.database_listener.unlisten_all(session))
            self.sessions.remove(session)
            session.logger.info("Session removed")


class EndpointLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):  # type: ignore
        msg = "[{path}] {msg}".format(
            path=self.extra['endpoint'].path,
            msg=msg)

        return msg, kwargs


class EndpointDatabaseListener:
    def __init__(self, endpoint: Endpoint) -> None:
        self.endpoint = endpoint
        self.logger = endpoint.logger

        self.connection = None

        self.ready = False

        self.channel_subscriptions = {}  # type: Dict[str, List[Session]]
        self.subscriptions_lock = asyncio.Lock()

    async def start(self) -> None:
        asyncio.ensure_future(self.listener())

    async def listener(self) -> None:
        deliverer = None
        reconnect_delay = 1

        while True:
            try:
                async with self.endpoint.db_pool.acquire() as connection:
                    monkey_patch_connection_closure_event(connection)

                    self.logger.info("Database listener connected")
                    reconnect_delay = 1
                    self.connection = connection

                    await self.reattach_subscriptions()

                    self.ready = True
                    self.notify_ready_change()

                    deliverer = asyncio.ensure_future(
                        self.deliver_notifications(connection))

                    await connection.closure_event.wait()

            except psycopg2.OperationalError as e:
                msg = "Error in database listener connection: {}"
                self.logger.error(msg.format(e))

            finally:
                if deliverer:
                    deliverer.cancel()
                    deliverer = None

                if self.connection is not None:
                    self.connection = None

                if self.ready:
                    self.ready = False
                    self.notify_ready_change()

            reconnect_delay = min(
                reconnect_delay*2, LISTENER_MAXIMUM_RECONNECT_DELAY)
            msg = "No database listener connection - will reconnect in {}s"
            self.logger.warning(msg.format(reconnect_delay))

            await asyncio.sleep(reconnect_delay)

    def notify_ready_change(self) -> None:
        for session in self.endpoint.sessions:
            session.send_database_readiness(self.ready)

    async def reattach_subscriptions(self) -> None:
        async with self.subscriptions_lock:
            for channel in self.channel_subscriptions:
                await self._listen(channel)

    async def deliver_notifications(self, connection: Any) -> None:
        while True:
            notification = await connection.notifies.get()
            await self.deliver_notification(notification)

    async def deliver_notification(self, notification: Any) -> None:
        async with self.subscriptions_lock:
            sessions = self.channel_subscriptions.get(notification.channel, [])

            for session in sessions:
                session.send_notification(notification)

    async def listen(self, session: Session, channel: str) -> None:
        async with self.subscriptions_lock:
            first_on_channel = False

            if channel not in self.channel_subscriptions:
                self.channel_subscriptions[channel] = []

                first_on_channel = True

            if session in self.channel_subscriptions[channel]:
                return

            self.channel_subscriptions[channel].append(session)

            if first_on_channel:
                await self._listen(channel)

    async def unlisten(self, session: Session, channel: str) -> None:
        async with self.subscriptions_lock:
            if channel not in self.channel_subscriptions:
                return

            await self._locked_unlisten(session, channel)

    async def unlisten_all(self, session: Session) -> None:
        async with self.subscriptions_lock:
            for channel in list(self.channel_subscriptions):
                await self._locked_unlisten(session, channel)

    async def _locked_unlisten(self, session: Session, channel: str) -> None:
        if session not in self.channel_subscriptions[channel]:
            return

        self.channel_subscriptions[channel].remove(session)

        if not self.channel_subscriptions[channel]:
            del self.channel_subscriptions[channel]
            await self._unlisten(channel)

    async def _listen(self, channel: str) -> None:
        listen_sql = psycopg2.sql.SQL("LISTEN {}").format(psycopg2.sql.Identifier(channel))
        async with self.connection.cursor() as cursor:
            await cursor.execute(listen_sql)

    async def _unlisten(self, channel: str) -> None:
        unlisten_sql = psycopg2.sql.SQL("UNLISTEN {}").format(psycopg2.sql.Identifier(channel))
        async with self.connection.cursor() as cursor:
            await cursor.execute(unlisten_sql)


def monkey_patch_connection_closure_event(connection: Any) -> None:
    connection.closure_event = asyncio.Event()
    monkey_patched_connection_closure_poll(connection)


def monkey_patched_connection_closure_poll(connection: Any) -> None:
    if connection.closed:
        connection.closure_event.set()
        return

    asyncio.get_event_loop().call_later(
        MONKEY_PATCHED_CONNECTION_CLOSURE_POLL_DELAY,
        monkey_patched_connection_closure_poll,
        connection)
