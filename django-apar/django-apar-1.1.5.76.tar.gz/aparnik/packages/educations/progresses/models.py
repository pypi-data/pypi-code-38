# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.packages.educations.courses.models import Course, CourseFile

User = get_user_model()


# Create your models here.
class ProgressSummaryManager(models.Manager):

    def get_queryset(self):
        return super(ProgressSummaryManager, self).get_queryset()

    def active(self):
        return self.get_queryset()

    def this_user(self, user):
        if not user.is_authenticated():
            return ProgressSummary.objects.none()
        return self.active().filter(user_obj=user)


class ProgressSummary(models.Model):
    percentage = models.FloatField(verbose_name=_('Percentage'))
    model = models.ForeignKey(Course, related_name='progress_summaries', verbose_name=_('Models'))
    user_obj = models.ForeignKey(User, related_name='progress_user', verbose_name=_('User'))

    objects = ProgressSummaryManager()

    class Meta:
        verbose_name = _('Progress Summary')
        verbose_name_plural = _('Progress Summary')

    def __unicode__(self):
        return '%s' % self.id


class ProgressesManager(BaseModelManager):

    def get_queryset(self):
        return super(ProgressesManager, self).get_queryset()

    def active(self):
        return super(ProgressesManager, self).active().filter(is_published=True)

    def this_user(self, user, file_obj=None):
        if not user.is_authenticated():
            return ProgressSummary.objects.none()

        queryset = self.active().filter(user_obj=user)
        if file_obj:
            queryset = queryset.filter(file_obj=file_obj)

        return queryset


class Progresses(BaseModel):
    STATUS_NOTSTARTED = 'SN'
    STATUS_STARTED = 'SS'
    STATUS_MANUALCOMPLETE = 'SM'
    STATUS_AUTOCOMPLETE = 'SA'
    STATUS = (
        (STATUS_NOTSTARTED, _('Not started')),
        (STATUS_STARTED, _('Started')),
        (STATUS_MANUALCOMPLETE, _('Manual complete')),
        (STATUS_AUTOCOMPLETE, _('Auto complete')),
    )
    is_published = models.BooleanField(default=True, verbose_name=_('Published'))
    user_obj = models.ForeignKey(User, verbose_name=_('User'))
    file_obj = models.ForeignKey(CourseFile, verbose_name=_('File'))
    status = models.CharField(max_length=2, choices=STATUS, default=STATUS_NOTSTARTED, verbose_name=_(
        'Status'))  # Determines if the file not started, started, completed automatically or completed manually by user

    objects = ProgressesManager()

    def __init__(self, *args, **kwargs):
        super(Progresses, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Progress')
        verbose_name_plural = _('Progresses')

    def __unicode__(self):
        return unicode(self.status)
