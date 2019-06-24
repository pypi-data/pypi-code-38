# -*- coding: utf-8 -*-

from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from ckeditor_uploader.fields import RichTextUploadingField
from aparnik.contrib.basemodels.models import BaseModelManager, BaseModel
from aparnik.contrib.filefields.models import FileField
from aparnik.contrib.categories.models import Category

User = get_user_model()


# Create your models here.
class NewsManager(BaseModelManager):
    def get_queryset(self):
        return super(NewsManager, self).get_queryset()

    def this_user(self, user):
        return self.get_queryset().filter(user_obj=user)

    def active(self):
        return self.get_queryset().filter(is_published=True, publish_date__lte=now())


class News(BaseModel):
    user_obj = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=300, unique=True, allow_unicode=True, verbose_name=_('Slug'))
    cover_images = models.ManyToManyField(FileField, blank=True, verbose_name=_('Cover Images'))
    content = RichTextUploadingField(config_name='basic', verbose_name=_('Content'))
    is_published = models.BooleanField(default=True, verbose_name=_('Is Published'))
    publish_date = models.DateTimeField(default=now, verbose_name=_('Published Date'))
    categories = models.ManyToManyField(Category, blank=True, verbose_name=_('Categories'))
    # TODO: add tag
    # tag = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Tag'))

    objects = NewsManager()

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('NEWS')

    def __init__(self, *args, **kwargs):
        super(News, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title, allow_unicode=True)
        super(News, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)
