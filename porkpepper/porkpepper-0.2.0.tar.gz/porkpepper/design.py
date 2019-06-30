from typing import *
import fnmatch
import json
import inspect
import asyncio
from .error import *
from .result import Result
from .node import PorkPepperNode
from .redis_server import RedisServer


PORKPEPPER_ATTR = "__porkpepper__"


class SocketBasedRedisServer(RedisServer):
    MAX_DB_COUNT = 2
    LOADS = json.loads

    def _session_db_size(self) -> int:
        app = self.app
        if app is not None:
            return app.sessions_count
        else:
            return 0

    def _user_db_size(self) -> int:
        app = self.app
        if app is not None:
            return app.users_count
        else:
            return 0

    @classmethod
    def _session_to_dict(cls, session):
        return dict(
                    type="session",
                    session_id=session.session_id,
                    create_timestamp=session.create_timestamp,
                    current_user=session.current_user
                )

    async def get(self, session, key) -> Result[bytes]:
        app = self.app
        if session.current_db == 0:
            session = app.get_session(key) if app is not None else None
            if session:
                status = self._session_to_dict(session)
                return Result(json.dumps(status))
        elif session.current_db == 1:
            sessions = app.get_user(key) if app is not None else None
            if sessions:
                status = dict(type="user", sessions=[self._session_to_dict(session) for session in sessions])
                return Result(json.dumps(status))
        return Result(None)

    async def getset(self, session, key, value) -> Result:
        return Result(NotImplementedError())

    @classmethod
    async def send_task(cls, session, message):
        try:
            await session.send(message)
        except Exception as e:
            pass

    async def set(self, session, key, value) -> Result:
        app = self.app
        if session.current_db == 0:
            session = app.get_session(key) if app is not None else None
            if session:
                asyncio.ensure_future(asyncio.Task(self.send_task(session, self.LOADS(value))))
        return Result(True)

    async def key_type(self, session, key):
        return Result("string")

    async def ping(self, session):
        return Result("PONG")

    def info_arguments(self):
        service_list = list()
        service_list.append(
            (0,
             dict(
                 keys=self._session_db_size(),
             )
             ))
        service_list.append(
            (1,
             dict(
                 keys=self._user_db_size(),
             )
             ))
        arguments = super(SocketBasedRedisServer, self).info_arguments()
        arguments.update(porkpepper_mode="websocket", keyspace=service_list)
        return arguments

    async def info(self, session):
        info_arguments = self.info_arguments()
        info = self.INFO_TEMPLATE.render(info_arguments)
        return Result(info)

    async def auth(self, session, password) -> Result[bool]:
        if self.password is None:
            return Result(NoPasswordError("ERR Client sent AUTH, but no password is set"))
        auth = self.password or ""
        return Result(password == auth.encode("utf8"))

    async def ttl(self, session, key):
        return Result(-1)

    def _scan_sessions(self, pattern=None):
        app = self.app
        keys = list()
        sessions = app.all_sessions() if app is not None else list()
        for session in sessions:
            if pattern is not None:
                if fnmatch.fnmatch(session.session_id, pattern):
                    keys.append(session.session_id)
            else:
                keys.append(session.session_id)
        return keys

    def _scan_users(self, pattern=None):
        app = self.app
        keys = list()
        users = app.all_users() if app is not None else list()
        for user in users:
            if pattern is not None:
                if fnmatch.fnmatch(user, pattern):
                    keys.append(user)
            else:
                keys.append(user)
        return keys

    async def scan(self, session, pattern):
        if session.current_db == 0:
            keys = self._scan_sessions(pattern)
            return Result(keys)
        if session.current_db == 1:
            keys = self._scan_users(pattern)
            return Result(keys)
        return Result(list())

    async def dbsize(self, session):
        if session.current_db == 0:
            size = self._session_db_size()
            return Result(size)
        if session.current_db == 1:
            size = self._user_db_size()
            return Result(size)
        return Result(0)

    async def select(self, session, db):
        if 0 <= db < self.MAX_DB_COUNT:
            session.current_db = db
            return Result(True)
        else:
            return Result(DatabaseNotFound())

    async def config(self, session, get_set, field, value=None):
        if get_set == b'GET' and field == b'databases':
            return Result([b'databases', f'{self.MAX_DB_COUNT}'.encode("utf8")])
        return Result(CommandNotFound())

    async def delete(self, session, key):
        if session.current_db == 0:
            app = self.app
            if app is not None:
                session = app.get_session(key)
                if session:
                    await session.close()
                return Result(1 if session else 0)
        return Result(0)


