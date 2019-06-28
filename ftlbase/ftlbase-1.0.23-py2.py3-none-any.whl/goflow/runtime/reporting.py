#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from .models import WorkItem, ProcessInstance


class ActivityState:
    total = 0
    inactive = 0
    pending = 0
    blocked = 0
    suspended = 0
    fallout = 0
    complete = 0

    def __init__(self, activity):
        wis = WorkItem.objects.filter(activity=activity)
        self.total = wis.count()
        self.inactive = wis.filter(status=WorkItem.STATUS_INACTIVE).count()
        self.pending = wis.filter(status=WorkItem.STATUS_PENDING).count()
        self.blocked = wis.filter(status=WorkItem.STATUS_BLOCKED).count()
        self.suspended = wis.filter(status=WorkItem.STATUS_SUSPENDED).count()
        self.fallout = wis.filter(status=WorkItem.STATUS_FALLOUT).count()
        self.complete = wis.filter(status=WorkItem.STATUS_CONCLUDED).count()


class ProcessState:
    total = 0
    initiated = 0
    pending = 0
    complete = 0
    suspended = 0

    def __init__(self, process):
        insts = ProcessInstance.objects.filter(process=process)
        self.total = insts.count()
        self.initiated = insts.filter(status=ProcessInstance.STATUS_INACTIVE).count()
        self.pending = insts.filter(status=ProcessInstance.STATUS_PENDING).count()
        self.complete = insts.filter(status=ProcessInstance.STATUS_CONCLUDED).count()
        self.suspended = insts.filter(status=ProcessInstance.STATUS_SUSPENDED).count()


class ActivityStats:
    number = 0
    time_min = None
    time_max = None
    time_mean = None

    def __init__(self, activity, user=None, year=None, month=None, day=None, datetime_interval=None):
        pass
