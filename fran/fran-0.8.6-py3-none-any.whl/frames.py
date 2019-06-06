import contextlib
from collections import deque
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from functools import lru_cache
from queue import Queue
from threading import Lock
from typing import Deque
import logging

import imageio
import numpy as np
from skimage.exposure import rescale_intensity

from fran.constants import DEFAULT_THREADS, DEFAULT_CACHE_SIZE

logger = logging.getLogger(__name__)


class FrameAccessor:
    count = 0

    def __init__(self, fpath, **kwargs):
        self.logger = logger.getChild(type(self)._accessor_name())
        self.lock = Lock()

        self.fpath = fpath
        with self.lock:
            self.reader = imageio.get_reader(fpath, mode="I", **kwargs)
            self.len = self.reader.get_length()
        self.logger.info("Detected %s frames", self.len)
        first = self[0]
        self.frame_shape = first.shape
        self.logger.info("Detected frames of shape %s", self.frame_shape)
        self.dtype = first.dtype
        self.logger.info(
            "Detected frames of dtype %s (non-uint8 may be slower)", self.dtype
        )

    @classmethod
    def _accessor_name(cls):
        name = f"{cls.__name__}<{cls.count}>"
        cls.count += 1
        return name

    def close(self):
        return self.reader.close()

    def __len__(self):
        return self.len

    def __getitem__(self, item):
        with self.lock:
            return self.reader.get_data(item)

    def __iter__(self):
        for idx in range(len(self)):
            yield self[idx]


class Spinner:
    def __init__(self, initial_idx, options):
        self.idx = initial_idx
        self.options = options

        self.max_idx = len(options) - 1

    def increase(self, steps=1):
        self.idx = min(self.max_idx, self.idx + steps)
        return self()

    def decrease(self, steps=1):
        self.idx = max(0, self.idx - steps)
        return self()

    def __call__(self, idx: int = None) -> float:
        if idx is not None:
            if idx < 0:
                self.idx = 0
            elif idx >= len(self.options):
                self.idx = len(self.options) - 1
            else:
                self.idx = idx

        return self.options[self.idx]


class ImageConverter:
    n_steps = 101

    def __init__(self, in_dtype, out_dtype=np.dtype("uint8")):
        if in_dtype not in (np.dtype("uint8"), np.dtype("uint16")):
            raise ValueError("Only uint8 and uint16 dtypes are supported")

        self.in_dtype = np.dtype(in_dtype)
        dtype_info = np.iinfo(self.in_dtype.name)

        options = np.linspace(
            dtype_info.min, dtype_info.max, self.n_steps, dtype=self.in_dtype
        )

        self.contrast_lower = Spinner(0, options)
        self.contrast_upper = Spinner(len(options) - 1, options)

        self.out_dtype = np.dtype(out_dtype)

    def __call__(self, arr):
        if arr.dtype != self.in_dtype:
            raise ValueError(
                f"Given array ({arr.dtype}) is not of the correct dtype ({self.in_dtype})"
            )
        return rescale_intensity(
            arr, (self.contrast_lower(), self.contrast_upper()), self.out_dtype.name
        ).astype(self.out_dtype)


class FrameSpooler:
    def __init__(
        self,
        fpath,
        cache_size=DEFAULT_CACHE_SIZE,
        max_workers=DEFAULT_THREADS,
        **kwargs,
    ):
        self.logger = logger.getChild(type(self).__name__)
        self.fpath = fpath
        self.logger.info("Opening file %s", fpath)

        frames = FrameAccessor(self.fpath, **kwargs)
        self.frame_dtype = frames.dtype
        self.frame_shape = frames.frame_shape
        self.frame_count = len(frames)

        self.accessor_pool = Queue()
        self.accessor_pool.put(frames)
        for _ in range(max_workers - 1):
            self.accessor_pool.put(FrameAccessor(self.fpath, **kwargs))

        self.current_idx = 0

        self.pyg_size = self.frame_shape[1::-1]

        self.half_cache = cache_size // 2

        self.idx_in_cache = 0
        cache_size = min(cache_size, len(frames))

        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.cache: Deque[Future] = deque(
            [self.fetch_frame(idx) for idx in range(cache_size)], cache_size
        )

    @contextlib.contextmanager
    def frames(self):
        accessor = self.accessor_pool.get(block=True)
        yield accessor
        self.accessor_pool.put(accessor)
        self.accessor_pool.task_done()

    def cache_range(self):
        """in frame number"""
        start = max(self.current_idx - self.idx_in_cache, 0)
        stop = start + len(self.cache)
        return start, stop

    def frame_idx_to_cache_idx(self, frame_idx):
        return frame_idx - self.cache_range()[0]

    def cache_idx_to_frame_idx(self, cache_idx):
        return cache_idx + self.cache_range()[0]

    @property
    def leftmost(self):
        return self.cache[0]

    @property
    def rightmost(self):
        return self.cache[-1]

    @property
    def current(self):
        return self.cache[self.idx_in_cache]

    def prev(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            if self.idx_in_cache > self.half_cache:
                self.idx_in_cache -= 1
            else:
                self.rightmost.cancel()
                idx = self.current_idx - self.idx_in_cache
                self.cache.appendleft(self.fetch_frame(idx))
        return self.current

    def next(self):
        if self.current_idx < self.frame_count - 2:
            self.current_idx += 1
            if self.idx_in_cache < self.half_cache:
                self.idx_in_cache += 1
            else:
                self.leftmost.cancel()
                idx = self.current_idx + self.idx_in_cache
                self.cache.append(self.fetch_frame(idx))
        return self.current

    def step(self, step=1):
        if not step:
            return self.current
        method = self.prev if step < 0 else self.next
        for _ in range(abs(step)):
            result = method()
        return result

    def fetch_frame(self, idx):
        if 0 <= idx < self.frame_count:
            f = self.executor.submit(
                self._fetch_frame,
                idx
                # self._fetch_frame, idx, self.contrast_lower, self.contrast_upper
            )
        else:
            f = Future()
            f.set_result(None)
        return f

    @lru_cache(maxsize=100)
    def _fetch_frame(self, idx):
        # todo: resize?
        with self.frames() as frames:
            arr = frames[idx]

        return arr

    def close(self):
        for f in self.cache:
            f.cancel()
        self.executor.shutdown()
        self.accessor_pool.put(None)
        while True:
            frames = self.accessor_pool.get(timeout=1)
            self.accessor_pool.task_done()
            if frames is None:
                break
            frames.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
