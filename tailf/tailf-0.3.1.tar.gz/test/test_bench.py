import asyncio
import importlib.resources

from tailf.aio import Tail
from .helpers import nose_async
from .bench import *


async def bench(filename, buffer_size=4096):
    global amount
    amount = 0
    with importlib.resources.path("test", filename) as path:
        with Tail(path, buffer_size=buffer_size) as tail:
            while True:
                try:
                    await asyncio.wait_for(tail.readline(), timeout=0.1)
                    amount += 1
                except asyncio.TimeoutError:
                    break


@nose_async
async def test_bench_readline_shortlines():
    bench_start("bench")
    try:
        await asyncio.wait_for(bench("shortlines.txt", 4096), timeout=2)
    finally:
        bench_end("bench")
        print("[lines read = %i]" % amount)
        bench_dump()


@nose_async
async def test_bench_readline_longlines():
    bench_start("bench")
    try:
        await asyncio.wait_for(bench("longlines.txt", 8), timeout=1)
    finally:
        bench_end("bench")
        print("[lines read = %i]" % amount)
        bench_dump()
