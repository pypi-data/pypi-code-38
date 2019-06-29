# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.shortblogs.models import ShortBlog


# Create your models here.
class FAQManager(models.Manager):
    def get_queryset(self):
        return super(FAQManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)


class FAQ(models.Model):
    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True
    )
    short_blogs = models.ManyToManyField(ShortBlog, verbose_name=_('Content Segment'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = FAQManager()

    def save(self, *args, **kwargs):

        return super(FAQ, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(FAQ, self).__init__(*args, **kwargs)

    class Meta:
        # ordering = ['latitude', 'longitude']
        verbose_name = _('Frequently Asked Question')
        verbose_name_plural = _('Frequently Asked Questions')
