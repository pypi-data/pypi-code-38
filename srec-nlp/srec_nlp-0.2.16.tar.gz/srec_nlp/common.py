import functools
import inspect
import itertools
from io import IOBase
from pathlib import Path
from typing import Callable, Union

import attr
import trio
from requests import HTTPError

from .exc import RateError


@attr.s(frozen=True)
class Score:
    positive: float = attr.ib(factory=float)
    negative: float = attr.ib(factory=float)
    classification: str = ""

    def __attrs_post_init__(self):
        classes = ("positive", "negative")
        filt = [getattr(self, c) for c in classes]
        mx = max(filt)
        object.__setattr__(
            self,
            "classification",
            next(itertools.compress(classes, map(mx.__eq__, filt))),
        )

    @classmethod
    def fromsingle(cls, value):
        """
        :param value: single value score
        :return:
        """
        negative = 1 - value
        positive = value

        return Score(positive=positive, negative=negative)

    @classmethod
    def fromtriplet(cls, positive, neutral, negative):
        """
        :param positive:  Confidence
        :param neutral: Confidence
        :param negative: Confidence
        :return: Score
        """
        positive += neutral / 2
        negative += neutral / 2
        return Score(positive=positive, negative=negative)

    def __getitem__(self):
        return self.positive, self.negative, self.classification

@attr.s(frozen=True)
class Query:
    content: str = attr.ib(factory=str)
    score: Score = attr.ib(default=Score())

    def __getitem__(self):
        return self.content, self.score

def _ensure_utf(
        func: Callable[[str], Query]
) -> Callable[[Union[IOBase, str, Path, bytes]], Query]:
    """

    :param func: Query function to wrap
    :return: Returns a wrapper for the provided function.
    """

    @functools.singledispatch
    def _text_is_utf(text: str):
        return text.replace("\n", "")

    @_text_is_utf.register(bytes)
    def _(text: bytes):
        return text.decode("utf-8").replace("\n", "")

    @_text_is_utf.register(Path)
    def _(path: Path):
        text = path.read_text("utf-8").replace("\n", "")
        return text

    @_text_is_utf.register(IOBase)
    def _(fp: IOBase):
        text = "".join(map(str, fp.readlines())).replace("\n", "")
        return text

    if not inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        def wrapper(self, text):
            text = _text_is_utf(text).replace("\n", "")
            return func(self, text)
    else:
        @functools.wraps(func)
        async def wrapper(self, text):
            text = _text_is_utf(text).replace('')
            return await func(self, text)

    return wrapper


def _parallel(func):
    """
    Vectorizies a function.
    If the function is synchronous, it uses trio.run to run the queries,
    if the function is async, it awaits.
    :param func:
    :return:
    """

    async def listd(self, query):
        def catch_httperr(exc):
            if isinstance(exc, (HTTPError, RateError)):
                raise exc
            else:
                print(exc)
                raise trio.MultiError([exc])

        async def list_internal(s, q, callback):
            if inspect.iscoroutinefunction(func):
                callback(await func(s, q))
            else:
                callback(func(s, q))

        results = []
        with trio.MultiError.catch(catch_httperr):
            async with trio.open_nursery() as nursery:
                for q in query:
                    nursery.start_soon(list_internal, self, q, results.append)

        return results

    @functools.wraps(func)
    def internal(self, query):
        if isinstance(query, list):
            return trio.run(listd, self, query)
        return func(self, query)

    return internal


def _parallel_async(func):
    async def asynchronous_call(self, query, pipe):
        result = await func(self, query)
        await pipe.send(result)
        await pipe.aclose()

    async def wrapper(self, query_in: trio._channel.MemoryReceiveChannel, qout: trio._channel.MemorySendChannel):
        async with trio.open_nursery() as nrs:
            async with qout:
                async for q in query_in:
                    nrs.start_soon(asynchronous_call, self, q, qout.clone())

    return wrapper
