# -*- coding: utf-8 -*-

'''
Created on 2017-05-09
@author: linkeddt.com
'''

from __future__ import unicode_literals

import copy
import datetime
from decimal import Decimal, DecimalException

from django.core import validators
from django.core.exceptions import ValidationError
# from django.forms.fields import Field
from django.forms.utils import from_current_timezone, to_current_timezone
# from django.utils.translation import ugettext as _, ungettext_lazy
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
from django.utils.encoding import smart_text, force_text, force_str
from django.utils import formats
from django.utils import six

import xlrd


__all__ = ('ExcelField', 'CharField', 'IntegerField', 'FloatField',
           'DecimalField', 'DateTimeField', 'ChoiceField', 'HexField')


class ExcelField(object):
    default_validators = []  # Default set of validators
    # Add an 'invalid' entry to default_error_message if you want a specific
    # field error message not raised by the field validators.
    default_error_messages = {
        'required': _('This field is required.'),
    }
    empty_values = list(validators.EMPTY_VALUES)

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, required=True, label=None, initial=None,
                 help_text='', error_messages=None, show_hidden_initial=False,
                 validators=[], index=0):
        # required -- Boolean that specifies whether the field is required.
        #             True by default.
        # widget -- A Widget class, or instance of a Widget class, that should
        #           be used for this Field when displaying it. Each Field has a
        #           default Widget that it'll use if you don't specify this. In
        #           most cases, the default widget is TextInput.
        # label -- A verbose name for this field, for use in displaying this
        #          field in a form. By default, Django will use a "pretty"
        #          version of the form field name, if the Field is part of a
        #          Form.
        # initial -- A value to use in this Field's initial display. This value
        #            is *not* used as a fallback if data isn't given.
        # help_text -- An optional string to use as "help text" for this Field.
        # error_messages -- An optional dictionary to override the default
        #                   messages that the field will raise.
        # show_hidden_initial -- Boolean that specifies if it is needed to render a
        #                        hidden widget with initial value after widget.
        # validators -- List of additional validators to use
        # localize -- Boolean that specifies if the field should be localized.
        self.required, self.label, self.initial = required, label, initial
        self.show_hidden_initial = show_hidden_initial
        self.help_text = help_text
        self.index = index

        # Increase the creation counter, and save our local copy.
        self.creation_counter = ExcelField.creation_counter
        ExcelField.creation_counter += 1

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        self.validators = self.default_validators + validators
        super(ExcelField, self).__init__()

    def prepare_value(self, value):
        return value

    def to_python(self, value):
        return value

    def validate(self, value):
        if value in self.empty_values and self.required:
            raise ValidationError(
                self.error_messages['required'], code='required')

    def run_validators(self, value):
        if value in self.empty_values:
            return
        errors = []
        for v in self.validators:
            try:
                v(value)
            except ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)
        if errors:
            raise ValidationError(errors)

    def clean(self, value):
        """
        Validates the given value and returns its "cleaned" value as an
        appropriate Python object.

        Raises ValidationError for any errors.
        """
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value

    def bound_data(self, data, initial):
        """
        Return the value that should be shown for this field on render of a
        bound form, given the submitted POST data for the field and the initial
        data, if any.

        For most fields, this will simply be data; FileFields need to handle it
        a bit differently.
        """
        return data

    def _has_changed(self, initial, data):
        """
        Return True if data differs from initial.
        """
        # For purposes of seeing whether something has changed, None is
        # the same as an empty string, if the data or initial value we get
        # is None, replace it w/ ''.
        initial_value = initial if initial is not None else ''
        try:
            data = self.to_python(data)
            if hasattr(self, '_coerce'):
                data = self._coerce(data)
        except ValidationError:
            return True
        data_value = data if data is not None else ''
        return initial_value != data_value

    def __deepcopy__(self, memo):
        result = copy.copy(self)
        memo[id(self)] = result
        result.validators = self.validators[:]
        return result


