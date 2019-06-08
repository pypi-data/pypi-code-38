from .manager import Manager
from tornado import gen
from tornado.options import options
from aioredis.pubsub import Receiver
from aioredis.abc import AbcChannel
from ..utils import rd_session
from ..utils import json_utils
from . import context
import aioredis
import asyncio
import logging
import json
import uuid

LOGGER = logging.getLogger(__name__)


class RedisManager(Manager):
    """
        A subclass of manager that delegates
        to a redis queue. It also subscribes
        to broadcasts and sends them on.
    """

    def _setup_queues_(self, workers):
        self._rd_client = {}
        self.broadcast_redis = None
        self.subscribe_redis = None
        self.ioloop.spawn_callback(self.setup_redis)

    async def setup_redis(self):
        loop = asyncio.get_event_loop()
        self.broadcast_redis = await rd_session.connect()
        self.subscribe_redis = await rd_session.connect()
        self.mpsc = Receiver(loop=loop)

        async def reader(mpsc):
            async for channel, msg in self.mpsc.iter():
                assert isinstance(channel, AbcChannel)
                LOGGER.debug("Got %r in channel %r", msg, channel)
                if channel.name == b"broadcast":
                    Manager._broadcast_(self, **json_utils.loads(msg))
                else:
                    client = self._rd_client.get(channel.name.decode("utf-8"))
                    result = json_utils.loads(msg)
                    if result and result.get("is_context") is True:
                        LOGGER.debug("found context")
                        messages = result["result"]["messages"]
                        result["result"] = result["result"]["result"]
                        if client:
                            LOGGER.debug("writing to client %s %r", client.id, result)
                            client.write_message(json_utils.dumps(result))
                        for signal, message, filter_clients in messages:
                            self.broadcast(signal, message, filter_clients)
                    elif client:
                        LOGGER.debug("writing to client %s %r", client.id, result)
                        client.write_message(json_utils.dumps(result))

        asyncio.ensure_future(reader(self.mpsc))
        LOGGER.info("subscribed to redis")
        await self.subscribe_redis.subscribe(self.mpsc.channel("broadcast"))
        LOGGER.info("listening for broadcast")

    def add_client(self, client):
        super().add_client(client)
        self.ioloop.add_callback(self._add_client, client)

    async def _add_client(self, client):
        channel = f"channel:{client.id}"
        self._rd_client[channel] = client
        await self.subscribe_redis.subscribe(self.mpsc.channel(channel))
        LOGGER.info(f"listening for {channel}")

    def remove_client(self, client):
        super().remove_client(client)
        self.ioloop.add_callback(self._remove_client, client)

    async def _remove_client(self, client):
        channel = f"channel:{client.id}"
        await self.subscribe_redis.unsubscribe(channel)
        if channel in self._rd_client.keys():
            del self._rd_client[channel]
        LOGGER.info(f"stopped {channel}")

    async def _broadcast_(self, signal, message, filter_clients=None):
        msg = {"signal": signal, "message": message, "filter_clients": filter_clients}
        LOGGER.info("broadcasting %s", signal)
        if self.broadcast_redis:
            await self.broadcast_redis.publish("broadcast", json_utils.dumps(msg))

    @gen.coroutine
    def put(self, content):
        if content.get("client_id"):
            content["reply"] = "channel:{client_id}".format(**content)
        procedure = self.get_target(content["method"])
        pn = f"{procedure.__module__}:{procedure.__name__}"
        content["method"] = pn
        yield self.broadcast_redis.execute(
            "rpush", options.redis_work_q, json_utils.dumps(content)
        )
