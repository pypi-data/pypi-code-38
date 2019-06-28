from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from concurrent.futures import ThreadPoolExecutor
from tornado import autoreload
from ..web.settings import settings
from ..utils.rd_session import connect
from ..utils.json_utils import dumps, loads
from ..utils.config import extend
from . import perform
import importlib
import threading
import asyncio
import logging

LOGGER = logging.getLogger(__name__)

"""
    Main worker file. It subscribes to the
    redis queue and broadcasts activity
"""


class Worker:
    def __init__(self, ioloop):
        self.ioloop = ioloop
        self.ioloop.set_default_executor(ThreadPoolExecutor())
        self.procedures = importlib.import_module(options.procedures)

    def get_params(self, content):
        if isinstance(content["params"], dict):
            return [], content["params"]
        elif isinstance(content["params"], list):
            return content["params"], {}
        else:
            raise Exception("Params neither list or dict")

    async def perform(self, content):
        actor = content.get("current_user")
        args, kwargs = self.get_params(content)
        method = content["method"]
        content["thread"] = threading.get_ident()
        if ":" in method:
            mod_name, func_name = method.split(":")
            procedure = getattr(importlib.import_module(mod_name), func_name)
        else:
            procedure = getattr(self.procedures, method)
        try:
            LOGGER.debug("%r %s %s", method, args, kwargs)
            result = await perform.perform(actor, procedure, args, kwargs)
            content["result"] = result
            if isinstance(result, perform.Context):
                content["is_context"] = True
        except Exception as ex:
            content["error"] = {"code": -32000, "message": str(ex)}
        return content

    async def _broadcast_(self, signal, message, filter_clients=None):
        msg = {"signal": signal, "message": message, "filter_clients": filter_clients}
        await self.broadcast_redis.publish("broadcast", dumps(msg))

    def broadcast(self, signal, message, filter_clients=None):
        """
            a thread safe way to broadcast
        """
        self.ioloop.spawn_callback(self._broadcast_, signal, message, filter_clients)

    async def do_work(self, val):
        content = loads(val[1].decode("utf-8"))
        if content.get("id"):
            await self._broadcast_("broadcast", {"working": content["id"]})
        content = await self.perform(content)
        if content.get("reply"):
            await self.broadcast_redis.publish(content["reply"], dumps(content))
            LOGGER.debug("published reply %s", content)

    async def work(self):
        """ Connects to redis a awaits messages from queue """
        self.broadcast_redis = await connect()
        self.work_q = await connect()
        LOGGER.info("ready for work")
        while True:
            val = await self.work_q.blpop(options.redis_work_q)
            if val:
                await self.do_work(val)
        self.work_q.close()
        await self.work_q.wait_closed()
        self.broadcast_redis.close()
        await self.broadcast_redis.wait_closed()

    async def put(self, content):
        await self.broadcast_redis.execute(
            "rpush", options.redis_work_q, dumps(content)
        )


def main():
    """ Creates Worker and starts tornado """
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    values = settings()
    if options.settings_extend:
        values = extend(options.settings_extend, values)

    assert options.redis_url
    autoreload.start()
    ioloop = IOLoop.current()
    perform._manager_ = Worker(ioloop=ioloop)
    for _ in range(options.workers):
        ioloop.spawn_callback(perform._manager_.work)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        logging.info("stopping")
