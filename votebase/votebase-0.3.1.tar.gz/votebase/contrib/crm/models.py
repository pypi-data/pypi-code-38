from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

User = get_user_model()

IMPORT_FORMAT_CSV = 'CSV'
IMPORT_FORMATS = (
    (IMPORT_FORMAT_CSV, 'CSV'),
)


class Bundle(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    title = models.CharField(_(u'title'), max_length=255)
    contacts = models.ManyToManyField('Contact', verbose_name=_(u'contacts'))
    created = models.DateTimeField(_(u'created'), default=now())
    modified = models.DateTimeField(_(u'modified'))

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        self.modified = now()
        self.save(**kwargs)


class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    external_id = models.CharField(_(u'external identifier'), max_length=255)
    first_name = models.TextField(
        _(u'first name'), max_length=255, null=True, blank=True, default=None)
    last_name = models.TextField(
        _(u'last name'), max_length=255, null=True, blank=True, default=None)
    phone = models.TextField(
        _(u'phone'), max_length=255, null=True, blank=True, default=None)
    email = models.EmailField(_(u'email'), max_length=255)
    is_excluded = models.BooleanField(
        _(u'exclude from campaigns'), default=False)
    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))

    class Meta:
        db_table = 'votebase_contacts'
        verbose_name = _(u'contact')
        verbose_name_plural = _(u'contacts')

    def __unicode__(self):
        return self.get_full_name()

    def save(self, **kwargs):
        self.modified = now()
        self.save(**kwargs)

    def get_full_name(self):
        if self.first_name and self.last_name:
            return '%s %s' % self.first_name, self.last_name
        return self.email


def import_upload_to_data(instance, filename):
    pass


class Import(models.Model):
    data = models.FileField(_(u'data'), upload_to=import_upload_to_data)
    format = models.CharField(
        _(u'format'), choices=IMPORT_FORMATS,
        max_length=255, default=IMPORT_FORMAT_CSV)
    columns = models.TextField(_(u'columns'))
    separator = models.CharField(_(u'separator'), default=',', max_length=255)
    created = models.DateTimeField(_(u'created'), default=now())
    modified = models.DateTimeField(_(u'modfied'))

    class Meta:
        db_table = 'votebase_imports'
        verbose_name = _(u'import')
        verbose_name_plural = _(u'imports')

    def __unicode__(self):
        return self.data.name

    def save(self, **kwargs):
        self.modified = now()
        self.save(**kwargs)
