from celery.schedules import crontab


class ScheduleConfiguration(object):

    def __init__(self, schedule, args: list = None, kwargs: dict = None, name: str = None, expires=None, retry: bool = True):
        self._schedule = schedule
        self._name = name
        self._args = args
        self._kwargs = kwargs
        self._expires = expires
        self._retry = retry

    @property
    def schedule(self):
        return self._schedule

    @property
    def name(self) -> str:
        return self._name

    @property
    def args(self) -> list:
        return self._args

    @property
    def kwargs(self) -> dict:
        return self._kwargs

    def entry(self, sig: str) -> dict:
        return {
            'schedule': self.schedule,
            'task': sig,
            'args': self.args,
            'kwargs': self.kwargs,
            'options': {
                'expires': self._expires,
                'retry': self._retry,
            },
        }

    @property
    def key(self):
        return self.name
