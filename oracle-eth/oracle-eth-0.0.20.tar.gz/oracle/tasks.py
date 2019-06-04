#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description: 异步任务
#  

"""
from celery import Task
from celery import Celery
from celery.schedules import crontab
import logging
import configparser
from oracle.database.modles import Army
from oracle.database import status
from celery.utils.log import get_task_logger

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setFormatter(formatter)
log.addHandler(console)

logger = get_task_logger('myapp')
logger.setLevel(logging.DEBUG)

app = Celery('tasks')


config = configparser.RawConfigParser()
config.read('/etc/oracle.conf', encoding='utf8')
app.conf.update(
    result_backend='redis://127.0.0.1:6379/0',
    broker_url='redis://127.0.0.1:6379/2',
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        print('return: {}'.format(retval))
        log.info('ddddddd')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('return22: {}'.format(task_id))
        log.info('kkkkkkkk')


@app.task(name='tasks.test', debug=True, base=CallbackTask())
def test(arg):
    print(arg)
    log.info('qqqqqqqq')
    return arg

@app.task(name='tasks.test2', debug=True)
def test2(arg):
    print(arg)
    log.info('rrrrrrrrrrrrr')
    return 1

@app.task()
def add(arg1, arg2):
    return arg1+arg2


@app.task(name='tasks.confirmAttribute')
def confirm_attribute(cport, identity, name, value, id=0):
    """
    异步上链
    :param cport:
    :param identity:
    :param name:
    :param value:
    :param id: 数据库中表的id
    :return:
    """
    tf = cport.confirm_attribute(identity, name, value)
    if tf is True:
        Army.select(id=id).update(status == status.EVENT_ETHEREUM_SUBMIT_SUCESS)
    if tf is False:
        Army.select(id=id).update(status == status.EVENT_ETHEREUM_SUBMIT_FAILED)


if __name__ == '__main__':
    result = test.delay(30, 42)
    # 10秒之后运行
    test.apply_async((2, 2), countdown=10)