from typing import *
import os
import time
import math
import random
import string
import asyncio
from jinja2 import Template
from .result import *
from .utils import *
from .redis_protocol import RedisProtocol
from .redis_task_node import RedisTaskNode
from .redis_session import RedisSession


class RedisServerBase(RedisProtocol):
    IDLE_TIMEOUT = 60
    WORKER_QUEUE = asyncio.Queue()
    ENABLE_AUTH = False
    MAX_DB_COUNT = 1

    INFO_TEMPLATE = Template(
        """# Server
redis_version:3.0.0
porkpepper_version:0.1.0
porkpepper_mode:{{ porkpepper_mode }}
process_id:{{ process_id }}
run_id:{{ run_id }}
tcp_port:{{ tcp_port }}
uptime_in_seconds:{{ uptime_in_seconds }}
uptime_in_days:{{ uptime_in_days }}

# Clients
connected_clients:{{ connected_clients }}

# Stats
total_connections_received:{{ total_connections_received }}
total_commands_processed:{{ total_commands_processed }}
instantaneous_ops_per_sec:{{ instantaneous_ops_per_sec }}
total_net_input_bytes:{{ total_net_input_bytes }}
total_net_output_bytes:{{ total_net_output_bytes }}

# Replication
role:master
connected_slaves:0
master_repl_offset:0

# Cluster
cluster_enabled:0

# Keyspace
{% for db, info in keyspace %}db{{ db }}:keys={{ info["keys"] }},expires=0,avg_ttl=0\r\n{% endfor %}
""", newline_sequence="\r\n")

    def __init__(self, app=None):
        self._http_app = app
        self.host = None
        self.port = None
        self.connections = set()
        self.start_time = 0
        self.run_id = ""
        self.total_connections_received = 0
        self.total_commands_processed = 0
        self.instantaneous_ops_per_sec = 0
        self.total_net_input_bytes = 0
        self.total_net_output_bytes = 0
        self.init_property()

    def init_property(self):
        self.connections = set()
        self.start_time = int(time.time())
        random_key = ''.join(random.choices(string.ascii_letters, k=128))
        run_id = create_base58_key(random_key, length=20, prefix="PP", timestamp=True)
        self.run_id = run_id
        self.total_connections_received = 0
        self.total_commands_processed = 0
        self.instantaneous_ops_per_sec = 0
        self.total_net_input_bytes = 0
        self.total_net_output_bytes = 0

    @property
    def app(self):
        return self._http_app

    @property
    def password(self):
        return None

    async def handle_stream(self, reader, writer):
        session = None
        try:
            self.connections.add((reader, writer, ))
            self.total_connections_received += 1
            auth = self.ENABLE_AUTH
            need_auth = True if auth else False
            need_auth_event = asyncio.Event()
            if need_auth:
                need_auth_event.set()
            session = RedisSession()
            session.reader = reader
            session.write = writer
            session.need_auth_event = need_auth_event
            session.server = self
            idle_timeout = self.IDLE_TIMEOUT
            while True:
                node_result = await RedisTaskNode.create(session, self)
                if node_result.is_error:
                    raise node_result.error
                if node_result.is_some:
                    node: RedisTaskNode = node_result.unwrap()
                    if node.fa:
                        func, kwargs = node.fa
                        if kwargs:
                            result = await func(**kwargs)
                        else:
                            result = await func()
                        node.result = result
                    write_result = await asyncio.wait_for(node.write_result(session, self),
                                                          timeout=idle_timeout)
                self.total_commands_processed += 1
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
            self.connections.remove((reader, writer, ))
            if session:
                session.reader = None
                session.write = None
                session.server = None

    def info_arguments(self):
        return {
            "porkpepper_version": "0.1.0",
            "porkpepper_mode": "",
            "process_id": os.getpid(),
            "run_id": self.run_id,
            "tcp_port": self.port,
            "uptime_in_seconds": int(time.time()) - self.start_time,
            "uptime_in_days": math.ceil((time.time() - self.start_time) / (24 * 60 * 60)),
            "connected_clients": len(self.connections),
            "keyspace": list(),
            "total_connections_received": self.total_connections_received,
            "total_commands_processed": self.total_commands_processed,
            "instantaneous_ops_per_sec": self.instantaneous_ops_per_sec,
            "total_net_input_bytes": self.total_net_input_bytes,
            "total_net_output_bytes": self.total_net_output_bytes,
        }

    async def serve(self, host='127.0.0.1', port=6379, forever=True, after_start=None, **kwargs):
        self.host = host
        self.port = port
        server = await asyncio.start_server(self.handle_stream, host, port, **kwargs)
        if after_start:
            after_start()
        if forever:
            async with server:
                await server.serve_forever()
        else:
            return server

    async def get(self, session, key) -> Result[bytes]:
        return Result(NotImplementedError())

    async def getset(self, session, key, value) -> Result:
        return Result(NotImplementedError())

    async def set(self, session, key, value) -> Result:
        return Result(NotImplementedError())

    async def key_type(self, session, key):
        return Result(NotImplementedError())

    async def ping(self, session):
        return Result(NotImplementedError())

    async def info(self, session):
        return Result(NotImplementedError())

    async def auth(self, session, password) -> Result[bool]:
        """
        如果是连接状态问题或者非密码对错的情况下，这里应返回 Result[Exception]
        判断密码正确时，应返回 Result[bool]
        :param session:
        :param password:
        :return:
        """
        return Result(NotImplementedError())

    async def ttl(self, session, key):
        return Result(NotImplementedError())

    async def scan(self, session, pattern):
        return Result(NotImplementedError())

    async def dbsize(self, session):
        return Result(NotImplementedError())

    async def select(self, session, db):
        return Result(NotImplementedError())

    async def config(self, session, get_set, field, value=None):
        return Result(NotImplementedError())

    async def delete(self, session, key):
        return Result(NotImplementedError())


__all__ = ["RedisServerBase", ]
