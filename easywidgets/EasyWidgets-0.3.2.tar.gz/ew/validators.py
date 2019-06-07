from __future__ import absolute_import
from __future__ import unicode_literals
from datetime import time
from dateutil.parser import parse

from formencode import validators as fev
import six
from six.moves import map

class Currency(fev.Number):
    symbol='$'
    format='$%.2f'
    store_factor=100

    def _to_python(self, value, state):
        value = value.strip(' \r\n\t' + self.symbol)
        return int(fev.Number._to_python(self, value, state) * self.store_factor)

    def from_python(self, value, state):
        if isinstance(value, six.string_types):
            return value
        elif isinstance(value, six.integer_types + (float,)):
            value = float(value) / self.store_factor
            return self.format  % value

class TimeConverter(fev.TimeConverter):
    
    def _to_python(self, value, state):
        value = super(TimeConverter, self)._to_python(value, state)
        if value is not None:
            value = time(*value)
        return value

class DateConverter(fev.DateConverter):
    
    def to_python(self, value, state):
        try:
            return parse(value).date()
        except ValueError:
            return super(DateConverter, self).to_python(value, state)

class OneOf(fev.FancyValidator):

    messages = {
        'invalid': 'Invalid Value',
        'notIn':'Value must be one of: %(items)s (not %(value)r)',
        }
    hideList = False

    def __init__(self, options):
        self.options = options

    def validate_python(self, value, state):
        if callable(self.options):
            options = self.options()
        else:
            options = self.options
        if not value in options:
            if self.hideList:
                raise fev.Invalid(self.message('invalid', state),
                                  value, state)
            else:
                items = '; '.join(map(str, options))
                raise fev.Invalid(self.message('notIn', state,
                                               items=items,
                                               value=value),
                                  value, state)

class UnicodeString(fev.UnicodeString):

    def from_python(self, value, state):
        # before py3 conversions, if value was None, this function would raise an exception
        #       TypeError: decoding Unicode is not supported
        # and FieldWidget.prepare_context trapped all errors, so it wouldn't change its value
        # so we preserve that resulting behavior (None stays None)
        if value is None:
            return None
        str_version = super(UnicodeString, self).from_python(value, state)
        return six.ensure_text(str_version, self.outputEncoding or 'utf-8')

class Int(fev.Int):
    def from_python(self, value, state):
        return str(value)