class CharField(ExcelField):

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        super(CharField, self).__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(
                validators.MinLengthValidator(int(min_length)))
        if max_length is not None:
            self.validators.append(
                validators.MaxLengthValidator(int(max_length)))

    def to_python(self, value):
        "Returns a Unicode object."
        if value in self.empty_values:
            return ''
        return smart_text(value)

    def widget_attrs(self, widget):
        attrs = super(CharField, self).widget_attrs(widget)
        if self.max_length is not None:
            # The HTML attribute is maxlength, not max_length.
            attrs.update({'maxlength': str(self.max_length)})
        return attrs


class IntegerField(ExcelField):
    default_error_messages = {
        'invalid': _('Enter a whole number.'),
    }

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        self.max_value, self.min_value = max_value, min_value
        super(IntegerField, self).__init__(*args, **kwargs)

        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

    def to_python(self, value):
        """
        Validates that int() can be called on the input. Returns the result
        of int(). Returns None for empty values.
        """
        value = super(IntegerField, self).to_python(value)
        if value in self.empty_values:
            return None
        try:
            if isinstance(value, float):
                value = int(value)
            else:
                value = int(str(value))
        except (ValueError, TypeError):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')
        return value


class HexField(ExcelField):
    default_error_messages = {
        'invalid': '闈�16杩涘埗鏁�.',
    }

    def __init__(self, *args, **kwargs):
        super(HexField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(HexField, self).to_python(value)
        if value in self.empty_values:
            return None
        try:
            if isinstance(value, float):
                return int(str(int(value)), 16)
            return int(value, 16)
        except (ValueError, TypeError):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')
        return value


class FloatField(IntegerField):
    default_error_messages = {
        'invalid': _('Enter a number.'),
    }

    def to_python(self, value):
        """
        Validates that float() can be called on the input. Returns the result
        of float(). Returns None for empty values.
        """
        value = super(IntegerField, self).to_python(value)
        if value in self.empty_values:
            return None
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')
        return value

    def validate(self, value):
        super(FloatField, self).validate(value)

        # Check for NaN (which is the only thing not equal to itself) and +/-
        # infinity
        if value != value or value in (Decimal('Inf'), Decimal('-Inf')):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')

        return value


class DecimalField(IntegerField):
    default_error_messages = {
        'invalid': _('Enter a number.'),
        'max_digits': ungettext_lazy(
            'Ensure that there are no more than %(max)s digit in total.',
            'Ensure that there are no more than %(max)s digits in total.',
            'max'),
        'max_decimal_places': ungettext_lazy(
            'Ensure that there are no more than %(max)s decimal place.',
            'Ensure that there are no more than %(max)s decimal places.',
            'max'),
        'max_whole_digits': ungettext_lazy(
            'Ensure that there are no more than %(max)s digit before the decimal point.',
            'Ensure that there are no more than %(max)s digits before the decimal point.',
            'max'),
    }

    def __init__(self, max_value=None, min_value=None, max_digits=None, decimal_places=None, *args, **kwargs):
        self.max_digits, self.decimal_places = max_digits, decimal_places
        super(DecimalField, self).__init__(
            max_value, min_value, *args, **kwargs)

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """
        if value in self.empty_values:
            return None
        value = smart_text(value).strip()
        try:
            value = Decimal(value)
        except DecimalException:
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')
        return value

    def validate(self, value):
        super(DecimalField, self).validate(value)
        if value in self.empty_values:
            return
        # Check for NaN, Inf and -Inf values. We can't compare directly for NaN,
        # since it is never equal to itself. However, NaN is the only value that
        # isn't equal to itself, so we can use this to identify NaN
        if value != value or value == Decimal("Inf") or value == Decimal("-Inf"):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')
        sign, digittuple, exponent = value.as_tuple()
        decimals = abs(exponent)
        # digittuple doesn't include any leading zeros.
        digits = len(digittuple)
        if decimals > digits:
            # We have leading zeros up to or past the decimal point.  Count
            # everything past the decimal point as a digit.  We do not count
            # 0 before the decimal point as a digit since that would mean
            # we would not allow max_digits = decimal_places.
            digits = decimals
        whole_digits = digits - decimals

        if self.max_digits is not None and digits > self.max_digits:
            raise ValidationError(
                self.error_messages['max_digits'],
                code='max_digits',
                params={'max': self.max_digits},
            )
        if self.decimal_places is not None and decimals > self.decimal_places:
            raise ValidationError(
                self.error_messages['max_decimal_places'],
                code='max_decimal_places',
                params={'max': self.decimal_places},
            )
        if (self.max_digits is not None and self.decimal_places is not None
                and whole_digits > (self.max_digits - self.decimal_places)):
            raise ValidationError(
                self.error_messages['max_whole_digits'],
                code='max_whole_digits',
                params={'max': (self.max_digits - self.decimal_places)},
            )
        return value


class BaseTemporalField(ExcelField):

    def __init__(self, input_formats=None, *args, **kwargs):
        super(BaseTemporalField, self).__init__(*args, **kwargs)
        if input_formats is not None:
            self.input_formats = input_formats

    def to_python(self, value):
        # Try to coerce the value to unicode.
        unicode_value = force_text(value, strings_only=True)
        if isinstance(unicode_value, six.text_type):
            value = unicode_value.strip()
        # If unicode, try to strptime against each input format.
        if isinstance(value, six.text_type):
            for format in self.input_formats:
                try:
                    return self.strptime(value, format)
                except (ValueError, TypeError):
                    continue
        raise ValidationError(self.error_messages['invalid'], code='invalid')

    def strptime(self, value, format):
        raise NotImplementedError('Subclasses must define this method.')


class DateTimeField(BaseTemporalField):
    input_formats = formats.get_format_lazy('DATETIME_INPUT_FORMATS')
    default_error_messages = {
        'invalid': _('Enter a valid date/time.'),
    }

    def prepare_value(self, value):
        if isinstance(value, datetime.datetime):
            value = to_current_timezone(value)
        return value

    def to_python(self, value):
        """
        Validates that the input can be converted to a datetime. Returns a
        Python datetime.datetime object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return from_current_timezone(value)
        if isinstance(value, datetime.date):
            result = datetime.datetime(value.year, value.month, value.day)
            return from_current_timezone(result)
        if isinstance(value, list):
            # Input comes from a SplitDateTimeWidget, for example. So, it's two
            # components: date and time.
            if len(value) != 2:
                raise ValidationError(
                    self.error_messages['invalid'], code='invalid')
            if value[0] in self.empty_values and value[1] in self.empty_values:
                return None
            value = '%s %s' % tuple(value)
        if isinstance(value, float):
            return xlrd.xldate.xldate_as_datetime(value, 0)

        result = super(DateTimeField, self).to_python(value)
        return from_current_timezone(result)

    def strptime(self, value, format):
        return datetime.datetime.strptime(force_str(value), format)


class ChoiceField(ExcelField):
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
    }

    def __init__(self, choices=(), required=True, label=None,
                 initial=None, help_text='', *args, **kwargs):
        super(ChoiceField, self).__init__(required=required, label=label,
                                          initial=initial, help_text=help_text, *args, **kwargs)
        self.choices = choices

    def __deepcopy__(self, memo):
        result = super(ChoiceField, self).__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        self._choices = list(value)

    choices = property(_get_choices, _set_choices)

    def to_python(self, value):
        "Returns a Unicode object."
        if value in self.empty_values:
            return None

        for k, v in self._choices:
            if v == value:
                return smart_text(k)

    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        super(ChoiceField, self).validate(value)
        if value and not self.valid_value(value):
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )

    def valid_value(self, value):
        "Check to see if the provided value is a valid choice"
        text_value = force_text(value)
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == force_text(k2):
                        return True
            else:
                if value == k or text_value == force_text(k):
                    return True
        return False
