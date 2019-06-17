# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

import uuid
from django_enumfield import enum

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.filefields.models import FileField


User = get_user_model()


# Create your models here.
class TicketPriority(enum.Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

    labels = {
        LOW: _('Low'),
        MEDIUM: _('Medium'),
        HIGH: _('High')
    }


class TicketStatus(enum.Enum):
    OPEN = 0
    WAITING_FOR_REVIEW = 1
    REVIEWED = 2
    CLOSE = 3

    labels = {
        OPEN: _('Open'),
        WAITING_FOR_REVIEW: _('Waiting for review'),
        REVIEWED: _('Reviewed'),
        CLOSE: _('Close')
    }


class TicketDepartment(enum.Enum):
    TECHNICAL = 0
    SALE = 1

    labels = {
        TECHNICAL: _('Technical'),
        SALE: _('Sale'),
    }


class TicketManager(BaseModelManager):

    def get_queryset(self):
        return super(TicketManager, self).get_queryset()

    def active(self):
        return super(TicketManager, self).active().filter(is_active=True)


class Ticket(BaseModel):
    user_obj = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    priority = enum.EnumField(TicketPriority, default=TicketPriority.LOW, verbose_name=_('Priority'))
    status = enum.EnumField(TicketStatus, default=TicketStatus.OPEN, verbose_name=_('Status'))
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name=_('UUID'))
    department = enum.EnumField(TicketDepartment, default=TicketDepartment.TECHNICAL, verbose_name=_('Department'))

    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    objects = TicketManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')


class TicketConversationManager(models.Manager):

    def get_queryset(self):
        return super(TicketConversationManager, self).get_queryset()

    def active(self):
        return super(TicketConversationManager, self).get_queryset().filter(is_active=True)


class TicketConversation(models.Model):
    user_obj = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    ticket_obj = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name=_('Ticket'))
    content = models.TextField(verbose_name=_('Content'))
    files_obj = models.ManyToManyField(FileField, verbose_name=_('Files'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = TicketConversationManager()

    def __unicode__(self):
        return "%s" % self.id

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Ticket Conversation')
        verbose_name_plural = _('Ticket Conversations')
