# coding: utf-8
from __future__ import print_function, division, absolute_import, unicode_literals

# from .exceptions import SouvenirFormException
from .models import Entry, ADDITION, CHANGE
from .helpers import get_human_value_for_field


class HistoryModelFormMixin(object):
    """

    Extend your django modelform with that mixin.
    Place it in the first position.

        class FooForm(HistoryModelFormMixin, forms.ModelForm):
           ...

    If you pass a 'request' parameter o your form, the request.user will be
    saved in the history Entry. You can override this by implementing a 'get_history_user' method in your modelform.


    """

    class Meta:
        history_exclude = ()  # List of form field that won't be saved in the history

    def __init__(self, *args, **kwargs):
        super(HistoryModelFormMixin, self).__init__(*args, **kwargs)
        self._history_exclude = getattr(self.Meta, "history_exclude", ())
        self._history_user = self.get_history_user()
        self._history_action_type = self.get_history_action_type()

    def get_history_user(self):
        """
        Returns the auth.User that will be saved in the history entry.
        By default, searches in self.request.user, or return None.
        """
        if hasattr(self, "request"):
            return getattr(self.request, "user", None)

    def get_history_action_type(self):
        """Is it ADDITION or CHANGE ? Returns a int"""
        if self.instance.pk is None:
            return ADDITION
        else:
            return CHANGE

    def save(self, *args, **kwargs):
        obj = super(HistoryModelFormMixin, self).save(*args, **kwargs)
        if self.has_changed() or self.files:
            changelog = []
            if self._history_action_type == CHANGE:
                bounded_fields = dict([(f.name, f) for f in self])
                for fieldname in self.changed_data:
                    field = bounded_fields.get(fieldname)
                    initial_value = get_human_value_for_field(field, field.initial)
                    changed_value = get_human_value_for_field(field, field.data)
                    if initial_value != changed_value:
                        changelog.append(
                            {"label": field.label, "initial_value": initial_value, "changed_value": changed_value}
                        )
                # for fieldname, file_upload in self.files.items():

            Entry.create(
                user=self._history_user,
                content_object=self.instance,
                action_type=self._history_action_type,
                changelog=changelog,
            )
        return obj
