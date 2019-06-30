from typing import *
from .result import Result
from .error import *


class RedisProtocol:
    CR_LF = [13, 10, ]

    @classmethod
    def set_nil(cls):
        buffer = "$-1\r\n".encode("utf8")
        return Result(buffer)

    @classmethod
    def set_integer(cls, n):
        if isinstance(n, bool):
            return Result(RedisProtocolFormatError())
        elif not isinstance(n, int):
            return Result(RedisProtocolFormatError())
        return Result(f":{n}\r\n".encode("utf8"))

    @classmethod
    def get_integer(cls, line: bytes):
        if isinstance(line, bytes):
            buffer = bytearray(line)
            if buffer.startswith(b":") and buffer.endswith(b"\r\n"):
                value_binary = buffer[1:-2]
                try:
                    count = int(value_binary)
                    return Result(count)
                except Exception as e:
                    return Result(e)
        return Result(RedisProtocolFormatError())

    @classmethod
    def set_ok(cls, reason: str = "OK"):
        if not isinstance(reason, str):
            return Result(RedisProtocolFormatError())
        return Result(f"+{reason}\r\n".encode("utf8"))

    @classmethod
    def set_err(cls, reason: str = "ERR"):
        if not isinstance(reason, str):
            return Result(RedisProtocolFormatError())
        return Result(f"-{reason}\r\n".encode("utf8"))

    @classmethod
    def set_count(cls, n: int) -> Result[bytes]:
        if isinstance(n, bool):
            return Result(RedisProtocolFormatError())
        elif not isinstance(n, int):
            return Result(RedisProtocolFormatError())
        if n < 0:
            return Result(RedisProtocolFormatError())
        return Result(f"*{n}\r\n".encode("utf8"))

    @classmethod
    def set_binary(cls, b: Union[bytes, str, int]):
        if isinstance(b, bool):
            return Result(RedisProtocolFormatError())
        if isinstance(b, str):
            arg_buffer = b.encode("utf8")
        elif isinstance(b, bytes):
            arg_buffer = b
        elif isinstance(b, int):
            arg_buffer = str(b).encode("utf8")
        else:
            return Result(RedisProtocolFormatError())
        length = len(arg_buffer)
        buffer = bytearray(f"${length}\r\n".encode("utf8"))
        buffer.extend(arg_buffer)
        buffer.extend(cls.CR_LF)
        return Result(buffer)

    @classmethod
    def get_count(cls, line: bytes) -> Result[int]:
        if isinstance(line, bytes):
            buffer = bytearray(line)
            if buffer.startswith(b"*") and buffer.endswith(b"\r\n"):
                value_binary = buffer[1:-2]
                if value_binary.isdigit():
                    return Result(int(value_binary))
                else:
                    Result(RedisProtocolFormatError())
        return Result(RedisProtocolFormatError())

    @classmethod
    def get_binary_size(cls, line: bytes) -> Result[int]:
        if isinstance(line, bytes):
            buffer = bytearray(line)
            if buffer.startswith(b"$") and buffer.endswith(b"\r\n"):
                value_binary = buffer[1:-2]
                if value_binary.isdigit():
                    return Result(int(value_binary))
                else:
                    Result(RedisProtocolFormatError())
        return Result(RedisProtocolFormatError())


__all__ = ["RedisProtocol", ]
