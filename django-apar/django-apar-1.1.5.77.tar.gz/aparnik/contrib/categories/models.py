# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.segments.models import BaseSegment, BaseSegmentManager
from aparnik.contrib.filefields.models import FileField
from aparnik.contrib.pages.models import Page


# Category Manager
class CategoryManager(BaseModelManager):
    def get_queryset(self):
        return super(CategoryManager, self).get_queryset()

    def page(self, page):
        return self.active().filter(pages=page)

    def first_level(self):
        return self.active().filter(parent_obj__isnull=True)

    def level(self, level):
        return self.active().filter(parent_obj__id=level)

    def home(self):
        from aparnik.contrib.settings.models import Setting
        try:
            setting = Setting.objects.get(key='CATEGORIES_HOME_ROOT')
            return self.active().filter(parent_obj__id=setting.get_value())
        except Exception as e:
            pass
        return self.none()

    def books(self):
        if is_app_installed('aparnik.packages.educations.books'):
            from aparnik.contrib.settings.models import Setting
            try:
                setting = Setting.objects.get(key='CATEGORIES_BOOKS_ROOT')
                return self.active().filter(parent_obj__id=setting.get_value())
            except Exception as e:
                pass
        return self.none()

    def courses(self):
        if is_app_installed('aparnik.packages.educations.courses'):
            from aparnik.contrib.settings.models import Setting
            try:
                setting = Setting.objects.get(key='CATEGORIES_COURSES_ROOT')
                return self.active().filter(parent_obj__id=setting.get_value())
            except Exception as e:
                pass
        return self.none()

    def childs(self, category_obj):
        return self.active().filter(parent_obj=category_obj)

    def childs_count(self, category_obj):
        return self.childs(category_obj).count()


# Category Model
class Category(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    image = models.ForeignKey(FileField, verbose_name=_('Image'))
    parent_obj = models.ForeignKey('self', blank=True, null=True, verbose_name=_('Parent'))
    # pages = models.ManyToManyField(Page, blank=True, verbose_name=_('Page'))

    objects = CategoryManager()

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
        return self.title

    # def get_api_uri(self):
    #     return reverse("api:category:detail", args=[self.id])

    def get_api_model_list_uri(self):
        return reverse('aparnik-api:categories:list-model', args=[self.id])

    def get_api_child_uri(self):
        return reverse('aparnik-api:categories:list-childs', args=[self.id])


# Course Segment Model
class CategorySegment(BaseSegment):

    objects = BaseSegmentManager()

    def __unicode__(self):
        return super(CategorySegment, self).__unicode__()

    class Meta:
        verbose_name = _('Category Segment')
        verbose_name_plural = _('Category Segments')
