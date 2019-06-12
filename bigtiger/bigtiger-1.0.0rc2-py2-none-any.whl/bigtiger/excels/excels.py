# -*- coding: utf-8 -*-

'''
Created on 2017年5月10日
@author: linkeddt.com
'''

from __future__ import unicode_literals

import copy
from collections import OrderedDict

from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.forms.utils import ErrorDict, ErrorList
from django.utils.translation import ugettext as _
from django.utils import six

from bigtiger.excels.fields import ExcelField


__all__ = ('BaseExcel', 'Excel', 'ExcelError')


class ExcelError(object):
    """
    Excel错误
    """

    def __init__(self, row_number, field, error_list):
        # row_number 行号
        # field 字段
        # error_list 错误列表
        self.row_number = row_number
        self.field = field
        self.error_list = error_list


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that collects Fields declared on the base classes.
    """
    def __new__(cls, name, bases, attrs):
        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, ExcelField):
                current_fields.append((key, value))
                attrs.pop(key)
        current_fields.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_fields'] = OrderedDict(current_fields)

        new_class = (super(DeclarativeFieldsMetaclass, cls)
                     .__new__(cls, name, bases, attrs))

        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class BaseExcel(object):

    def __init__(self, data=None, error_class=ErrorList, label_suffix=None, empty_permitted=False):
        self.data = data or {}
        self.error_class = error_class
        # Translators: This is the default suffix added to form field labels
        self.label_suffix = label_suffix if label_suffix is not None else _(
            ':')
        self.empty_permitted = empty_permitted
        self._errors = None  # Stores the errors after clean() has been called.
        self._changed_data = None

        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        self.fields = copy.deepcopy(self.base_fields)

    def __str__(self):
        return self.as_table()

    def __iter__(self):
        for name in self.fields:
            yield self[name]

    @property
    def errors(self):
        "Returns an ErrorDict for the data provided for the form"
        if self._errors is None:
            self.full_clean()
        return self._errors

    def is_valid(self):
        """
        Returns True if the form has no errors. Otherwise, False. If errors are
        being ignored, returns False.
        """
        # return self.is_bound and not bool(self.errors)
        return (not bool(self.errors))

    def non_field_errors(self):
        """
        Returns an ErrorList of errors that aren't associated with a particular
        field -- i.e., from Form.clean(). Returns an empty ErrorList if there
        are none.
        """
        return self.errors.get(NON_FIELD_ERRORS, self.error_class())

    def _raw_value(self, fieldname):
        """
        Returns the raw_value for a particular field name. This is just a
        convenient wrapper around widget.value_from_datadict.
        """
        field = self.fields[fieldname]
        prefix = self.add_prefix(fieldname)
        return field.widget.value_from_datadict(self.data, self.files, prefix)

    def add_error(self, field, error):
        """
        Update the content of `self._errors`.

        The `field` argument is the name of the field to which the errors
        should be added. If its value is None the errors will be treated as
        NON_FIELD_ERRORS.

        The `error` argument can be a single error, a list of errors, or a
        dictionary that maps field names to lists of errors. What we define as
        an "error" can be either a simple string or an instance of
        ValidationError with its message attribute set and what we define as
        list or dictionary can be an actual `list` or `dict` or an instance
        of ValidationError with its `error_list` or `error_dict` attribute set.

        If `error` is a dictionary, the `field` argument *must* be None and
        errors will be added to the fields that correspond to the keys of the
        dictionary.
        """
        if not isinstance(error, ValidationError):
            # Normalize to ValidationError and let its constructor
            # do the hard work of making sense of the input.
            error = ValidationError(error)

        if hasattr(error, 'error_dict'):
            if field is not None:
                raise TypeError(
                    "The argument `field` must be `None` when the `error` "
                    "argument contains errors for multiple fields."
                )
            else:
                error = error.error_dict
        else:
            error = {field or NON_FIELD_ERRORS: error.error_list}

        for field, error_list in error.items():
            if field not in self.errors:
                if field != NON_FIELD_ERRORS and field not in self.fields:
                    raise ValueError(
                        "'%s' has no field named '%s'." % (self.__class__.__name__, field))
                self._errors[field] = self.error_class()
            self._errors[field].extend(error_list)
            if field in self.cleaned_data:
                del self.cleaned_data[field]

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        self._errors = ErrorDict()
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed():
            return

        self._clean_fields()
        self._clean_form()
        self._post_clean()

    def _clean_fields(self):
        data_len = len(self.data)
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            # value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            if field.index >= data_len:
                value = None
            else:
                value = self.data[field.index]

            try:
                value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)

    def _clean_form(self):
        try:
            cleaned_data = self.clean()
        except ValidationError as e:
            self.add_error(None, e)
        else:
            if cleaned_data is not None:
                self.cleaned_data = cleaned_data

    def _post_clean(self):
        """
        An internal hook for performing additional cleaning after form cleaning
        is complete. Used for model validation in model forms.
        """
        pass

    def clean(self):
        """
        Hook for doing any extra form-wide cleaning after Field.clean() been
        called on every field. Any ValidationError raised by this method will
        not be associated with a particular field; it will have a special-case
        association with the field named '__all__'.
        """
        return self.cleaned_data

    def has_changed(self):
        """
        Returns True if data differs from initial.
        """
        return bool(self.changed_data)

    @property
    def changed_data(self):
        if self._changed_data is None:
            self._changed_data = []
            # XXX: For now we're asking the individual widgets whether or not the
            # data has changed. It would probably be more efficient to hash the
            # initial data, store it in a hidden field, and compare a hash of the
            # submitted data, but we'd need a way to easily get the string value
            # for a given field. Right now, that logic is embedded in the render
            # method of each widget.
            for name, field in self.fields.items():
                prefixed_name = self.add_prefix(name)
                data_value = field.widget.value_from_datadict(
                    self.data, self.files, prefixed_name)
                if not field.show_hidden_initial:
                    initial_value = self.initial.get(name, field.initial)
                    if callable(initial_value):
                        initial_value = initial_value()
                else:
                    initial_prefixed_name = self.add_initial_prefix(name)
                    hidden_widget = field.hidden_widget()
                    try:
                        initial_value = field.to_python(hidden_widget.value_from_datadict(
                            self.data, self.files, initial_prefixed_name))
                    except ValidationError:
                        # Always assume data has changed if validation fails.
                        self._changed_data.append(name)
                        continue
                if field._has_changed(initial_value, data_value):
                    self._changed_data.append(name)
        return self._changed_data


class Excel(six.with_metaclass(DeclarativeFieldsMetaclass, BaseExcel)):
    pass
    "A collection of Fields, plus their associated data."
