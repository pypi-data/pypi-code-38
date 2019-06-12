import asyncio
import tempfile

from tailf.aio import Tail
from .helpers import nose_async, write_through


@nose_async
async def test_readline():
    with tempfile.NamedTemporaryFile("w+b") as f:
        with Tail(f.name) as tail:
            coro = tail.readline()
            task = asyncio.create_task(coro)
            await asyncio.sleep(0.25)
            assert not task.done(), "No full line yet"
            write_through(f, b"alpha\nbeta\nga")
            await task
            assert task.result() == b"alpha\n", "'alpha' is read"
            assert await tail.readline() == b"beta\n", "'beta' is read"
            coro = tail.readline()
            task = asyncio.create_task(coro)
            await asyncio.sleep(0.25)
            assert not task.done(), "No full line yet"
            write_through(f, b"mma\ndel")
            await task
            assert task.result() == b"gamma\n", "'gamma' is read"
            coro = tail.readline()
            task = asyncio.create_task(coro)
            await asyncio.sleep(0.25)
            assert not task.done(), "No full line yet"
            assert not tail.is_truncated(), "Not truncated yet"

            # TODO truncations
            f.truncate(0)
            f.seek(0)
            await task
            assert task.result() == b"del", "'del' is consumed after truncation"
            assert tail.is_truncated(), "Truncated"
            write_through(f, b"epsilon\nzeta\net")
            assert await tail.readline() == b"", "Truncation not consumed yet"
            assert tail.get_truncated(), "Consuming truncation"
            assert await tail.readline() == b"epsilon\n", "'epsilon' is read"


@nose_async
async def test_concurrent():
    async def fill_file(f, strings):
        with f:
            for i, s in enumerate(strings):
                if i != 0:
                    await asyncio.sleep(0.1)
                write_through(f, s)

    with tempfile.NamedTemporaryFile("w+b") as f:
        data = [b"alpha\nbe", b"ta\ngamma\nde"]
        asyncio.get_event_loop().create_task(fill_file(f, data))
        with Tail(f.name) as tail:
            for line in b"alpha\n", b"beta\n", b"gamma\n":
                assert await tail.readline() == line
