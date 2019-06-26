# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Form Widgets
"""

from __future__ import unicode_literals, absolute_import, division

import json
import datetime
import decimal

import six

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags, HTML

from tailbone.forms.types import ProductQuantity


class ReadonlyWidget(dfwidget.HiddenWidget):

    readonly = True

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        # TODO: is this hacky?
        text = kw.get('text')
        if not text:
            text = field.parent.tailbone_form.render_field_value(field.name)
        return HTML.tag('span', text) + tags.hidden(field.name, value=cstruct, id=field.oid)


class NumberInputWidget(dfwidget.TextInputWidget):
    template = 'numberinput'
    autocomplete = 'off'


class PercentInputWidget(dfwidget.TextInputWidget):
    """
    Custom text input widget, used for "percent" type fields.  This widget
    assumes that the underlying storage for the value is a "traditional"
    percent value, e.g. ``0.36135`` - but the UI should represent this as a
    "human-friendly" value, e.g. ``36.135 %``.
    """
    template = 'percentinput'
    autocomplete = 'off'

    def serialize(self, field, cstruct, **kw):
        if cstruct not in (colander.null, None):
            # convert "traditional" value to "human-friendly"
            value = decimal.Decimal(cstruct) * 100
            value = value.quantize(decimal.Decimal('0.001'))
            cstruct = six.text_type(value)
        return super(PercentInputWidget, self).serialize(field, cstruct, **kw)

    def deserialize(self, field, pstruct):
        pstruct = super(PercentInputWidget, self).deserialize(field, pstruct)
        if pstruct is colander.null:
            return colander.null
        # convert "human-friendly" value to "traditional"
        try:
            value = decimal.Decimal(pstruct)
        except decimal.InvalidOperation:
            raise colander.Invalid(field.schema, "Invalid decimal string: {}".format(pstruct))
        value = value.quantize(decimal.Decimal('0.00001'))
        value /= 100
        return six.text_type(value)


class CasesUnitsWidget(dfwidget.Widget):
    """
    Widget for collecting case and/or unit quantities.  Most useful when you
    need to ensure user provides cases *or* units but not both.
    """
    template = 'cases_units'
    amount_required = False
    one_amount_only = False

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        kw['cases'] = cstruct['cases'] or ''
        kw['units'] = cstruct['units'] or ''
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null

        schema = ProductQuantity()
        try:
            validated = schema.deserialize(pstruct)
        except colander.Invalid as exc:
            raise colander.Invalid(field.schema, "Invalid pstruct: %s" % exc)

        if self.amount_required and not (validated['cases'] or validated['units']):
            raise colander.Invalid(field.schema, "Must provide case or unit amount",
                                   value=validated)

        if self.amount_required and self.one_amount_only and validated['cases'] and validated['units']:
            raise colander.Invalid(field.schema, "Must provide case *or* unit amount, "
                                   "but *not* both", value=validated)

        return validated


class DynamicCheckboxWidget(dfwidget.CheckboxWidget):
    """
    This checkbox widget can be "dynamic" in the sense that form logic can
    control its value and state.
    """
    template = 'checkbox_dynamic'


class PlainSelectWidget(dfwidget.SelectWidget):
    template = 'select_plain'


class CustomSelectWidget(dfwidget.SelectWidget):
    """
    This widget is mostly for convenience.  You can set extra kwargs for the
    :meth:`serialize()` method, e.g.::

       widget.set_template_values(foo='bar')
    """

    def set_template_values(self, **kw):
        if not hasattr(self, 'extra_template_values'):
            self.extra_template_values = {}
        self.extra_template_values.update(kw)

    def get_template_values(self, field, cstruct, kw):
        values = super(CustomSelectWidget, self).get_template_values(field, cstruct, kw)
        if hasattr(self, 'extra_template_values'):
            values.update(self.extra_template_values)
        return values


class DynamicSelectWidget(CustomSelectWidget):
    """
    This is a "normal" select widget, but instead of (or in addition to) its
    values being set when constructed, they must be assigned dynamically in
    real-time, e.g. based on other user selections.

    Really all this widget "does" is render some Vue.js-compatible HTML, but
    the page which contains the widget is ultimately responsible for wiring up
    the logic for things to work right.
    """
    template = 'select_dynamic'


class JQuerySelectWidget(dfwidget.SelectWidget):
    template = 'select_jquery'


class PlainDateWidget(dfwidget.DateInputWidget):
    template = 'date_plain'


class JQueryDateWidget(dfwidget.DateInputWidget):
    """
    Uses the jQuery datepicker UI widget, instead of whatever it is deform uses
    by default.
    """
    template = 'date_jquery'
    type_name = 'text'
    requirements = None

    default_options = (
        ('changeMonth', True),
        ('changeYear', True),
        ('dateFormat', 'yy-mm-dd'),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        options = dict(
            kw.get('options') or self.options or self.default_options
        )
        options.update(kw.get('extra_options', {}))
        kw.setdefault('options_json', json.dumps(options))
        kw.setdefault('selected_callback', None)
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)


class JQueryTimeWidget(dfwidget.TimeInputWidget):
    """
    Uses the jQuery datepicker UI widget, instead of whatever it is deform uses
    by default.
    """
    template = 'time_jquery'
    type_name = 'text'
    requirements = None
    default_options = (
        ('showPeriod', True),
    )


class JQueryAutocompleteWidget(dfwidget.AutocompleteInputWidget):
    """ 
    Uses the jQuery autocomplete plugin, instead of whatever it is deform uses
    by default.
    """
    template = 'autocomplete_jquery'
    requirements = None
    field_display = ""
    service_url = None
    cleared_callback = None
    selected_callback = None

    default_options = (
        ('autoFocus', True),
    )
    options = None

    def serialize(self, field, cstruct, **kw):
        if 'delay' in kw or getattr(self, 'delay', None):
            raise ValueError(
                'AutocompleteWidget does not support *delay* parameter '
                'any longer.'
            )
        if cstruct in (colander.null, None):
            cstruct = ''
        self.values = self.values or []
        readonly = kw.get('readonly', self.readonly)

        options = dict(
            kw.get('options') or self.options or self.default_options
        )
        options['source'] = self.service_url

        kw['options'] = json.dumps(options)
        kw['field_display'] = self.field_display
        kw['cleared_callback'] = self.cleared_callback
        kw.setdefault('selected_callback', self.selected_callback)
        tmpl_values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **tmpl_values)
