from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Tag(models.Model):
    """
    A single tag.

    A tag has a unique name, and data models is added to a tag via :class:`.TaggedObject`.
    """
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    #: The label for the tag.
    taglabel = models.CharField(
        verbose_name=_('Tag'),
        max_length=30,
        unique=True,
        help_text=_('Maximum 30 characters.')
    )

    #: The tagtype is a way for applications to group tags by type.
    #: No logic is assigned to this field by default, other than
    #: that is is ``db_indexed``. The valid choices for the field
    #: is configured via the :setting:`IEVV_TAGFRAMEWORK_TAGTYPE_CHOICES`
    #: setting.
    tagtype = models.CharField(
        max_length=255,
        db_index=True,
        blank=True, null=False,
        default=''
    )

    @staticmethod
    def get_tagtype_choices():
        """
        Returns choices for :obj:`.tagtype`.

        This is not set as choices on the field (because changing that would
        trigger a migration), but it should be used in any form displaying
        tagtype.

        You configure the return value via the
        ``IEVV_TAGFRAMEWORK_TAGTYPE_CHOICES`` Django setting.
        """
        choices = getattr(settings, 'IEVV_TAGFRAMEWORK_SITE_TYPE_CHOICES',
                          [('', '')])
        for choice in choices:
            yield choice

    @classmethod
    def get_tagtype_valid_values(cls):
        """
        Returns an iterator over the choices returned by
        :meth:`.get_tagtype_choices`, but only the values (not the labels)
        as a flat list.
        """
        for value, label in cls.get_tagtype_choices():
            yield value

    def clean(self):
        tagtype_valid_values = set(Tag.get_tagtype_valid_values())
        if self.tagtype not in tagtype_valid_values:
            raise ValidationError({
                'tagtype': _('Must be one of: %(choices)s. Current value: %(value)s.') % {
                    'choices': ', '.join(repr(value) for value in tagtype_valid_values),
                    'value': repr(self.tagtype),
                }
            })


class TaggedObject(models.Model):
    """
    Represents a many-to-many relationship between any data model object and
    a :class:`.Tag`.
    """
    class Meta:
        verbose_name = _('Tagged object')
        verbose_name_plural = _('Tagged objects')

    #: The :class:`.Tag`.
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    #: The ContentType of the tagged object.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    #: The ID of the tagged object.
    object_id = models.PositiveIntegerField()

    #: The GenericForeignKey using :obj:`~TaggedObject.content_type` and
    #: :obj:`~TaggedObject.object_id` to create a generic foreign key
    #: to the tagged object.
    content_object = GenericForeignKey('content_type', 'object_id')
