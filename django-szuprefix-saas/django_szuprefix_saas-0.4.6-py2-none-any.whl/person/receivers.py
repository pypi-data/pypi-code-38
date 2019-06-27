# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from . import helper
from ..saas.models import Worker
import logging

log = logging.getLogger("django")

@receiver(post_save, sender=Worker)
def init_person(sender, **kwargs):
    try:
        worker = kwargs['instance']
        helper.init_person(worker)
    except Exception, e:
        import traceback
        log.error("init_person error: %s" % traceback.format_exc())
