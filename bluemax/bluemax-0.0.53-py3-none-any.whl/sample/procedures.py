from bluemax import context
import time
import asyncio
from tornado import gen
from typing import Tuple


__all__ = ["add", "a_add", "t_add"]


def add(a: int = 2, b: int = 2, sleep_for: float = 0.1) -> Tuple[str, int]:
    """ returns a plus b syncronous."""
    result = a + b
    time.sleep(sleep_for)
    context.broadcast_on_success(
        "action", {"name": "add", "result": result, "user": context.get_current_user()}
    )
    return "add", result


async def a_add(a: int = 2, b: int = 3, sleep_for: float = 0.2) -> Tuple[str, int]:
    """ returns a plus b, async native."""
    result = a + b
    await asyncio.sleep(sleep_for)
    context.broadcast_on_success(
        "action",
        {"name": "a_add", "result": result, "user": context.get_current_user()},
    )
    return "a_add", result


@gen.coroutine
def t_add(a: int = 2, b: int = 4, sleep_for: float = 0.3) -> Tuple[str, int]:
    """ returns a plus b, async tornado."""
    result = a + b
    yield gen.sleep(sleep_for)
    context.broadcast_on_success(
        "action",
        {"name": "t_add", "result": result, "user": context.get_current_user()},
    )
    return "t_add", result
