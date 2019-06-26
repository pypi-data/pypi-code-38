from asyncio import iscoroutinefunction
from functools import wraps
from time import time as time_
from typing import Callable, Generator, Optional, Union

from .graphite import Graphite

__all__ = [
    'count',
    'time',
]


class MetricMeta(type):
    def __new__(mcs, name, bases, namespace):
        graphite = namespace.pop('graphite', None)
        prefix = namespace.pop('prefix', None)
        klass = super().__new__(mcs, name, bases, namespace)

        if graphite:
            klass.graphite = graphite

        if prefix:
            klass.prefix = prefix

        return klass

    @property
    def graphite(cls) -> Graphite:
        return getattr(cls, '_graphite')

    @graphite.setter
    def graphite(cls, value: Graphite):
        if not isinstance(value, Graphite):
            raise TypeError("graphite must be Graphite, not {}", type(value).__name__)

        setattr(cls, '_graphite', value)

    @property
    def prefix(cls) -> str:
        return getattr(cls, '_prefix', '')

    @prefix.setter
    def prefix(cls, value: str):
        if not isinstance(value, str):
            raise TypeError("prefix must be str, not {}", type(value).__name__)

        setattr(cls, '_prefix', value)

    @prefix.deleter
    def prefix(cls):
        if hasattr(cls, '_prefix'):
            delattr(cls, '_prefix')


class Metric(metaclass=MetricMeta):
    def __init__(self, metric: str, *, graphite: Optional[Graphite] = None):
        if not isinstance(metric, str):
            raise TypeError("metric must be str, not {}", type(metric).__name__)

        if graphite and not isinstance(graphite, Graphite):
            raise TypeError("graphite must be Graphite, not {}", type(graphite).__name__)

        self._metric = metric
        self._graphite = graphite

    @property
    def metric(self) -> str:
        return '.'.join(x for x in (type(self).prefix, self._metric) if x)

    def send(self, value: int, timestamp: Optional[int] = None):
        graphite = self._graphite or type(self).graphite
        graphite.send(self.metric, value, timestamp)

    def count(self, func: Callable) -> Callable:
        @wraps(func)
        def deco(*args, **kwargs):
            self.send(1)
            return func(*args, **kwargs)
        return deco

    def time(self, func: Callable) -> Callable:
        if iscoroutinefunction(func):
            @wraps(func)
            async def deco(*args, **kwargs):
                start = time_()
                ret = await func(*args, **kwargs)
                self.send(int(round(time_() - start, 6) * 1000000))
                return ret
        else:
            @wraps(func)
            def deco(*args, **kwargs):
                start = time_()
                ret = func(*args, **kwargs)
                self.send(int(round(time_() - start, 6) * 1000000))
                return ret
        return deco


class MaxMetric(Metric):
    @property
    def metric(self) -> str:
        return super().metric + '.max'


class MinMetric(Metric):
    @property
    def metric(self) -> str:
        return super().metric + '.min'


class AvgMetric(Metric):
    @property
    def metric(self) -> str:
        return super().metric + '.avg'


class SumMetric(Metric):
    @property
    def metric(self) -> str:
        return super().metric + '.sum'


class CountMetric(Metric):
    @property
    def metric(self) -> str:
        return super().metric + '.count'


class TimeMetric(Metric):
    @property
    def metric(self) -> str:
        return super().metric + '.time'


class MsMetric(TimeMetric):
    @property
    def metric(self) -> str:
        return super().metric + '.ms'


class UsMetric(TimeMetric):
    @property
    def metric(self) -> str:
        return super().metric + '.us'


class NsMetric(TimeMetric):
    @property
    def metric(self) -> str:
        return super().metric + '.ns'


for time_class in TimeMetric.__subclasses__():
    for agg_class in [MaxMetric, MinMetric, AvgMetric, SumMetric]:
        name_ = '{}{}'.format(agg_class.__name__.replace('Metric', ''), time_class.__name__)
        globals()[name_] = type(name_, (agg_class, time_class), {})


def _recursive_subclasses(cls: type) -> Generator[type, None, None]:
    yield cls

    for klass in cls.__subclasses__():
        yield from _recursive_subclasses(klass)


__all__.extend(c.__name__ for c in _recursive_subclasses(Metric))


def count(func: Union[Callable, str], *, klass: MetricMeta = CountMetric) -> Callable[[Callable], Callable]:
    if isinstance(func, Callable):
        return klass('{}.{}'.format(func.__module__, func.__qualname__)).count(func)
    else:
        return klass(func).count


def time(func: Union[Callable, str], *, klass: MetricMeta = UsMetric) -> Callable[[Callable], Callable]:
    if isinstance(func, Callable):
        return klass('{}.{}'.format(func.__module__, func.__qualname__)).time(func)
    else:
        return klass(func).time
