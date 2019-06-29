# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models


@receiver(post_save, sender=models.Task)
def send_message(sender, **kwargs):
    task = kwargs['instance']
    if task.is_active is False:
        return
    ids = task.receiver_ids
    if task.messages.count() == len(ids):
        return
    ctype = task.receiver_content_type
    for id in ids:
        obj = ctype.get_object_for_this_type(id)
        models.Message.objects.create(receiver=obj, task=task, )

