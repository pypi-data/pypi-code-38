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
    """Entry log that will save an action made by a user (form submission, or any other custom action)

    Query examples:
        You can extend your model with HistoryBaseModel defined below
        or directly query the Entry model.

        >>> entries = Entry.get_for_model(my_instance)  # get all entries for an instance
        >>> entries = entries.filter(created_by=my_user)  # filter entries on a specific user

    """

    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="history_entries", null=True, blank=True)

    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("object_type", "object_id")
    object_repr = models.CharField(max_length=200)

    action_type = models.PositiveSmallIntegerField(choices=ACTION_TYPE_CHOICES)
    short_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-created_date",)

    def __str__(self):
        return self.short_message

    @staticmethod
    def create(user, content_object, action_type=CHANGE, changelog=None, short_message=None):
        """Saves an Entry log history of the 'content_object'

        Args:
            user (auth.User): The user who made the action
            content_object (models.Model): The related model object
            action_type (int): Action type (see ACTION_TYPE_CHOICES)
            changelog (list, optional): List of ChangedData attributes that will be created
            object_repr (str, optional): A representation of the content_object
            short_message (str, optional): A short message that can be displayed if no changelog is available

        Returns:
            Entry: The freshly created Entry
        """
        changelog = changelog or []
        entry = Entry.objects.create(
            created_by=user,
            action_type=action_type,
            object_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.id,
            object_repr=get_object_repr(content_object),
        )

        if not short_message:
            short_message = ACTION_MESSAGES[action_type].format(entry.get_user_full_name(), entry.object_repr)

        entry.short_message = short_message
        entry.save()
        [ChangedData(entry=entry, **data).save() for data in changelog]
        return entry

    @staticmethod
    def get_for_model(obj):
        return Entry.objects.filter(object_id=obj.pk, object_type=ContentType.objects.get_for_model(obj))

    def get_user_full_name(self):
        """Returns the human readable name of the user"""
        if self.created_by:
            return self.created_by.get_full_name() or self.created_by.username
        return _("Anonymous")

    def is_addition(self):
        return self.action_type == ADDITION

    def is_change(self):
        return self.action_type == CHANGE

    def is_deletion(self):
        return self.action_type == DELETION


@python_2_unicode_compatible
class ChangedData(models.Model):
    """Store the changed datas of a forms.ModelForm
    The label, initial value and changed value intend to be human readable,
    so they can be used directly to show to end-users.
    """

    entry = models.ForeignKey(Entry)
    label = models.CharField(_("Label"), max_length=200)
    initial_value = models.TextField(_("Initial value"), blank=True, null=True)
    changed_value = models.TextField(_("Updated value"), blank=True, null=True)

    def __str__(self):
        return self.label


class HistoryBaseModel(models.Model):
    """Base model that implements utilities to query history entries of your models.
    Just extends your model with this one :

        >> class MyModel(HistoryBaseModel):
        >>     pass
        >>
        >> inst = MyModel.objects.get(...)
        >> inst.get_history_entries()  # Returns <Entry queryset>

    """

    def get_history_entries(self):
        """Returns all the history Entries for that model"""
        return Entry.get_for_model(self)

    def log_custom_history(self, user, message):
        """Save a message in history for that instance"""
        return Entry.create(user=user, content_object=self, short_message=message)

    class Meta:
        abstract = True
