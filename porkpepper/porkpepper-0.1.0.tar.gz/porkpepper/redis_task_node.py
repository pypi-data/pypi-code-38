from typing import *
import asyncio
from .error import *
from .result import Result


class RedisTaskNode:
    def __init__(self, command, fa: Optional[Tuple[Callable, Union[None, Dict]]], writer_queue: asyncio.Queue):
        self.command: bytes = command
        self.fa = fa
        self.writer_queue = writer_queue
        self.result = None

    @classmethod
    async def create(cls, reader, writer_queue: asyncio.Queue, need_auth_event: asyncio.Event, mixin: 'RedisServerBase') -> Result['RedisTaskNode']:
        idle_timeout = mixin.IDLE_TIMEOUT
        line = await asyncio.wait_for(reader.readline(), timeout=idle_timeout)
        if not line:
            return Result(EOFError())
        args_count_result = mixin.get_count(line)
        if args_count_result.is_error:
            return Result(args_count_result.error)
        args_count = args_count_result.unwrap()
        commands = list()
        for _ in range(args_count):
            data = await asyncio.wait_for(reader.readline(), timeout=idle_timeout)
            binary_size_result = mixin.get_binary_size(data)
            if binary_size_result.is_error:
                return Result(binary_size_result.error)
            binary_size = binary_size_result.unwrap()
            data = await asyncio.wait_for(reader.readexactly(binary_size + 2), timeout=idle_timeout)
            commands.append(data[:-2])
        if not commands:
            return Result(RedisProtocolFormatError())
        command = commands[0].upper()
        if command == b'AUTH':
            if len(commands) > 1:
                password = commands[1]
            else:
                password = b''
            fa = (mixin.auth, dict(password=password), )
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        if need_auth_event.is_set():
            node = RedisTaskNode(b'AUTH', None, writer_queue)
            node.result = Result(NoPasswordError("NOAUTH Authentication required."))
            return Result(node)
        if command == b'CONFIG':
            if len(commands) != 3:
                return Result(RedisProtocolFormatError())
            fa = (mixin.config, dict(get_set=commands[1], field=commands[2]))
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'INFO':
            fa = (mixin.info, None)
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'SELECT':
            if len(commands) != 2:
                return Result(RedisProtocolFormatError())
            database_id = int(commands[1])
            fa = (mixin.select, dict(db=database_id))
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'DBSIZE':
            if len(commands) != 1:
                return Result(RedisProtocolFormatError())
            fa = (mixin.dbsize, None)
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'PING':
            fa = (mixin.ping, None)
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'SET':
            if len(commands) < 3:
                return Result(RedisProtocolFormatError())
            key = commands[1].decode("utf8").strip()
            value = commands[2]
            fa = (mixin.set, dict(key=key, value=value))
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'GET':
            if len(commands) != 2:
                return Result(RedisProtocolFormatError())
            key = commands[1].decode("utf8").strip()
            fa = (mixin.get, dict(key=key))
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'TYPE':
            if len(commands) != 2:
                return Result(RedisProtocolFormatError())
            key = commands[1].decode("utf8").strip()
            fa = (mixin.key_type, dict(key=key))
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'TTL':
            if len(commands) != 2:
                return Result(RedisProtocolFormatError())
            key = commands[1].decode("utf8").strip()
            fa = (mixin.ttl, dict(key=key))
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        elif command == b'SCAN':
            if len(commands) < 2 or len(commands) % 2:
                return Result(RedisProtocolFormatError())
            pattern = None
            args_pairs = zip(commands[2::2], commands[3::2])
            for arg_name, arg_value in args_pairs:
                if arg_name.upper() == b'MATCH':
                    pattern = f'^{arg_value.decode("utf8").replace("*", ".+")}$'
                elif arg_name.upper() == b'COUNT':
                    pass
            fa = (mixin.scan, dict(pattern=pattern))
            node = RedisTaskNode(command, fa, writer_queue)
            return Result(node)
        else:
            node = RedisTaskNode(b'NOOP', None, writer_queue)
            node.result = Result(CommandNotFound())
            return Result(node)

    async def write_result(self, writer, need_auth_event: asyncio.Event, mixin: 'RedisServerMixin') -> Result[bool]:
        command = self.command
        if command == b'AUTH':
            auth_result = self.result
            if auth_result.is_error:
                if isinstance(auth_result.error, ExceptionWithReplyError):
                    error_reply = auth_result.error.reply
                else:
                    error_reply = "ERR"
                binary_result = mixin.set_err(error_reply)
                need_auth_event.set()
            elif not auth_result.unwrap():
                binary_result = mixin.set_err("ERR invalid password")
                need_auth_event.set()
            else:
                binary_result = mixin.set_ok()
                need_auth_event.clear()
            writer.write(binary_result.unwrap())
        elif need_auth_event.is_set():
            binary_result = mixin.set_err("NOAUTH Authentication required.")
            writer.write(binary_result.unwrap())
        elif command == b'CONFIG':
            config_result = self.result
            if config_result.is_error:
                return Result(config_result.error)
            binary_lines = config_result.unwrap()
            item_size = len(binary_lines)
            writer.write(mixin.set_count(item_size).unwrap())
            for binary in binary_lines:
                binary_result = mixin.set_binary(binary)
                writer.write(binary_result.unwrap())
        elif command == b'INFO':
            info_result = self.result
            if info_result.is_error:
                return Result(info_result.error)
            binary_result = mixin.set_binary(info_result.unwrap())
            if binary_result.is_error:
                return Result(binary_result.error)
            writer.write(binary_result.unwrap())
        elif command == b'SELECT':
            select_result = self.result
            if select_result.is_error:
                writer.write(mixin.set_err("ERR invalid DB index").unwrap())
            else:
                writer.write(mixin.set_ok().unwrap())
        elif command == b'DBSIZE':
            dbsize_result = self.result
            if dbsize_result.is_error:
                return Result(dbsize_result.error)
            binary_result = mixin.set_integer(dbsize_result.unwrap())
            if binary_result.is_error:
                return Result(binary_result.error)
            writer.write(binary_result.unwrap())
        elif command == b'PING':
            ping_result = self.result
            if ping_result.is_error:
                return Result(ping_result.error)
            binary_result = mixin.set_ok(ping_result.unwrap())
            if binary_result.is_error:
                return Result(binary_result.error)
            writer.write(binary_result.unwrap())
        elif command == b'SET':
            set_result = self.result
            if set_result.is_error:
                return Result(set_result.error)
            binary_result = mixin.set_ok()
            if binary_result.is_error:
                return Result(binary_result.error)
            writer.write(binary_result.unwrap())
        elif command == b'GET':
            get_result = self.result
            if get_result.is_error:
                return Result(get_result.error)
            if get_result.unwrap() is None:
                binary_result = mixin.set_nil()
            else:
                binary_result = mixin.set_binary(get_result.unwrap())
            if binary_result.is_error:
                return Result(binary_result.error)
            writer.write(binary_result.unwrap())
        elif command == b'TYPE':
            key_type_result = self.result
            if key_type_result.is_error:
                return Result(key_type_result.error)
            binary_result = mixin.set_ok(key_type_result.unwrap())
            if binary_result.is_error:
                return Result(binary_result.error)
            writer.write(binary_result.unwrap())
        elif command == b'TTL':
            ttl_result = self.result
            if ttl_result.is_error:
                return Result(ttl_result.error)
            binary_result = mixin.set_integer(ttl_result.unwrap())
            if binary_result.is_error:
                return Result(binary_result.error)
            writer.write(binary_result.unwrap())
        elif command == b'SCAN':
            scan_result = self.result
            if scan_result.is_error:
                return Result(scan_result.error)
            keys = scan_result.unwrap()
            count = len(keys)
            writer.write(mixin.set_count(2).unwrap())
            writer.write(mixin.set_binary(0).unwrap())
            writer.write(mixin.set_count(count).unwrap())
            for key in keys:
                writer.write(mixin.set_binary(key).unwrap())
                await writer.drain()
        else:
            binary_result = mixin.set_err("COMMAND NOT EXISTS")
            writer.write(binary_result.unwrap())
        await writer.drain()
        return Result(True)


__all__ = ["RedisTaskNode", ]
