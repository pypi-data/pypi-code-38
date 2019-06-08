# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.filefields.models import FileField
from aparnik.contrib.segments.models import BaseSegment, BaseSegmentManager
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager


# Create your models here.
class SocialNetworkManager(BaseModelManager):
    def get_queryset(self):
        return super(SocialNetworkManager, self).get_queryset()


class SocialNetwork(BaseModel):
    link = models.URLField(
        max_length=255,
        verbose_name=_('Link')
    )

    icon = models.ForeignKey(
        FileField,
        verbose_name=_('Icon'),
    )

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=31,
        default=None
    )
    value = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Value'))

    android_app_shortcut = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Android shortcut'))
    ios_app_shortcut = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('iOS shortcut'))

    def __unicode__(self):
        return '%s, %s' % (self.title, self.link)

    def __init__(self, *args, **kwargs):
        super(SocialNetwork, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Social Network')
        verbose_name_plural = _('Social Networks')


class SocialNetworkSegment(BaseSegment):

    objects = BaseSegmentManager()

    def __unicode__(self):
        return super(SocialNetworkSegment, self).__unicode__()

    class Meta:
        verbose_name = _('Social Segment')
        verbose_name_plural = _('Social Segments')
