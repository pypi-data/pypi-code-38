# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_szuprefix_saas.saas.models import Party
from django.contrib.auth.models import User
from django_szuprefix.utils import modelutils


class Task(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "任务"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="message_tasks",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="message_tasks",
                             on_delete=models.PROTECT)
    receiver_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    receiver_ids = modelutils.JSONField("所有接收者ID", blank=True, null=True)
    type = models.CharField("消息类型", max_length=32, default='sys')
    title = models.CharField("标题", max_length=255, blank=True)
    content = models.TextField("内容", blank=True, null=True)
    link = models.CharField("连接", max_length=255, blank=True, null=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    is_active = models.BooleanField("有效", default=True)

    def __unicode__(self):
        return self.title


class Message(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "消息"
        ordering = ('-create_time',)
        unique_together = ('task', 'receiver_content_type', 'receiver_object_id')

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="messages",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="messages",
                             on_delete=models.PROTECT)
    receiver_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    receiver_object_id = models.PositiveIntegerField()
    receiver = GenericForeignKey('receiver_content_type', 'receiver_object_id')
    task = models.ForeignKey(Task, verbose_name=Task._meta.verbose_name, related_name="messages",
                             on_delete=models.PROTECT)
    is_read = models.BooleanField("是否已读", default=False, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    read_time = models.DateTimeField("阅读时间", null=True, blank=True)

    def save(self, **kwargs):
        self.receiver_content_type = self.task.receiver_content_type
        self.party = self.task.party
        self.user = self.receiver.as_user()
        return super(Message, self).save(**kwargs)
