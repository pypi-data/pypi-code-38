from typing import Union, Tuple, Dict, Mapping, Any, SupportsFloat, Iterable, Sequence

from functools import total_ordering

from math import isclose

from time_me.runner import Runner, runner as to_runner
from time_me.timer import Timer

ArgSet_Raw = Tuple[Tuple, Dict]
ArgSet = Union[ArgSet_Raw, Tuple, Dict]


def parse_argset(a):
    if isinstance(a, tuple) and len(a) == 2 and isinstance(a[0], tuple) and isinstance(a[1], dict):
        return a
    elif isinstance(a, Iterable):
        return a, {}
    elif isinstance(a, Mapping):
        return (), a
    raise TypeError(a)


class Coach:
    def __init__(self, sanity_argsets: Mapping[ArgSet, Any] = None):
        self._sanity_argsets = sanity_argsets or {}

        self._measured = set()

    def call(self, runner: Runner, argset: ArgSet, timer: Timer):
        a, k = parse_argset(argset)
        with timer.resume():
            runner(*a, **k)

    def sane(self, expected_value: Any, actual: Any):
        if isinstance(actual, (float, int)):
            return isclose(actual, expected_value)
        return expected_value == actual

    def iter_argsets(self, timer) -> Iterable[ArgSet_Raw]:
        yield ((), {})

    def __call__(self, runner):
        if not isinstance(runner, Runner):
            runner = to_runner(runner)

        for sa, expected in self._sanity_argsets.items():
            a, k = parse_argset(sa)
            actual = runner(*a, **k)
            if not self.sane(expected, actual):
                raise ValueError(f'{expected} vs {actual}')

        timer = Timer()
        n = 0

        for argset in self.iter_argsets(timer):
            a, k = argset
            with timer.resume():
                runner(*a, **k)
            n += 1

        ret = self.Result(runner, timer, n)
        runner.assign_result(self, ret)
        self._measured.add(ret)
        return ret

    def measure(self, obj):
        self(obj)
        return obj

    def compare(self, *objs):
        if not objs:
            objs = self._measured
        results = []
        for o in objs:
            if isinstance(o, __class__.Result):
                results.append(o)
            else:
                res_dict = getattr(o, '__results__', None)
                if isinstance(res_dict, Mapping) and self in res_dict:
                    results.append(res_dict[self])
                else:
                    results.append(self(o))

        return self.ResultComparison(sorted(results))

    @total_ordering
    class Result:
        def __init__(self, runner: Runner, total_time: SupportsFloat, n: int):
            self.runner = runner
            self.total_time = float(total_time)
            self.n = n

        def __float__(self):
            return self.total_time / self.n

        def __lt__(self, other):
            return float(self) < float(other)

        def __str__(self):
            if self.n > 1:
                return f'{self.runner}: {self.total_time:.2g}/{self.n:,} = {float(self):.2g} seconds'
            return f'{self.runner}: {self.total_time:.2g} seconds'

        def __truediv__(self, other):
            return float(self) / float(other)

    class ResultComparison(Sequence[Result]):
        def __init__(self, source: Sequence):
            self.source = source

        def __iter__(self):
            yield from self.source

        def __getitem__(self, item):
            return self.source[item]

        def __len__(self):
            return len(self.source)

        def __str__(self):
            return '\n'.join(str(r) for r in self)

        def bar(self, autoshow=True):
            import matplotlib.pyplot as plt

            plt.bar(
                range(len(self)), [float(r) for r in self], tick_label=[r.runner.__name__ for r in self]
            )
            plt.ylabel('seconds / run')

            best = self[0]
            for i, not_best in enumerate(self[1:], 1):
                plt.text(i, not_best / 2, f'{not_best / best:.1f}x {best.runner.__name__}', ha='center', wrap=True)

            if autoshow:
                plt.show()


class TimeLimitCoach(Coach):
    def __init__(self, time_limit, **kwargs):
        super().__init__(**kwargs)
        self.time_limit = time_limit

    def iter_argsets(self, timer) -> Iterable[ArgSet_Raw]:
        while timer < self.time_limit:
            for argset in super().iter_argsets(timer):
                yield argset


class ArgCoach(Coach):
    def __init__(self, n: int = 1, argsets: Iterable[ArgSet] = ((),), **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.argsets = argsets

    def iter_argsets(self, timer) -> Iterable[ArgSet_Raw]:
        for _ in range(self.n):
            for argset in self.argsets:
                yield parse_argset(argset)
