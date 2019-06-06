import logging

from exceptions import JournalException
from models import (Journal, Tag, Template)

import django.db.models
from django.conf import settings

from decorator import atomic

__all__ = ('record', 'error_record', 'Journal')


def unicode_truncate(s, length, encoding='utf-8'):
    '''Truncate an unicode string so that its UTF-8 encoding is less than
       length.'''
    encoded = s.encode(encoding)[:length]
    return encoded.decode(encoding, 'ignore')

@atomic
def record(tag, template, using=None, **kwargs):
    '''Record an event in the journal. The modification is done inside the
       current transaction.

       tag:
           a string identifier giving the type of the event
       tpl:
           a format string to describe the event
       kwargs:
           a mapping of object or data to interpolate in the format string
    '''
    template = unicode(template)
    tag = Tag.objects.using(using).get_cached(name=tag)
    template = Template.objects.using(using).get_cached(content=template)
    try:
        message = template.content.format(**kwargs)
    except (KeyError, IndexError), e:
        raise JournalException(
                'Missing variable for the template message', template, e)
    try:
        logger = logging.getLogger('django.journal.%s' % tag)
        if tag.name == 'error' or tag.name.startswith('error-'):
            logger.error(message)
        elif tag.name == 'warning' or tag.name.startswith('warning-'):
            logger.warning(message)
        else:
            logger.info(message)
    except:
        try:
            logging.getLogger('django.journal').exception('Unable to log msg')
        except:
            pass # we tried, really, we tried
    journal = Journal.objects.using(using).create(tag=tag, template=template,
            message=unicode_truncate(message, 128))
    for name, value in kwargs.iteritems():
        if value is None:
            continue
        tag = Tag.objects.using(using).get_cached(name=name)
        if isinstance(value, django.db.models.Model):
            journal.objectdata_set.create(tag=tag, content_object=value)
        else:
            journal.stringdata_set.create(tag=tag, content=unicode(value))
    return journal

def error_record(tag, tpl, **kwargs):
    '''Records error events.

       You must use this function when logging error events. It uses another
       database alias than the default one to be immune to transaction rollback
       when logging in the middle of a transaction which is going to
       rollback.
    '''
    return record(tag, tpl,
            using=getattr(settings, 'JOURNAL_DB_FOR_ERROR_ALIAS', 'default'),
            **kwargs)
