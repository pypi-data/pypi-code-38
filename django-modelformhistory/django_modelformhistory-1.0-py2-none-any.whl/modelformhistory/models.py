# coding: utf-8
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .helpers import get_object_repr


ADDITION = 1
CHANGE = 2
DELETION = 3

ACTION_TYPE_CHOICES = ((ADDITION, _("Addition")), (CHANGE, _("Change")), (DELETION, _("Deletion")))

ACTION_MESSAGES = {
    ADDITION: _("""{} has added '{}'"""),
    CHANGE: _("""{} has updated '{}'"""),
    DELETION: _("""{} has deleted '{}'"""),
}


@python_2_unicode_compatible
class Entry(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="history_entries", null=True, blank=True)

    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("object_type", "object_id")
    object_repr = models.CharField(max_length=200)

    # The short message for humans
    action_type = models.PositiveSmallIntegerField(choices=ACTION_TYPE_CHOICES)
    short_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-created_date",)

    def __str__(self):
        return self.short_message

    def is_addition(self):
        return self.action_type == ADDITION

    def is_change(self):
        return self.action_type == CHANGE

    def is_deletion(self):
        return self.action_type == DELETION

    def get_user_full_name(self):
        if self.created_by:
            return self.created_by.get_full_name() or self.created_by.username
        return _("Anonymous")

    @staticmethod
    def create(user, content_object, action_type, changelog=None, object_repr=""):
        changelog = changelog or []
        entry = Entry(created_by=user, action_type=action_type)
        if content_object:
            entry.object_type = ContentType.objects.get_for_model(content_object)
            entry.object_id = content_object.id
            entry.object_repr = get_object_repr(content_object)
        else:
            entry.object_repr = object_repr
        entry.short_message = ACTION_MESSAGES[action_type].format(entry.get_user_full_name(), entry.object_repr)
        entry.save()

        [ChangedData(entry=entry, **data).save() for data in changelog]
        return entry


class ChangedData(models.Model):
    entry = models.ForeignKey(Entry)
    label = models.CharField(_("Label"), max_length=200)
    initial_value = models.TextField(_("Initial value"), blank=True, null=True)
    changed_value = models.TextField(_("Updated value"), blank=True, null=True)
