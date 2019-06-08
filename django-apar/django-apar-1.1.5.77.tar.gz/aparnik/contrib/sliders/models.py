# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.filefields.models import FileField
from aparnik.contrib.socials.models import SocialNetwork
from aparnik.contrib.pages.models import Page
from aparnik.contrib.segments.models import BaseSegment, BaseSegmentManager


# Create your models here.
class SliderManager(BaseModelManager):

    def get_queryset(self):
        return super(SliderManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def home(self):
        return self.active().filter(is_home=True)

    def library(self):
        return self.active().filter(is_library=True)

    def page(self, page):
        return self.active().filter(pages=page)


class Slider(BaseModel):
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Name'))
    image = models.ForeignKey(FileField, verbose_name=_('Image'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    objects = SliderManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Slide Show')
        verbose_name_plural = _('Slide Shows')


class SliderImage(Slider):

    objects = SliderManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Image Slide Show')
        verbose_name_plural = _('Image Slide Shows')


class SliderVideo(Slider):

    video = models.ForeignKey(FileField, verbose_name=_('Video'))

    objects = SliderManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Video Slider')
        verbose_name_plural = _('Video Sliders')


class SliderSocialNetwork(Slider):

    social = models.ForeignKey(SocialNetwork, verbose_name=_('Social'))

    objects = SliderManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Social Network Slider')
        verbose_name_plural = _('Social Network Sliders')


class SliderLink(Slider):

    link = models.URLField(verbose_name=_('Link'))

    objects = SliderManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Link Slider')
        verbose_name_plural = _('Link Sliders')


class SliderBaseModel(Slider):

    model = models.ForeignKey(BaseModel, verbose_name=_('Model'))

    objects = SliderManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Model Slider')
        verbose_name_plural = _('Model Sliders')


# Slider Segment Model
class SliderSegment(BaseSegment):

    objects = BaseSegmentManager()

    def __unicode__(self):
        return super(SliderSegment, self).__unicode__()

    class Meta:
        verbose_name = _('Slider Segment')
        verbose_name_plural = _('Sliders Segments')
