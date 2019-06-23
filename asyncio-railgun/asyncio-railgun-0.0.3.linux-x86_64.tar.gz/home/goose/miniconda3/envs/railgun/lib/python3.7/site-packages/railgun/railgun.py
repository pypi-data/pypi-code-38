import asyncio
from copy import deepcopy
from typing import Optional


class Railgun(object):
    """
    RailGun Class.
    RailGun is a library for using asyncio to execute concurrent tasks
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

    def _set_semaphores(cls):
        cls.semaphore = asyncio.BoundedSemaphore(cls.semaphores_count)

    async def run_async_job(self, task, async_semaphore):
        """
        :param task:
        :param async_semaphore:
        :return:
        """
        async with async_semaphore:
            try:
                if asyncio.iscoroutine(task) or asyncio.iscoroutinefunction(task):
                    return await task
                else:
                    return task
            except Exception as e:
                print(e)
                return task

    def _setup_jobs(self, *args) -> list:
        """
        :param args: general arguments passed to async method, func(*args, **kwargs)
        :return: list
        """
        return [
            asyncio.ensure_future(self.run_async_job(deepcopy(task), self.semaphores))
            for task in args
        ]

    def _setup_repeat_jobs(self, func, args, repeat=0) -> list:
        """
        :param func:
        :param args:
        :param repeat: a count of the number of repeats from 0 to repeat
        :return: list
        """
        return [
            asyncio.ensure_future(
                self.run_async_job(deepcopy(func(*args)), self.semaphores)
            )
            for _ in range(0, repeat)
        ]

    def run(self, tasks: list = []) -> list:
        """
        :param tasks: tasks passed to async method, func(*args, **kwargs)
        :return: list of results
        """
        jobs = self._setup_jobs(*tasks)
        return self.loop.run_until_complete(asyncio.gather(*jobs))

    async def run_async(self, tasks: list = []):
        """
        Run a list of tasks with an async return
        :param tasks:
        :return:
        """
        jobs = self._setup_jobs(*tasks)
        return await asyncio.gather(*jobs)

    def repeat(self, func, args, repeat: int = 0, run_async: bool = False) -> any:
        """
        Repeat same method and args multiple times. This method would be ideal for something
        like a loadtest, where multiples of the same calls are made to the same url
        :param func: any
        :param args: any
        :param repeat: int
        :param run_async: bool
        :return: any
        """
        jobs = self._setup_repeat_jobs(func, args, repeat)
        if run_async:
            return asyncio.gather(*jobs)
        else:
            return self.loop.run_until_complete(asyncio.gather(*jobs))
