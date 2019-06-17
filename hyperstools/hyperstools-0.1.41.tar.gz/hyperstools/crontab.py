# encoding: utf-8
import logging
import os
import time
import traceback

import apscheduler
import django
import redis
from apscheduler import events
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

logger = logging.getLogger("tools")


def error_handler(ev):
    if ev.exception:
        logger.error("%s error.", traceback.format_exc())
    else:
        logger.debug("%s miss", str(ev))


def record(func):
    def inner(*args, **kwargs):
        name = func.__name__
        module = func.__module__
        logger.info("start {}:{}".format(module, name))
        django.db.close_old_connections()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())
        logger.info("finish {}: {}".format(module, name))
        return result

    return inner


def _getJobID(func):
    module = func.__module__.split(".")[-1]
    return "{}{}".format(module, func.__name__)


class Scheduler(object):
    _records = []  # type: list

    def __init__(self, config=None):
        # _url = getattr(settings, "REDIS_URL", settings.REDIS_HOST)
        # _connection_kwargs = redis.ConnectionPool.from_url(_url).connection_kwargs
        self.scheduler = BackgroundScheduler()
        # self.scheduler.add_jobstore(
        #     "redis",
        #     jobs_key="crontab.jobs",
        #     run_times_key="crontab.run_times",
        #     **_connection_kwargs
        # )
        self.scheduler.add_listener(
            error_handler, events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED
        )
        self._records.extend(config or [])

    def addJob(self, **config):
        """增加定时器任务
        examle:
        直接调用
        Scheduler().addJob(method=func, seconds=30)

        :**config: 定时器配置
        :returns: self

        """
        method = config.pop("method")
        if "seconds" in config:
            config.setdefault("trigger", "interval")
        elif "hour" in config:
            config.setdefault("trigger", "cron")
        config["id"] = _getJobID(method)
        self.removeJob(config["id"])
        self.scheduler.add_job(method, **config)
        return self

    def removeJob(self, jobId):
        try:
            job = self.scheduler.get_job(jobId)
            if job:
                job.remove()
        except apscheduler.schedulers.base.JobLookupError:
            pass
        return self

    @classmethod
    def record(cls, **config):
        """记录定时器

        使用装饰器
        @Scheduler.record(seconds=30)
        def test():
            print('hello world')
        :**config: TODO
        :returns: TODO

        """

        def wrapper(method):
            config["method"] = method
            cls._records.append(config)
            return method

        return wrapper

    def start(self, config=None):
        self.scheduler.start()
        [self.addJob(**x) for x in self._records]
        self.scheduler.print_jobs()
        try:
            while True:
                time.sleep(1)
        except SystemExit:
            self.scheduler.shutdown()
