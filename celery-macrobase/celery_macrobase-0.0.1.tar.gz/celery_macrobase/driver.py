import asyncio
from typing import List, Tuple, ClassVar, Dict
from enum import Enum
from functools import partial
import logging.config

from macrobase_driver.driver import MacrobaseDriver
from macrobase_driver.hook import HookHandler
from macrobase_driver.logging import get_logging_config, LogLevel

from celery_macrobase import endpoint
from celery_macrobase.method import Method
from celery_macrobase.config import CeleryDriverConfig
from celery_macrobase.hook import CeleryHookNames

from celery import Celery, signals

import uvloop

from structlog import get_logger
log = get_logger('CeleryDriver')


class CeleryDriver(MacrobaseDriver):

    class CeleryDriverType(Enum):
        worker = 0
        beat = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.name is None:
            self.name = 'CeleryDriver'

        self.config = CeleryDriverConfig()
        self._hooks: Dict[CeleryHookNames, List[HookHandler]] = {}
        self._methods: List[Method] = []

    def update_config(self, config: CeleryDriverConfig):
        """
        Add celery driver config
        """
        self.config.update(config)

    def add_hook(self, name: CeleryHookNames, handler):
        if name not in self._hooks:
            self._hooks[name] = []

        self._hooks[name].append(HookHandler(self, handler))

    def add_method(self, method: Method):
        self._methods.append(method)

    def add_methods(self, methods: List[Method]):
        self._methods.extend(methods)

    def _get_name_task(self, name: str) -> str:
        return f'{self.config.BLUEPRINT}.{name}'

    def _apply_method(self, method: Method):
        name = self._get_name_task(method.name)
        task = self._app.task(name=name, bind=True)(method.handler)

    def _setup_logging(self, *args, **kwargs):
        from logging.config import dictConfig
        dictConfig(get_logging_config(self.config))

    def _prepare(self):
        uvloop.install()

        self._app = Celery(self.config.BLUEPRINT)
        self._app.conf.update(self.config.get_worker_config())

        # Setup celery signals
        signals.setup_logging.connect(self._setup_logging)

        if self.config.HEALTH_ENDPOINT:
            self._apply_method(Method(endpoint.HealthEndpoint(self.context, self.config), 'health'))

        [self._apply_method(method) for method in self._methods]
        # self._app.on_after_finalize.connect(self._post_applying_method)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

        self._prepare()

        self.loop.run_until_complete(self._call_hooks(CeleryHookNames.before_worker_start))

        try:
            self._app.worker_main()
        except Exception as e:
            print(e)
        finally:
            self.loop.run_until_complete(self._call_hooks(CeleryHookNames.after_worker_stop))


class CeleryDriverBeat(CeleryDriver):

    def _setup_logging(self, *args, **kwargs):
        from logging.config import dictConfig
        dictConfig(get_logging_config(self.config))

    def _prepare(self):
        uvloop.install()

        self._app = Celery(self.config.BEAT_BLUEPRINT)
        self._app.conf.update(self.config.get_beat_config())

        # Setup celery signals
        signals.setup_logging.connect(self._setup_logging)

        for method in self._methods:
            if method.schedule is None:
                continue

            self._app._add_periodic_task(method.name, method.schedule.entry(self._get_name_task(method.name)))

    def run(self, *args, **kwargs):
        self._prepare()

        self.loop.run_until_complete(self._call_hooks(CeleryHookNames.before_beat_start))

        try:
            self._app.Beat().run()
        except Exception as e:
            print(e)
        finally:
            self.loop.run_until_complete(self._call_hooks(CeleryHookNames.after_beat_start))
