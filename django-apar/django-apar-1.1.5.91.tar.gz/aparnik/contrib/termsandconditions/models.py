# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.shortblogs.models import ShortBlog


# Create your models here.
class TermsAndConditionsManager(models.Manager):
    def get_queryset(self):
        return super(TermsAndConditionsManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)


class TermsAndConditions(models.Model):
    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True
    )
    short_blogs = models.ManyToManyField(ShortBlog, verbose_name=_('Content Segment'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = TermsAndConditionsManager()

    def save(self, *args, **kwargs):

        return super(TermsAndConditions, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(TermsAndConditions, self).__init__(*args, **kwargs)

    class Meta:
        # ordering = ['latitude', 'longitude']
        verbose_name = _('Terms And Conditions')
        verbose_name_plural = _('Terms And Conditions')
