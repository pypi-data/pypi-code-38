# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import ugettext as _

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.segments.models import BaseSegment, BaseSegmentManager
from aparnik.contrib.filefields.models import FileField
from aparnik.contrib.categories.models import Category
from aparnik.packages.shops.files.models import File, FileManager


User = get_user_model()


# Publisher Manager
class PublisherManager(BaseModelManager):

    def get_queryset(self):
        return super(PublisherManager, self).get_queryset()

    def active(self):
        return super(PublisherManager, self).active()


# Publisher Model
class Publisher(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_('Title'))

    objects = PublisherManager()

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')

    def __unicode__(self):
        return self.title

    def get_api_uri(self):
        return reverse('aparnik-api:educations:publishers:details', args=[self.id])


# Publisher Manager
class WriterTranslatorManager(BaseModelManager):

    def get_queryset(self):
        return super(WriterTranslatorManager, self).get_queryset()

    def active(self):
        return super(WriterTranslatorManager, self).active()


# Publisher Model
class WriterTranslator(BaseModel):
    first_name = models.CharField(max_length=60, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=60, verbose_name=_('Last Name'))

    objects = WriterTranslatorManager()

    class Meta:
        verbose_name = _('Writer Translator')
        verbose_name_plural = _('Writers Translators')

    def __unicode__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_api_uri(self):
        return reverse('aparnik-api:educations:writers-translators:details', args=[self.id])


# Library MANAGER
class BookManager(FileManager):

    def get_queryset(self):
        return super(BookManager, self).get_queryset()

    def active(self):
        return super(BookManager, self).active()


# Library MODEL
class Book(File):
    sample_book = models.ForeignKey(FileField, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Sample Book'))
    published_date = models.DateTimeField(verbose_name=_('Published Date'))
    category_obj = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))
    publisher_obj = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name=_('Publisher'))
    writers_obj = models.ManyToManyField(WriterTranslator, related_name='library_writers', verbose_name=_('Writers'))
    translators_obj = models.ManyToManyField(WriterTranslator, blank=True, related_name='library_translators', verbose_name=_('Translators'))

    # TODO : Add languages field

    objects = BookManager()

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')

    def __unicode__(self):
        return "%s" % self.title


# Base Segment Model
class BookSegment(BaseSegment):

    objects = BaseSegmentManager()

    def __unicode__(self):
        return super(BookSegment, self).__unicode__()

    class Meta:
        verbose_name = _('Book Segment')
        verbose_name_plural = _('Book Segments')
