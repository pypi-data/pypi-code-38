import asyncio
import time
from copy import deepcopy
from typing import Optional


class Railgun(object):
    """


    """

    def __init__(
        self,
        semaphores_count: Optional[int] = 50,
        timeout: Optional[int] = 5,
        retry: Optional[bool] = False,
        loop: Optional[any] = asyncio.get_event_loop(),
    ):

        self.semaphores_count = semaphores_count
        self.timeout = timeout
        self.retry = retry
        self.semaphores = asyncio.Semaphore(value=semaphores_count)
        self.loop = loop

    # @classmethod
    def _set_semaphores(cls):
        cls.semaphore = asyncio.BoundedSemaphore(cls.semaphores_count)

    # @classmethod
    async def run_async_job(self, task, async_semaphore):
        async with async_semaphore:
            try:
                if asyncio.iscoroutine(task) or asyncio.iscoroutinefunction(task):
                    return await task
                else:
                    return task
            except Exception as e:
                print(e)
                return task

    # @classmethod
    def _setup_jobs(self, *args) -> list:
        start = time.time()
        _ = [
            asyncio.ensure_future(self.run_async_job(deepcopy(task), self.semaphores))
            for task in args
        ]
        print(time.time() - start)
        return _

    def _setup_repeat_jobs(self, func, args, repeat=0):
        start = time.time()
        _ = [
            asyncio.ensure_future(
                self.run_async_job(deepcopy(func(*args)), self.semaphores)
            )
            for task in range(0, repeat)
        ]
        print(time.time() - start)
        return _

    # @classmethod
    def run(self, tasks: list = []):
        jobs = self._setup_jobs(*tasks)
        return self.loop.run_until_complete(asyncio.gather(*jobs))

    # @classmethod
    async def run_async(self, tasks: list = []):
        jobs = self._setup_jobs(*tasks)
        return await asyncio.gather(*jobs)

    def repeat(self, func, args, repeat=0, run_async=False):
        jobs = self._setup_repeat_jobs(func, args, repeat)
        if run_async:
            asyncio.gather(*jobs)
        else:
            return self.loop.run_until_complete(asyncio.gather(*jobs))
