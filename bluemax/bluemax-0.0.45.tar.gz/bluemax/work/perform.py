from tornado.ioloop import IOLoop
from tornado import gen
import asyncio
import threading
import functools
import logging

LOGGER = logging.getLogger(__name__)


_context_ = threading.local()
_manager_ = None


class Context:
    """
        Used to capture broadcast
        that should only fly if
        the action completes.
    """

    def __init__(self, result, messages):
        self.result = result
        self.messages = messages

    def to_json(self):
        return {
            "_type_": self.__class__.__name__,
            "result": self.result,
            "messages": self.messages,
        }


def get_current_user():
    if hasattr(_context_, "user"):
        return _context_.user


def set_current_user(user):
    LOGGER.info("current user: %s", user)
    _context_.user = user


def broadcast(signal, message, filter_clients=None):
    _manager_.broadcast(signal, message, filter_clients)


def broadcast_on_success(signal, message, filter_clients=None):
    if hasattr(_context_, "broadcasts"):
        _context_.broadcasts.append((signal, message, filter_clients))
    else:
        broadcast(signal, message, filter_clients)


def register_object(obj: object) -> str:
    return _manager_.register_state(obj)


def deregister_object(name: str):
    return _manager_.deregister_state(name)


def put_work(actor, method, params):
    content = {"current_user": actor, "method": method, "params": params}
    _manager_.ioloop.add_callback(_manager_.put, content)


async def perform(actor, fn, args, kwargs):
    ioloop = IOLoop.current()
    if asyncio.iscoroutinefunction(fn):
        result = asyncio.ensure_future(fn(*args, **kwargs))
    elif gen.is_coroutine_function(fn):
        result = fn(*args, **kwargs)
    else:
        result = ioloop.run_in_executor(None, _perform_, actor, fn, args, kwargs)
    if asyncio.isfuture(result):
        result = await result
    return result


def _perform_(actor, fn, args, kwargs):
    _context_.broadcasts = []
    set_current_user(actor)

    try:
        LOGGER.info("%s %r %r", fn, args, kwargs)
        result = fn(*args, **kwargs)
        result = Context(result, _context_.broadcasts)
        return result
    except Exception as ex:
        LOGGER.exception(ex)
        raise ex
    finally:
        _context_.broadcasts = []
        _context_.user = None
