import abc
import re


class LanguageType(abc.ABC):
    name = None
    default_value = None

    def __hash__(self):
        return hash(self.name)

    @abc.abstractmethod
    def check(self, obj):
        pass

    def pointer(self):
        return PointerType(self)

    def autocast(self, value):
        return value

    def __str__(self):
        return self.name

    def matches(self, other):
        return hash(self) == hash(other) or other.matches(self)

class FunctionType(LanguageType):
    def __init__(self, arg_types, return_type):
        self.arg_types = list(arg_types)
        self.return_type = return_type

        assert all(isinstance(x, LanguageType) for x in self.arg_types)
        assert isinstance(self.return_type, LanguageType)

    def __str__(self):
        return '{}({})'.format(str(self.return_type), ','.join(str(x) for x in self.arg_types))

    def check(self, obj):
        return (
            obj.return_kind.matches(self.return_type)
            and len(self.arg_types) == len(obj.arg_typenames)
            and all(
                a.matches(b)
                for (a, _), b in zip(obj.arg_typenames, self.arg_types)
            )
        )

class PointerType(LanguageType):
    name = 'pointer'
    default_value = None

    def __init__(self, deref_type):
        self.deref_type = deref_type

    def __str__(self):
        return str(self.deref_type) + '*'

    def __hash__(self):
        return hash(hash(self.deref_type) + hash('_ptr'))

    def check(self, obj):
        from . import vm
        return obj is None or (isinstance(obj, vm.FrePointer) and obj.kind.matches(self.deref_type))

class ArrayType(LanguageType):
    name = 'array'
    default_value = ()

    def autocast(self, value):
        if not isinstance(value, list):
            return list(value)

        return value

    def __init__(self, element_type):
        self.element_type = element_type

    def __str__(self):
        return str(self.element_type) + '%'

    def __hash__(self):
        return hash(hash(self.element_type) + hash('[]'))

    def check(self, obj):
        return isinstance(obj, list) and all(self.element_type.check(o) for o in obj)

class VoidType(LanguageType):
    name = 'void'
    default_value = None

    def check(self, obj):
        return obj is None

class IntType(LanguageType):
    name = 'int'
    default_value = 0

    def check(self, obj):
        return isinstance(obj, int) or obj in (True, False)

    def autocast(self, value):
        return int(value)

class FloatType(LanguageType):
    name = 'float'
    default_value = 0.

    def check(self, obj):
        return isinstance(obj, int) or isinstance(obj, float)

    def autocast(self, value):
        return float(value)

class StringType(LanguageType):
    name = 'string'
    default_value = ''

    def check(self, obj):
        return isinstance(obj, bytes) or isinstance(obj, str)

    def autocast(self, value):
        return str(value)
class AnyType(LanguageType):
    name = 'any'
    default_value = None

    def check(self, obj):
        return True

    def matches(self, other):
        return True


##=======================##


class LanguageSpecs(object):
    keywords = ()
    types = ()
    type_modifiers = ''
    identifier_modifiers = ''
    values = {}

    def find_type(self, name):
        try:
            return next(x for x in self.types if x.name == name)

        except StopIteration:
            raise ValueError("Type '{}' not found!".format(name))

class FreSpecs(LanguageSpecs):
    keywords = ('func', 'if', 'else', 'while', 'return', 'continue', 'break', 'set')
    types = (VoidType, IntType, FloatType, StringType, AnyType)
    type_modifiers = '*%'
    identifier_modifiers = '@*'
    values = {'none': None, 'null': None, 'true': True, 'false': False}