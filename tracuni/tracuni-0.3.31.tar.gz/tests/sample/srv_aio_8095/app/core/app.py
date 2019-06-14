import asyncio
import signal
import logging

from aiohttp.web_runner import _raise_graceful_exit

from app.core.component import Component
from app.core.helper import GracefulExit, PrepareError


class BaseApp(object):
    def __init__(self, config=None, loop=None):
        super(BaseApp, self).__init__()
        self.config = config
        self.loop = loop or asyncio.get_event_loop()
        self._components: dict = {}
        self._stop_deps: dict = {}
        self._stopped: list = []
        self._tracer: az.Tracer = None

    def attach_component(
            self,
            name: str,
            comp: Component,
            stop_after: list = None
    ):
        if not isinstance(comp, Component):
            raise UserWarning()
        if name in self._components:
            raise UserWarning()
        comp.loop = self.loop
        comp.app = self
        self._components[name] = comp
        self._stop_deps[name] = stop_after

    def __getattr__(self, item):
        if item not in self._components:
            raise AttributeError
        return self._components[item]

    @staticmethod
    def log_err(err):
        if isinstance(err, BaseException):
            logging.exception(err)
        else:
            logging.error(err)

    @staticmethod
    def log_warn(warn):
        logging.warning(warn)

    @staticmethod
    def log_info(info):
        logging.info(info)

    @staticmethod
    def log_debug(debug):
        logging.debug(debug)

    def setup_logging(
            self,
            tracer_driver,
            tracer_svc_name,
            tracer_url,
            statsd_addr,
            statsd_prefix,
            sample_rate=1.0,
            send_interval=3
    ):
        self._tracer = None

    async def _shutdown_tracer(self):
        if self._tracer:
            self.log_info("Shutting down tracer")
            await self._tracer.close()

    @property
    def tracer(self):
        return self._tracer

    def run(self):
        try:
            self.loop.run_until_complete(self.run_prepare())
        except PrepareError as e:
            self.log_err(e)
            return 1
        except KeyboardInterrupt:  # pragma: no cover
            return 1
        self.run_loop()
        self.loop.run_until_complete(self.run_shutdown())
        print("Bye")
        if hasattr(self.loop, 'shutdown_asyncgens'):
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()
        return 0

    async def run_prepare(self):
        self.log_info('Prepare for start')
        await asyncio.gather(*[comp.prepare() for comp in self._components.values()], loop=self.loop)

        self.log_info('Starting...')
        await asyncio.gather(*[comp.start() for comp in self._components.values()], loop=self.loop)
        self.log_info('Running...')

    def run_loop(self):
        try:
            self.loop.add_signal_handler(signal.SIGINT, _raise_graceful_exit)
            self.loop.add_signal_handler(signal.SIGTERM, _raise_graceful_exit)
        except NotImplementedError:  # pragma: no cover
            # add_signal_handler is not implemented on Windows
            pass
        try:
            self.loop.run_forever()
        except GracefulExit:  # pragma: no cover
            pass

    async def run_shutdown(self):
        self.log_info('Shutting down...')
        for comp_name in self._components:
            await self._stop_comp(comp_name)
        await self._shutdown_tracer()

    async def _stop_comp(self, name):
        if name in self._stopped:
            return
        if name in self._stop_deps and self._stop_deps[name]:
            for dep_name in self._stop_deps[name]:
                await self._stop_comp(dep_name)
        await self._components[name].stop()
        self._stopped.append(name)