class WebsocketNode(PorkPepperNode):
    def __init__(self, session_class, websocket_path, redis_server=SocketBasedRedisServer, **kwargs):
        super(WebsocketNode, self).__init__(
            redis_server=redis_server,
            session_class=session_class,
            websocket_path=websocket_path,
            **kwargs
        )

    async def start(self, service_map: Dict[int, Type] = None, redis_host="127.0.0.1", redis_port=6379, **kwargs):
        return await super(WebsocketNode, self).start(
            enable_websocket=True,
            redis_host=redis_host,
            redis_port=redis_port, **kwargs
        )

    async def serve(self, service_map: Dict[int, Type] = None, redis_host="127.0.0.1", redis_port=6379, **kwargs):
        await super(WebsocketNode, self).serve(
            enable_websocket=True,
            redis_host=redis_host,
            redis_port=redis_port,
            **kwargs
        )


def service(key: str, output: bool = False, description: Optional[str] = None, meta: Optional[Dict] = None):
    def wrap(func):
        signature = inspect.signature(func)
        setattr(func, PORKPEPPER_ATTR, dict(
            key=key,
            output=output,
            signature=signature,
            description=description,
            meta=meta if meta else dict()
        ))
        return func

    return wrap


class ServiceBasedRedisServer(RedisServer):
    MAX_DB_COUNT = 0
    SERVICE_MAP = dict()

    async def get(self, session, key) -> Result[bytes]:
        if session.current_db < 0 or session.current_db >= self.MAX_DB_COUNT:
            return Result(DatabaseNotFound())
        current_service = self.SERVICE_MAP.get(session.current_db, None)
        if not current_service:
            return Result(DatabaseNotFound())
        service_map = current_service["map"]
        service_dict = service_map.get(key, None)
        if not service_dict:
            return Result(None)
        service_arguments = service_dict["args"]
        output = {
            "type": "api",
            "key": service_arguments["key"],
            "output": service_arguments["output"],
            "signature": str(service_arguments["signature"]),
            "description": service_arguments["description"],
            "meta": service_arguments["meta"],
        }
        return Result(json.dumps(output))

    async def getset(self, session, key, value) -> Result:
        if session.current_db < 0 or session.current_db >= self.MAX_DB_COUNT:
            return Result(DatabaseNotFound())
        current_service = self.SERVICE_MAP.get(session.current_db, None)
        if not current_service:
            return Result(DatabaseNotFound())
        service_map = current_service["map"]
        service_dict = service_map.get(key, None)
        if not service_dict:
            return Result(KeyNotFound())
        handler = service_dict["handler"]
        service_arguments = service_dict["args"]
        loads = current_service["loads"]
        dumps = current_service["dumps"]
        if not service_arguments.get("output", False):
            return Result(WrongCommand())
        try:
            signature = service_arguments["signature"]
            message = loads(value)
            if "kwargs" in signature.parameters:
                result = await handler(**message)
            else:
                result = await handler(message=message)
            return Result(dumps(result))
        except Exception as e:
            return Result(e)

    async def set(self, session, key, value) -> Result:
        if session.current_db < 0 or session.current_db >= self.MAX_DB_COUNT:
            return Result(DatabaseNotFound())
        current_service = self.SERVICE_MAP.get(session.current_db, None)
        if not current_service:
            return Result(DatabaseNotFound())
        service_map = current_service["map"]
        service_dict = service_map.get(key, None)
        if not service_dict:
            return Result(KeyNotFound())
        handler = service_dict["handler"]
        service_arguments = service_dict["args"]
        loads = current_service["loads"]
        try:
            signature = service_arguments["signature"]
            message = loads(value)
            if "kwargs" in signature.parameters:
                await handler(**message)
            else:
                await handler(message=message)
            return Result(True)
        except Exception as e:
            return Result(e)

    async def key_type(self, session, key):
        return Result("string")

    async def ping(self, session):
        return Result("PONG")

    def info_arguments(self):
        service_list = list()
        for db in range(self.MAX_DB_COUNT):
            service_list.append(
                (db,
                 dict(
                     keys=len(self.SERVICE_MAP.get(db, dict()).get("map", list())),
                 )
                 ))
        arguments = super(ServiceBasedRedisServer, self).info_arguments()
        arguments.update(porkpepper_mode="service", keyspace=service_list)
        return arguments

    async def info(self, session):
        info_arguments = self.info_arguments()
        info = self.INFO_TEMPLATE.render(info_arguments)
        return Result(info)

    async def ttl(self, session, key):
        return Result(-1)

    async def scan(self, session, pattern):
        if session.current_db < 0 or session.current_db >= self.MAX_DB_COUNT:
            return Result(DatabaseNotFound())
        current_service = self.SERVICE_MAP.get(session.current_db, None)
        if not current_service:
            return Result(list())
        service_map = current_service["map"]
        return Result(list(service_map.keys()))

    async def dbsize(self, session):
        if session.current_db < 0 or session.current_db >= self.MAX_DB_COUNT:
            return Result(DatabaseNotFound())
        current_service = self.SERVICE_MAP.get(session.current_db, None)
        if not current_service:
            return Result(0)
        service_map = current_service["map"]
        return Result(len(service_map))

    async def select(self, session, db):
        if 0 <= db < self.MAX_DB_COUNT:
            session.current_db = db
            return Result(True)
        else:
            return Result(DatabaseNotFound())

    async def config(self, session, get_set, field, value=None):
        if get_set == b'GET' and field == b'databases':
            return Result([b'databases', f'{self.MAX_DB_COUNT}'.encode("utf8")])
        return Result(CommandNotFound())


