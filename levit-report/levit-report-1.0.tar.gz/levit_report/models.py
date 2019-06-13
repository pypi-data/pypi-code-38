import mimetypes

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


CONVERT_CHOICES = [
    ('pdf', 'pdf'),
    ('doc', 'doc'),
    ('docx', 'docx'),
    ('xls', 'xls'),
    ('xlsx', 'xlsx'),
]

EXT_MAPPING = {
    'text': 'odt',
    'spreadsheet': 'ods',
}


class Document(models.Model):

    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    source = models.FileField(_('source'), upload_to='reports')
    convert_to = models.CharField(_('convert to'), max_length=5, choices=CONVERT_CHOICES, blank=True, null=True)
    merge_with_tos = models.BooleanField(_('merge with tos'), default=False)
    content_type = models.ForeignKey(ContentType, related_name='reports', verbose_name=_('content type'),
                                     on_delete=models.CASCADE)
    get_language_from_target = models.BooleanField(_('get language from target'), default=False)
    is_default_for_ct = models.BooleanField(_('is default for content type'), default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default_for_ct:
            self.__class__.objects.filter(content_type=self.content_type, is_default_for_ct=True) \
                .update(is_default_for_ct=False)
        return super(Document, self).save(*args, **kwargs)

    @property
    def extension(self):
        if self.convert_to is not None and self.convert_to != '':
            return self.convert_to
        ext = self.source.name.rsplit('.', 1)[-1]
        if 'oasis.opendocument' in self.source.name:
            return EXT_MAPPING.get(ext, ext)
        return ext

    @property
    def output_type(self):
        return mimetypes.guess_type('brol.{}'.format(self.extension))[0]
