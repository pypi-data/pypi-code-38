# -*- coding: utf-8 -*-


from django.db import models
from django.db.models.signals import post_save
from django.db.models.aggregates import Max
from polymorphic.models import PolymorphicManager, PolymorphicModel
from django.utils.translation import ugettext as _
from django.urls import reverse

from aparnik.contrib.basemodels.models import BaseModel
from aparnik.contrib.pages.models import Page


# Base Segment MANAGER
class BaseSegmentManager(PolymorphicManager):

    def get_queryset(self):
        return super(BaseSegmentManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def page(self, page):
        return self.active().filter(pages=page).order_by('page_sort_segment__sort')


# Base Segment Model
class BaseSegment(PolymorphicModel):
    title = models.CharField(max_length=60, verbose_name=_('Title'))
    model_obj = models.ManyToManyField(BaseModel, through='SegmentSort', verbose_name=_('Model'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    pages = models.ManyToManyField(Page, blank=True, through='PageSort', related_name='segment_pages', verbose_name=_('Page'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = BaseSegmentManager()

    def __str__(self):
        return "%s" % self.title

    class Meta:
        verbose_name = _('Base Segment')
        verbose_name_plural = _('Bases Segments')

    def get_api_list_model_uri(self):
        return reverse('aparnik-api:segments:list-model-segment', args=[self.id])


class SegmentSortManager(models.Manager):

    def get_queryset(self):
        return super(SegmentSortManager, self).get_queryset().order_by('sort')

    def all(self):
        return self.get_queryset()


class SegmentSort(models.Model):
    model_obj = models.ForeignKey(BaseModel, related_name='segment_sort_model', on_delete=models.CASCADE, verbose_name=_('Model'))
    segment_obj = models.ForeignKey(BaseSegment, related_name='segment_sort_segment', on_delete=models.CASCADE, verbose_name=_('Segment'))
    sort = models.IntegerField(default=0, verbose_name=_('Sort'))

    objects = SegmentSortManager()

    class Meta:
        verbose_name = _('Segment Sort')
        verbose_name_plural = _('Segments Sort')
        ordering = ['sort']


def post_save_segment_sort_receiver(sender, instance, created, *args, **kwargs):
    if instance.sort == 0:
        max = SegmentSort.objects.filter(segment_obj=instance.segment_obj).aggregate(Max('sort'))['sort__max']
        instance.sort = max + 1
        instance.save()
    else:
        for obj in SegmentSort.objects.exclude(id=instance.id).filter(segment_obj=instance.segment_obj, sort=instance.sort):
            obj.sort = obj.sort + 1
            obj.save()


post_save.connect(post_save_segment_sort_receiver, sender=SegmentSort)


class PageSort(models.Model):
    page_obj = models.ForeignKey(Page, related_name='page_sort_page', on_delete=models.CASCADE, verbose_name=_('Page'))
    segment_obj = models.ForeignKey(BaseSegment, related_name='page_sort_segment', on_delete=models.CASCADE, verbose_name=_('Segment'))
    sort = models.IntegerField(default=0, verbose_name=_('Sort'))

    class Meta:
        verbose_name = _('Page Sort')
        verbose_name_plural = _('Pages Sort')
        ordering = ['sort']


def post_save_page_sort_receiver(sender, instance, created, *args, **kwargs):
    if instance.sort == 0:
        max = PageSort.objects.filter(page_obj=instance.page_obj).aggregate(Max('sort'))['sort__max']
        instance.sort = max + 1
        instance.save()
    else:
        for obj in PageSort.objects.exclude(id=instance.id).filter(page_obj=instance.page_obj, sort=instance.sort):
            obj.sort = obj.sort + 1
            obj.save()


post_save.connect(post_save_page_sort_receiver, sender=PageSort)
