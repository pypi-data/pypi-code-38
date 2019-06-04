# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task, chord

__author__ = 'denishuang'
import logging

log = logging.Logger("django")

