# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
# from aparnik.contrib.segments.admin import


# Category Manager
class PageManager(BaseModelManager):
    def get_queryset(self):
        return super(PageManager, self).get_queryset()

    def active(self):
        return super(PageManager, self).active()

    def home(self):
        return self.active().filter(is_show_in_home=True)


# Page Model
class Page(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    english_title = models.CharField(max_length=100, verbose_name=_('English Title'))

    is_show_in_home = models.BooleanField(default=False, verbose_name=_('Is Show in home'))

    objects = PageManager()

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.title

    # def get_api_uri(self):
    #     return reverse("api:category:detail", args=[self.id])

