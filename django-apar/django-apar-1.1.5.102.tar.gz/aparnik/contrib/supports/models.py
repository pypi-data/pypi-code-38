# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.socials.models import SocialNetwork
from aparnik.utils.fields import PhoneField


# Create your models here.
class SupportManager(BaseModelManager):

    def get_queryset(self):
        return super(SupportManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)


class Support(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    online = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Online'))
    offline = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Offline'))
    phone = PhoneField(blank=True, null=True, mobile=False, verbose_name=_('Phone'))
    online_days = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Online Days'))

    socials = models.ManyToManyField(SocialNetwork, verbose_name=_('Socials'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    objects = SupportManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Support')
        verbose_name_plural = _('Supports')
