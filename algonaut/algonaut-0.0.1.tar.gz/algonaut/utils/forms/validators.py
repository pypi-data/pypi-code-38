import re
import uuid
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from algonaut.settings import settings as settings

class ToLower:

    def __call__(self, name, value, form):
        return [], value.lower(), False

class JSON:

    def __call__(self, name, value, form):
        try:
            d = json.loads(value)
            return [], d, False
        except:
            return [form.t('form.json.invalid')], None, True

class Regex:

    def __init__(self, regex):
        self.regex = re.compile(regex)

    def __call__(self, name, value, form):
        if not self.regex.match(value):
            return [form.t('form.regex-does-not-match')], None, True

class Optional:

    def __init__(self, default=None, validate_default=False):
        self.default = default
        self.validate_default = validate_default

    def __call__(self, name, value, form):
        if value is None or (isinstance(value, (str, bytes)) and not value):
            return [], self.default, not self.validate_default

class Required:

    def __call__(self, name, value, form):
        if value is None:
            return [form.t('form.is-required')], None, True

class EMail:

    regex = re.compile(r'^[^\@]+\@[^\@]+\.[\w]+$')

    def __call__(self, name, value, form):
        if not value or not self.regex.match(value):
            return [form.t('form.invalid-email')], None, True


class Length:

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, name, value, form):
        if self.min is not None and len(value) < self.min or \
           self.max is not None and len(value) > self.max:
            return [form.t('form.invalid-length', min=self.min, max=self.max)], None, True

class Type:

    type = object

    def __init__(self, convert=False):
        self.convert=convert

    def __call__(self, name, value, form):
        err = [form.t('form.not-of-type', type=self.type.__name__.lower())], None, True
        if self.convert:
            try:
                value = self.type(value)
            except ValueError:
                return err
        if not isinstance(value, self.type):
            return err
        return [], value, False

class String(Type):

    type = str

class Boolean(Type):

    type = bool

class Integer(Type):

    type = int

    def __init__(self, *args, min=None, max=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min = min
        self.max = max

    def __call__(self, name, value, form):
        result = super().__call__(name, value, form)
        if result:
            errors, value, stop = result
            if errors:
                return result
        if self.min is not None and value < self.min or \
           self.max is not None and value > self.max:
           return [form.t('form.integer-out-of-bounds',
                          min=self.min if self.min is not None else '',
                          max=self.max if self.max is not None else '')], None, True

class UUID:

    def __call__(self, name, value, form):
        try:
            value = uuid.UUID(value)
        except ValueError:
            return [form.t('form.not-a-uuid')], None, True
        return [], value, False

class DateTime:

    def __init__(self, format='%Y-%m-%dT%H:%M:%SZ'):
        self.format = format

    def __call__(self, name, value, form):
        try:
            value = datetime.datetime.strptime(value, self.format)
        except ValueError:
            return [form.t('form.datetime-not-well-formatted', format=self.format)], None, True

class Choices:

    def __init__(self, choices):
        self.choices = choices

    def __call__(self, name, value, form):
        if not value in self.choices:
            return [form.t('form.not-a-valid-choice', choices=self.choices)], None, True

class Equal:

    def __init__(self, value, message=None):
        self.value = value
        self.message = message or 'form.not-equal'

    def __call__(self, name, value, form):
        if value != self.value:
            return [form.t(self.message)], None, True
