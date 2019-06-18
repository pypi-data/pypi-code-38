# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task, chord
from django.contrib.contenttypes.models import ContentType

__author__ = 'denishuang'
import logging

log = logging.Logger("django")

@shared_task(ignore_result=True, time_limit=5, max_retries=3)
def add(x, y):
    import time
    print "add %s %s" % (x,y)
    time.sleep(10)
    print "add %s %s done" % (x,y)
    return x + y

@shared_task
def tsum(numbers):
    return sum(numbers)

@shared_task
def reduce_object(objects):
    return objects

@shared_task(default_retry_delay=1800, retry=False)
def get_object_data(params):
    from .modelutils import get_objects_accessor_data
    return list(get_objects_accessor_data(params.get("accessors"),params.get("content_type_id"),params.get("object_ids")))

def get_objects(qset, accessors):
    return get_object_data.delay(dict(content_type_id=ContentType.objects.get_for_model(qset.model).id,
             object_ids = list(qset.values_list("id",flat=True)),
             accessors = accessors))
