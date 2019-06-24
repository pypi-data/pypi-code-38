# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task, chord
from . import helper
from django_szuprefix_saas.saas.models import Worker

__author__ = 'denishuang'
import logging

log = logging.Logger("celery")


@shared_task(ignore_result=True)
def init_student(worker_id):
    try:
        student, created = helper.init_student(Worker.objects.get(id=worker_id))
        log.info("init_student:%s,%s", student, created)
    except:
        import traceback
        log.warning("init_student exception:%s", traceback.format_exc())
