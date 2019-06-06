import string

from django.db import models
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

import managers


class Tag(models.Model):
    '''Tag allows typing event and data linked to events.

       name:
           the string identifier of the tag
    '''
    objects = managers.TagManager()
    name = models.CharField(verbose_name=_('name'), max_length=32, unique=True,
            db_index=True)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    class Meta:
        ordering = ('name',)
        verbose_name = _('tag')


class Template(models.Model):
    '''Template for formatting an event.

       ex.: Template(
                content='{user1} gave group {group} to {user2}')
    '''
    objects = managers.TemplateManager()
    content = models.TextField(verbose_name=_('content'), unique=True,
            db_index=True)

    def __unicode__(self):
        return self.content

    def natural_key(self):
        return (self.content,)

    class Meta:
        ordering = ('content',)


class Journal(models.Model):
    '''One line of the journal.

       Each recorded event in the journal is a Journal instance.

       time - the time at which the event was recorded
       tag - the tag giving the type of event
       template - a format string to present the event
       message - a simple string representation of the event, computed using
       the template and associated datas.
    '''
    objects = managers.JournalManager()

    time = models.DateTimeField(verbose_name=_('time'), auto_now_add=True,
            db_index=True)
    tag = models.ForeignKey(Tag, verbose_name=_('tag'),
            on_delete=models.PROTECT)
    template = models.ForeignKey(Template, verbose_name=_('template'),
            on_delete=models.PROTECT)
    message = models.CharField(verbose_name=_('message'), max_length=128,
            db_index=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = _('journal entry')
        verbose_name_plural = _('journal entries')

    def message_context(self):
        ctx = {}
        for data in self.objectdata_set.all():
            if data.content_object is not None:
                ctx[data.tag.name] = data.content_object
            else:
                ctx[data.tag.name] = u'<deleted {content_type} {object_id}>'.format(
                        content_type=data.content_type, object_id=data.object_id)
        for data in self.stringdata_set.all():
            ctx[data.tag.name] = data.content
        for text, field, format_spec, conversion in string.Formatter().parse(self.template.content):
            if not field:
                continue
            splitted = field.split('.')
            if splitted[0] not in ctx:
                ctx[splitted[0]] = None
        return ctx

    def add_object_tag(self, tag_name, obj):
        ObjectData(journal=self,
                tag=Tag.objects.get_cached(name=tag_name),
                content_object=obj).save()

    def __unicode__(self):
        ctx = self.message_context()
        return self.template.content.format(**ctx)

    def __repr__(self):
        return '<Journal pk:{0} tag:{1} message:{2}>'.format(
                self.pk, unicode(self.tag).encode('utf-8'),
                unicode(self.message).encode('utf-8'))


class StringData(models.Model):
    '''String data associated to a recorded event.

       journal:
           the recorded event
       tag:
           the identifier for this data
       content:
           the string value of the data
    '''
    journal = models.ForeignKey(Journal, verbose_name=_('journal entry'))
    tag = models.ForeignKey(Tag, verbose_name=_('tag'))
    content = models.TextField(verbose_name=_('content'))

    class Meta:
        unique_together = (('journal', 'tag'),)
        verbose_name = _('linked text string')


class ObjectData(models.Model):
    '''Object data associated with a recorded event.

       journal:
           the recorded event
       tag:
           the identifier for this data
       content_object:
           the object value of the data
    '''
    journal = models.ForeignKey(Journal, verbose_name=_('journal entry'))
    tag = models.ForeignKey(Tag, verbose_name=_('tag'))
    content_type = models.ForeignKey('contenttypes.ContentType',
            verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(db_index=True,
            verbose_name=_('object id'))
    content_object = generic.GenericForeignKey('content_type',
            'object_id')

    class Meta:
        unique_together = (('journal', 'tag'),)
        verbose_name = _('linked object')

    def __unicode__(self):
        return u'{0}:{1}:{2}'.format(self.journal.id, self.tag, self.content_object)
