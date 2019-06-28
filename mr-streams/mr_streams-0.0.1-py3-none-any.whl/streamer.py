from functools import partial, reduce
from  mr_streams.exceptions import IllegalStreamOperationException
from itertools import islice
from time import time


class EOL():
    pass

class Streamer:
    def __init__(self, _iter):
        self.structure = iter(_iter)
        self.eol = EOL()

    def _build(self, expression):
        self.structure = expression
        self.structure = iter(self.structure)
        return self

    def __iter__(self):
        return self

    def __next__(self):
        _obj = next(self.structure, self.eol)
        if _obj is not self.eol:
            return _obj
        else:
            raise StopIteration
    def _flatten(self, _generator,_function):
        yield from (y for x in _generator for y in _function(x))


    def _chunk(self, iterable, n = 1):
        values_remaining = True
        while values_remaining == True:
            temp_cache = []
            for _ in range(n):
                next_val = next(iterable, self.eol)
                if next_val is not self.eol:
                    temp_cache.append(next_val)
                else:
                    values_remaining = False
                    break
            yield temp_cache

    def chunk(self,n):
        chunk_n = partial(self._chunk, n = n)
        return self._build(chunk_n(self.structure))

    def map(self, _function, *args, **kwargs):
        _curried_function = partial(_function, *args, **kwargs)
        return self._build(map(_curried_function, self.structure))

    def flatmap(self, _function, *args, **kwargs):
        _curried_function = partial(_function, *args, **kwargs)
        return self._build(self._flatten(self.structure, _curried_function))

    def reduce(self, _function, initializer = None, *args, **kwargs):
        struct = iter(self.structure)
        a = next(struct, self.eol)
        if a is self.eol:
            raise IllegalStreamOperationException("Tying to reduce reducing a stream with no values")

        b = next(struct, self.eol) if initializer is None else initializer
        if b is self.eol and initializer is None:
            return a

        _initial = _function(a,b)
        _curried_function = partial(_function,  *args, **kwargs)
        return reduce(_curried_function, struct, _initial)

    def filter(self, _function, *args, **kwargs):
        _curried_function = partial(_function, *args, **kwargs)
        return self._build(filter(_curried_function, self.structure))

    def _skip(self, iterable, n):
        counter = 0
        for x in iterable:
            if counter % n == 0:
                yield x
            counter = counter + 1

    def skip(self, n):
        return self._build(self._skip(self.structure, n = n))

    def _identity(self):
        return self

    def _window(self, seq, n=2, *args, **kwargs):
        "Returns a sliding window (of width n) over data from the iterable"
        "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result

    def window(self,n = 2,stride = 1):
        ph =  self._build(self._window(iter(self.structure), n = n + stride))
        return ph

    def tap(self, _function, *args, **kwargs):
        def _tap(function, iterable):
            for x in iterable:
                function(x)
                yield x
        _curried_function = partial(_function, *args, **kwargs)
        return self._build(_tap(_curried_function, self.structure))

    def _take(self, n, iterable):
        for i, val in enumerate(iterable):
            if i == n:
                break
            else:
                yield val

    def take(self, n):
        return self._build(self._take(n, self.structure))


    def _drop(self, n, iterable):
        for i, val in enumerate(iterable):
            if i >= n :
                yield val

    def drop(self, n):
        return self._build(self._drop(n, self.structure))

    def drain(self):
        for _ in self.structure:
            continue

    def rate_limited(self, t = 0):
        """ Drains a stream and only emits an object after N seconds has elapsed.

        Useful in real-time streams where data loss is tolerable. For example frames
        from a webcam. Processing can often happen slower than the acquisition of a frame.
        Instead of backing up the queue with unprocessed frames it makes more sense to sample
        every K seconds(where K > t)  and drop the rest of the frames.

        Args:
            t: time to wait before an emitted item is re-sampled.

        Returns:
            Streamer

        """
        def x(iterable):
            t1 = time()
            for v in iterable:
                t2 = time()
                if t2 - t1 > t:
                    t1 = t2
                    yield v
        return self._build(x(self.structure))


if __name__ == "__main__":
    add = lambda a,b: a + b
    Streamer(range(10000)).map(add, 1).chunk(5).emission_rate_limiter(5)