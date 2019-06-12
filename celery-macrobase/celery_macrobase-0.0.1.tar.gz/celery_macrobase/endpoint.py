import asyncio
from asyncio import AbstractEventLoop
from macrobase_driver.endpoint import Endpoint

from celery import Task
from celery.utils.log import get_task_logger

from structlog import get_logger
log = get_logger('CeleryEndpoint')


class CeleryEndpoint(Endpoint):

    def __call__(self, *args, **kwargs):
        return self.handle(*args, **kwargs)

    def handle(self, *args, **kwargs):
        log.info(f'Received {self.__name__}')
        return self.method(*args, **kwargs)

    def method(self, *args, **kwargs):
        pass


class HealthEndpoint(CeleryEndpoint):

    def method(self, *args, **kwargs) -> str:
        return 'Health'
