# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models

import logging

log = logging.getLogger('django')


@receiver(post_save, sender=models.Item)
def cal_request_amount(sender, **kwargs):
    # try:
    item = kwargs['instance']
    item.request.cal_amount()
    item.request.save()
    # except Exception, e:
    #     log.error(e)
