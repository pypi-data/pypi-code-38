# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models

import logging

log = logging.getLogger('django')

