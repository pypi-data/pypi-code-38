from typing import *
import asyncio
from .result import *
from .redis_protocol import RedisProtocol
from .redis_task_node import RedisTaskNode


class RedisServerBase(RedisProtocol):
    IDLE_TIMEOUT = 60
    WORKER_QUEUE = asyncio.Queue()
    ENABLE_AUTH = False

    def __init__(self):
        self._http_app = None

    @property
    def app(self):
        return self._http_app

    async def worker(self):
        while True:
            try:
                node: RedisTaskNode = await self.WORKER_QUEUE.get()
                if node.fa:
                    func, kwargs = node.fa
                    if kwargs:
                        result = await func(**kwargs)
                    else:
                        result = await func()
                    node.result = result
                await node.writer_queue.put(node)
            except asyncio.CancelledError:
                return
            except Exception as e:
                pass

    async def handle_stream(self, reader, writer):
        try:
            auth = self.ENABLE_AUTH
            need_auth = True if auth else False
            need_auth_event = asyncio.Event()
            if need_auth:
                need_auth_event.set()
            writer_queue = asyncio.Queue()
            await asyncio.wait([
                self.reader_loop(reader, need_auth_event, writer_queue),
                self.writer_loop(writer, need_auth_event, writer_queue),
            ])
        except asyncio.TimeoutError as e:
            return Result(e)
        except Exception as e:
            return Result(e)
        finally:
            try:
                writer.close()
            except Exception as e:
                pass

    async def reader_loop(self, reader, need_auth_event: asyncio.Event, writer_queue: asyncio.Queue):
        try:
            while True:
                node_result = await RedisTaskNode.create(reader, writer_queue, need_auth_event, self)
                if node_result.is_error:
                    raise node_result.error
                if node_result.is_some:
                    await self.WORKER_QUEUE.put(node_result.unwrap())
        except asyncio.TimeoutError as e:
            return Result(e)
        except Exception as e:
            return Result(e)
        finally:
            await writer_queue.put(None)

    async def writer_loop(self, writer, need_auth_event: asyncio.Event, writer_queue: asyncio.Queue):
        idle_timeout = self.IDLE_TIMEOUT
        try:
            while True:
                node: Optional[RedisTaskNode] = await writer_queue.get()
                if node is None:
                    return
                write_result = await asyncio.wait_for(node.write_result(writer,  need_auth_event, self), timeout=idle_timeout)
                if write_result.is_error:
                    raise write_result.error
                elif not write_result.unwrap():
                    return
        except asyncio.TimeoutError as e:
            return Result(e)
        except Exception as e:
            return Result(e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                pass

    async def serve(self, host='127.0.0.1', port=6379):
        server = await asyncio.start_server(self.handle_stream, host, port)
        async with server:
            await asyncio.gather(server.serve_forever(), self.worker())

    async def get(self, key) -> Result[bytes]:
        return Result(NotImplementedError())

    async def getset(self, key, value) -> Result:
        return Result(NotImplementedError())

    async def set(self, key, value) -> Result:
        return Result(NotImplementedError())

    def hmget(self, key, *fields):
        return Result(NotImplementedError())

    def hmset(self, key, **fields):
        return Result(NotImplementedError())

    async def key_type(self, key):
        return Result(NotImplementedError())

    async def ping(self):
        return Result(NotImplementedError())

    async def info(self):
        return Result(NotImplementedError())

    def subscribe(self, channle):
        return Result(NotImplementedError())

    async def auth(self, password) -> Result[bool]:
        """
        如果是连接状态问题或者非密码对错的情况下，这里应返回 Result[Exception]
        判断密码正确时，应返回 Result[bool]
        :param password:
        :return:
        """
        return Result(NotImplementedError())

    async def ttl(self, key):
        return Result(NotImplementedError())

    async def scan(self, pattern):
        return Result(NotImplementedError())

    async def dbsize(self):
        return Result(NotImplementedError())

    async def select(self, db):
        return Result(NotImplementedError())

    async def config(self, get_set, field, value=None):
        return Result(NotImplementedError())


__all__ = ["RedisServerBase", ]
