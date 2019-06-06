#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

from celery import Celery
from werkzeug.utils import import_string


class Task():
    def __init__(self, name="task", broker="", backend="", config_name="celeryconfig"):
        self.name = name
        self.broker = broker
        self.backend = backend
        try:
            self.config = import_string(config_name)
            self.conf = self.config.celery_settings
        except:
            self.conf = {}

    def task(self):
        self.name = self.conf.get("name", self.name)
        self.broker = self.conf.get("broker", self.broker)
        self.backend = self.conf.get("backend", self.backend)
        task = Celery(self.name, broker=self.broker, backend=self.backend)
        return task

    def task_from_config(self):
        task = Celery(__name__)
        task.config_from_object(self.config)
        return task
