import abc
import datetime

from . import TowelValueError


class Field(abc.ABC):

    def __init__(self, value=None, **kwargs):
        self.value = value

    @classmethod
    @abc.abstractmethod
    def sql(cls):
        pass

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        if isinstance(new, self.PYTHON_TYPE) or new is None:
            self._value = new
        else:
            raise TowelValueError(f"{new} is not instance of {self.PYTHON_TYPE}")

    @property
    @abc.abstractmethod
    def SQL_TYPE(self):
        pass

    @property
    @abc.abstractmethod
    def PYTHON_TYPE(self):
        pass


class Integer(Field):
    SQL_TYPE = "int"
    PYTHON_TYPE = int

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)

    @Field.value.setter
    def value(self, new):
        if isinstance(new, self.PYTHON_TYPE) or new is None:
            self._value = new
        else:
            raise TowelValueError(f"{new} is not instance of {self.PYTHON_TYPE}")

    @classmethod
    def sql(cls):
        return cls.SQL_TYPE


class Real(Field):
    SQL_TYPE = "real"
    PYTHON_TYPE = float

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)

    @Field.value.setter
    def value(self, new):
        if isinstance(new, self.PYTHON_TYPE) or new is None:
            self._value = new
        else:
            raise TowelValueError(f"{new} is not instance of {self.PYTHON_TYPE}")

    @classmethod
    def sql(cls):
        return cls.SQL_TYPE


class Date(Field):
    SQL_TYPE = "date"
    PYTHON_TYPE = datetime.date

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)

    @Field.value.setter
    def value(self, new):
        if isinstance(new, self.PYTHON_TYPE) or new is None:
            self._value = new
        else:
            raise TowelValueError(f"{new} is not instance of {self.PYTHON_TYPE}")

    @classmethod
    def sql(cls):
        return cls.SQL_TYPE


class VarChar(Field):
    SQL_TYPE = "varchar"
    DEFAULT_LENGTH = 50
    PYTHON_TYPE = str

    def __init__(self, value, length, **kwargs):
        super().__init__(value, **kwargs)
        self.DEFAULT_LENGTH = length

        self.sql = self._sql_placeholder

    @Field.value.setter
    def value(self, new):
        if isinstance(new, self.PYTHON_TYPE) or new is None:
            self._value = new
        else:
            raise TowelValueError(f"{new} is not instance of {self.PYTHON_TYPE}")

    @classmethod
    def sql(cls):
        return f"{cls.SQL_TYPE}({cls.DEFAULT_LENGTH})"

    def _sql_placeholder(self):
        return f"{self.SQL_TYPE}({self.DEFAULT_LENGTH})"


class ForeignKey:
    field = Integer

    SQL_TYPE = field.SQL_TYPE
    PYTHON_TYPE = field.PYTHON_TYPE

    def __init__(self, table, field=None, **kwargs):
        self.table = table
        self.field = (field or self.field)(None)

    @property
    def value(self):
        return self.field.value

    @value.setter
    def value(self, new):
        self.field.value = new

    def sql(self):
        return self.field.sql() + " references " + self.table.tablename() + "(id)"


class Column:
    field_inst = None
    column_name = None

    def __init__(self, field_class, value=None, **attrs):
        if not issubclass(field_class, ForeignKey):
            if isinstance(field_class, type) and not issubclass(field_class, Field):
                raise TowelValueError(f'{field_class} is not instance of {Field.__name__}')

        self.field_class = field_class
        self._attrs = attrs

        if issubclass(field_class, ForeignKey):
            self.field_inst = ForeignKey(**attrs)
            self.foreign_entity = attrs.get("table")
            self.entity_name = attrs.get("entity_name", "foreign_entity")
        else:
            self.field_inst = self.field_class(value, **self._attrs)

    def __str__(self):
        return str(self.field_inst)

    def create_duplicate(self):
        cls = self.__class__(self.field_class, **self._attrs)
        cls.column_name = self.column_name

        return cls

    @property
    def value(self):
        return self.field_inst.value

    @value.setter
    def value(self, new):
        try:
            self.field_inst.value = new
        except TowelValueError:
            raise TowelValueError(f"Value {new} is illegal for column of type {self.field_inst.__class__.__name__}")

    @property
    def sql(self):
        return ' '.join((self.column_name, self.field_inst.sql()))
