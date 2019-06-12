from celery_macrobase.endpoint import CeleryEndpoint
from celery_macrobase.exceptions import RoutingException
from celery_macrobase.schedule import ScheduleConfiguration
from celery.schedules import crontab


class Method(object):

    def __init__(self, handler: CeleryEndpoint, name: str, schedule: ScheduleConfiguration = None):
        """Constructor of celery method.

        Arguments:
            handler (CeleryEndpoint): Celery endpoint class.
            name (str): Name of method.
            schedule (int or crontab): Schedule for periodic execute."""

        super(Method, self).__init__()

        if not isinstance(handler, CeleryEndpoint):
            raise RoutingException('Handler must be instance of CeleryEndpoint class')

        self._handler = handler
        self._name = name
        self._schedule = schedule
        self._signature = None

    def set_signature(self, signature):
        self._signature = signature

    @property
    def handler(self) -> CeleryEndpoint:
        return self._handler

    @property
    def name(self) -> str:
        return self._name

    @property
    def schedule(self) -> ScheduleConfiguration:
        return self._schedule

    @property
    def signature(self):
        return self._signature
