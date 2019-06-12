# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals

from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class ViewAdmin(object):

    def register(self, form, admin):
        rf = None
        if hasattr(admin, 'readonly_fields'):
            rf = admin.readonly_fields

        fieldsets = None if admin is None else admin.fieldsets
        return ViewForm(form, fieldsets=fieldsets, readonly_fields=rf)


class ViewForm(object):

    def __init__(self, form, fieldsets, readonly_fields=None):
        self.form = form
        if fieldsets is None:
            self.fieldsets = (
                (None, {'fields': [name for name in form.fields.items()]}),)
        else:
            self.fieldsets = normalize_fieldsets(fieldsets)

        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields

    def __iter__(self):
        for name, options in self.fieldsets:
            yield Fieldset(self.form, name,
                           readonly_fields=self.readonly_fields,
                           **options
                           )

    def first_field(self):
        try:
            fieldset_options = self.fieldsets[0]
            field_name = fieldset_options['fields'][0]
            if not isinstance(field_name, basestring):
                field_name = field_name[0]
            return self.form[field_name]
        except (KeyError, IndexError):
            pass
        try:
            return iter(self.form).next()
        except StopIteration:
            return None

    def _media(self):
        media = self.form.media
        for fs in self:
            media = media + fs.media
        return media
    media = property(_media)


class Fieldset(object):

    def __init__(self, form, name=None, readonly_fields=(), fields=(), classes=(),
                 description=None):
        self.form = form
        self.name, self.fields = name, fields
        self.classes = u' '.join(classes)
        self.description = description
        self.readonly_fields = readonly_fields

    def __iter__(self):
        for field in self.fields:
            yield Fieldline(self.form, field, self.readonly_fields)


class Fieldline(object):

    def __init__(self, form, field, readonly_fields=None):
        self.form = form  # A django.forms.Form instance
        if not hasattr(field, "__iter__"):
            self.fields = [field]
        else:
            self.fields = field
        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields

    def __iter__(self):
        for i, field in enumerate(self.fields):
            if field in self.readonly_fields:
                yield AdminReadonlyField(self.form, field, is_first=(i == 0))
            else:
                yield AdminField(self.form, field, is_first=(i == 0))

    def errors(self):
        return mark_safe(u'\n'.join([self.form[f].errors.as_ul() for f in self.fields if f not in self.readonly_fields]).strip('\n'))


class AdminField(object):

    def __init__(self, form, field, is_first):
        self.field = form[field]  # A django.forms.BoundField instance
        self.is_first = is_first  # Whether this field is first on the line
        self.is_checkbox = isinstance(
            self.field.field.widget, forms.CheckboxInput)
        self.is_hidden = isinstance(self.field.field.widget, forms.HiddenInput)

    def label_tag(self):
        classes = ['control-label']
        if not self.field.label:
            return ""
        contents = conditional_escape(force_unicode(self.field.label))
        if self.is_checkbox:
            classes.append(u'CheckboxLabel')
        if self.field.field.required:
            classes.append(u'required')
            contents = '<span>*</span>' + contents
        if not self.is_first:
            classes.append(u'inline')
        attrs = classes and {'class': u' '.join(classes)} or {}
        return self.field.label_tag(contents=mark_safe(contents), attrs=attrs, label_suffix='：')

    def errors(self):
        return mark_safe(self.field.errors.as_ul())


class AdminReadonlyField(object):

    def __init__(self, form, field, is_first):
        self.field = form[field]  # A django.forms.BoundField instance
        self.form = form
        self.is_first = is_first
        self.is_checkbox = False
        self.is_readonly = True

    def label_tag(self):
        classes = ['control-label']
        contents = conditional_escape(force_unicode(self.field.label))
        if self.is_checkbox:
            classes.append(u'CheckboxLabel')
        if self.field.field.required:
            classes.append(u'required')
            contents = '<span>*</span>' + contents
        if not self.is_first:
            classes.append(u'inline')
        attrs = classes and {'class': u' '.join(classes)} or {}
        return self.field.label_tag(contents=mark_safe(contents), attrs=attrs, label_suffix='：')

    def contents(self):
        widget = self.field.field.widget
        if widget is not None:
            if isinstance(widget, forms.Textarea) or isinstance(widget, forms.TextInput):
                widget.attrs.update({'readonly': 'readonly'})
            else:
                widget.attrs.update({'disabled': 'disabled'})

        """
        data = ''.join(self.field.data) if isinstance(
            self.field.data, list) else self.field.data
        """

        value = self.field.value()
        data = ','.join(value) if isinstance(value, list) else value

        autoid = self.field.auto_id
        name = self.field.name

        oldname = u'name="%s"' % name
        newname = u'name="%s_hdn"' % name
        oldid = u'id="%s"' % autoid
        newid = u'id="%s_hdn"' % autoid

        hdnhtml = u'<input id="%s" type="hidden" value="%s" name="%s"/>' % (
            autoid, data, name)
        str1 = force_unicode(
            force_unicode(self.field).replace(oldname, newname))
        str1 = str1.replace(oldid, newid)

        s = force_unicode(str1) + hdnhtml
        return mark_safe(s)

    def errors(self):
        return mark_safe(self.field.errors.as_ul())


def normalize_fieldsets(fieldsets):
    """
    Make sure the keys in fieldset dictionaries are strings. Returns the
    normalized data.
    """
    result = []
    for name, options in fieldsets:
        result.append((name, normalize_dictionary(options)))
    return result


def normalize_dictionary(data_dict):
    """
    Converts all the keys in "data_dict" to strings. The keys must be
    convertible using str().
    """
    for key, value in data_dict.items():
        if not isinstance(key, str):
            del data_dict[key]
            data_dict[str(key)] = value
    return data_dict

form_admin = ViewAdmin()
