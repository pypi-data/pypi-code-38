"""This service will execute sub-services according to the HttpServerServiceConfig.SERVICES_NAMES
    Services names separated by semicolon - the augs are global to all of those services"""

from threading import RLock
import six
import os

from rook.config import HttpServerServiceConfig
from .flask_tracer import FlaskTracer

from rook.exceptions import RookNoHttpServiceRegistered


class HttpServerService(object):
    NAME = "HttpService"

    def __init__(self):
        self._lock = RLock()
        self._augs = {}
        self._services = {}

        services_names = os.environ.get('ROOKOUT_HTTP_SERVICES', HttpServerServiceConfig.SERVICES_NAMES).split(';')

        if FlaskTracer.NAME in services_names:
            self._services[FlaskTracer.NAME] = FlaskTracer(self.execute_augs)

    def add_logging_aug(self, aug):
        with self._lock:
            if len(self._services) == 0:
                raise RookNoHttpServiceRegistered()

            self._augs[aug.aug_id] = aug
            aug.set_active()

    def remove_aug(self, aug_id):
        with self._lock:
            try:
                aug = self._augs[aug_id]
            except KeyError:
                return

            del self._augs[aug_id]
            aug.set_removed()

    def clear_augs(self):
        with self._lock:
            aug_ids = list(self._augs.keys())

            for aug_id in aug_ids:
                self.remove_aug(aug_id)

    def close(self):
        self.clear_augs()

    def execute_augs(self, extracted):
        with self._lock:
            for aug in six.itervalues(self._augs):
                aug.execute(dict(), extracted)