class RedisServiceNode(PorkPepperNode):
    def __init__(self, redis_server=ServiceBasedRedisServer, **kwargs):
        super(RedisServiceNode, self).__init__(redis_server=redis_server, **kwargs)

    def clear_service(self):
        if self._redis_server:
            self._redis_server.MAX_DB_COUNT = 0
            self._redis_server.SERVICE_MAP.clear()

    def update_service(self, db: int, new_service: Type):
        members = inspect.getmembers(new_service, inspect.ismethod)
        service_map = dict()
        for _, member in members:
            if not inspect.iscoroutinefunction(member):
                continue
            sign = inspect.signature(member)
            if "message" not in sign.parameters and "kwargs" not in sign.parameters:
                continue
            if not hasattr(member, PORKPEPPER_ATTR):
                continue
            service_arguments = getattr(member, PORKPEPPER_ATTR)
            key = service_arguments.get("key", None)
            if key in service_map:
                raise KeyError
            if not isinstance(key, str):
                raise ValueError
            service_map[key] = dict(handler=member, args=service_arguments)
        loads = getattr(new_service, "LOADS", json.loads)
        dumps = getattr(new_service, "DUMPS", json.dumps)
        if self._redis_server:
            if db + 1 > self._redis_server.MAX_DB_COUNT:
                self._redis_server.MAX_DB_COUNT = db + 1
            self._redis_server.SERVICE_MAP[db] = dict(loads=loads, dumps=dumps, map=service_map)
            
    async def _initialize_service_map(self, service_map: Dict[int, Type] = None):
        if service_map:
            for db, service_type in service_map.items():
                if not isinstance(db, int):
                    raise ValueError
                self.update_service(db, service_type)
        else:
            self.clear_service()

    async def start(self, service_map: Dict[int, Type] = None, redis_host="127.0.0.1", redis_port=6379, **kwargs):
        await self._initialize_service_map(service_map)
        return await super(RedisServiceNode, self).start(
            enable_websocket=False,
            redis_host=redis_host,
            redis_port=redis_port, **kwargs
        )

    async def serve(self, service_map: Dict[int, Type] = None, redis_host="127.0.0.1", redis_port=6379, **kwargs):
        await self._initialize_service_map(service_map)
        await super(RedisServiceNode, self).serve(
            enable_websocket=False,
            redis_host=redis_host,
            redis_port=redis_port,
            **kwargs
        )


__all__ = ["WebsocketNode", "RedisServiceNode", "service", "SocketBasedRedisServer", "ServiceBasedRedisServer", ]
