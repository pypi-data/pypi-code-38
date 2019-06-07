from enum import Enum, auto
import dateutil
import re
from . import exceptions


class FieldException(exceptions.CommonException):

    def __init__(self, message, cause=None):
        super().__init__(message, cause)


class Field:

    class Do(Enum):
        SKIP = auto(),
        DEFAULT = auto(),
        RAISE = auto()

    def __init__(self, missing=Do.RAISE, error=Do.RAISE, default=None):
        self._missing = missing
        self._error = error
        self._default = default

    def getDefault(self):
        return self._default

    def getOnMissing(self):
        return self._missing

    def getOnError(self):
        return self._error

    def clean(self, value):
        raise NotImplementedError()

    def cleanAndAdd(self, present, value, add):
        if present:
            try:
                value = self.clean(value)
            except FieldException as e:
                if self._error == Field.Do.RAISE:
                    raise e
                elif self._error == Field.Do.DEFAULT:
                    add(self._default)
            else:
                add(value)
        else:
            if self._missing == Field.Do.RAISE:
                raise FieldException("Required but missing")
            elif self._missing == Field.Do.DEFAULT:
                add(self._default)


class TypeField(Field):

    def __init__(self, type, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(missing=missing, error=error, default=default)
        self._type = type

    def getType(self):
        return self._type

    @staticmethod
    def formatTypeConstraint(typeConstraint):
        if isinstance(typeConstraint, type):
            return typeConstraint.__name__
        elif isinstance(typeConstraint, (tuple, list)):
            return " or ".join(map(lambda t: t.__name__, typeConstraint))
        else:
            return "<error type>"

    def clean(self, value):
        if not isinstance(value, self._type):
            raise FieldException("Expected type {}".format(TypeField.formatTypeConstraint(self._type)))
        return value


class ScalarField(TypeField):

    def __init__(self, type, min=None, max=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(type, missing=missing, error=error, default=default)
        self._min = min
        self._max = max

    def getMin(self):
        return self._min

    def getMax(self):
        return self._max

    def clean(self, value):
        value = super().clean(value)
        if self._min is not None and value < self._min:
            raise FieldException("Value must be >= {}".format(self._min))
        if self._max is not None and value > self._max:
            raise FieldException("Value must be <= {}".format(self._max))
        return value


class IntField(ScalarField):

    def __init__(self, min=None, max=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(int, min=min, max=max, missing=missing, error=error, default=default)


class FloatField(ScalarField):

    def __init__(self, min=None, max=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__((int, float), min=min, max=max, missing=missing, error=error, default=default)


class BoolField(TypeField):

    def __init__(self, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(bool, missing=missing, error=error, default=default)


class StringField(TypeField):

    def __init__(self, minLength=None, maxLength=None, regex=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(str, missing=missing, error=error, default=default)
        self._minLength = minLength
        self._maxLength = maxLength
        self._regex = re.compile(regex) if regex is not None else None

    def getMinLength(self):
        return self._minLength

    def getMaxLength(self):
        return self._maxLength

    def getRegex(self):
        return self._regex

    def clean(self, value):
        value = super().clean(value)
        if self._minLength is not None and len(value) < self._minLength:
            raise FieldException('String must be at least {} characters long'.format(self._minLength))
        if self._maxLength is not None and len(value) > self._maxLength:
            raise FieldException('String cannot be longer than {} characters'.format(self._maxLength))
        if self._regex is not None and not self._regex.match(value):
            raise FieldException('String does not match regex "{}"'.format(self._regex))
        return value


class ListField(TypeField):

    def __init__(self, minLength=None, maxLength=None, fields=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(list, missing=missing, error=error, default=default)
        self._minLength = minLength
        self._maxLength = maxLength
        self._fields = fields

    def getMinLength(self):
        return self._minLength

    def getMaxLength(self):
        return self._maxLength

    def getFields(self):
        return self._fields

    def clean(self, value):
        value = super().clean(value)
        if self._minLength is not None and len(value) < self._minLength:
            raise FieldException('List length must be >= {}'.format(self._minLength))
        if self._maxLength is not None and len(value) > self._maxLength:
            raise FieldException('List length must be <= {}'.format(self._maxLength))
        if self._fields is not None:
            if isinstance(self._fields, list):
                fields = self._fields
            elif isinstance(self._fields, Field):
                fields = [self._fields] * len(value)
            else:
                raise TypeError("Bad type fields type")
            items = []
            for i, item in enumerate(value):
                if fields[i] is not None:
                    try:
                        fields[i].cleanAndAdd(True, item, items.append)
                    except FieldException as e:
                        raise FieldException("Field exception on item {}".format(i), e)
                else:
                    items.append(item)
            value = items
        return value

    @staticmethod
    def byLength(length, fields=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        return ListField(length, length, fields, missing, error, default)

    @staticmethod
    def byFields(fields=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        return ListField.byLength(len(fields), fields, missing, error, default)


class TimeField(TypeField):

    def __init__(self, min=None, max=None, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(str, missing=missing, error=error, default=default)
        self._min = min
        self._max = max

    def getMin(self):
        return self._min

    def getMax(self):
        return self._max

    def clean(self, value):
        try:
            value = dateutil.parser.parse(value)
        except ValueError as e:
            raise FieldException("Invalid datetime: {}".format(str(e)))
        except OverflowError as e:
            raise FieldException("Overflow error")
        if self._min is not None and value < self._min:
            raise FieldException("Value must be >= {}".format(self._min))
        if self._max is not None and value > self._max:
            raise FieldException("Value must be <= {}".format(self._max))
        return value


class DictField(TypeField):

    def __init__(self, fields, missing=Field.Do.RAISE, error=Field.Do.RAISE, default=None):
        super().__init__(dict, missing=missing, error=error, default=default)
        self._fields = fields

    def getFields(self):
        return self._fields

    def clean(self, value):
        value = super().clean(value)
        if self._fields is not None:
            dictionary = {}
            if isinstance(self._fields, Field):
                for key, item in value.items():
                    try:
                        def add(v):
                            dictionary[key] = v
                        self._fields.cleanAndAdd(True, item, add)
                    except FieldException as e:
                        raise FieldException('Field exception on item "{}"'.format(key), e)
            elif isinstance(self._fields, dict):
                for key, item in self._fields.items():
                    try:
                        def add(v):
                            dictionary[key] = v
                        present = key in value
                        self._fields[key].cleanAndAdd(present, value[key] if present else None, add)
                    except FieldException as e:
                        raise FieldException('Field exception on item "{}"'.format(key), e)
                unexpected = set(value.keys()) - set(self._fields.keys())
                if len(unexpected) > 0:
                    raise FieldException('Unexpected fields {}'.format(unexpected))
            else:
                raise TypeError("Bad fields type")
            value = dictionary
        return value
