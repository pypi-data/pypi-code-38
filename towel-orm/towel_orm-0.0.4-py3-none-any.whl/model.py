from . import TowelAttributeError, Column, ObjectManager, Integer, ForeignKey
from collections import namedtuple


class MetaModel(type):

    def __new__(cls, name, bases, body, *args, **kwargs):
        if_db_implemented = any("db" in dir(base) for base in bases) or "db" in body

        for column_name, instance in body.items():
            if isinstance(instance, Column):
                instance.column_name = column_name

        if name != "AbstractBaseModel":
            if not if_db_implemented:
                raise TowelAttributeError("DB was not defined")

            if not body.get("__tablename__"):
                body["__tablename__"] = name.lower()

            foreigns = [col for _, col in body.items() if
                        isinstance(col, Column) and issubclass(col.field_class, ForeignKey)]
            if any(foreigns):
                for col in foreigns:
                    body[col.entity_name] = col.foreign_entity

        return super().__new__(cls, name, bases, body)


class AbstractBaseModel(metaclass=MetaModel):
    __tablename__ = None
    _objects = ObjectManager
    id = Column(Integer)

    def __init__(self, **kwargs):
        kwargs["id"] = kwargs.get("id", None)
        for key in kwargs:
            if key not in dir(self):
                raise TowelAttributeError(f'"{key} is not defined in {self.__class__.__name__}"')
            else:
                inst = getattr(self, key)
                if isinstance(inst, Column):
                    column = inst.create_duplicate()
                    column.value = kwargs.get(key)
                    setattr(self, key, column)

        if isinstance(self._objects, type):
            self._objects = self._objects(self)
        else:
            self._objects = self._objects.__class__(self)
        self.objects = self._objects_placeholder
        self.columns = self._columns_placeholder

        foreigns = [col for col in self.columns() if issubclass(col.field_class, ForeignKey)]
        if any(foreigns):
            for col in foreigns:
                entity = col.foreign_entity.objects().get(col.value)
                setattr(self, col.entity_name, entity)

    def __str__(self):
        return (self.__class__.__name__ + "(" +
                ", ".join(key + "=" + str(getattr(self, key).value) for key in dir(self)
                          if isinstance(getattr(self, key), Column)) + ")")

    @classmethod
    def columns(cls):
        for item in dir(cls):
            instance = getattr(cls, item)
            if isinstance(instance, Column):
                yield instance

    @classmethod
    def from_namedtuple(cls, nt):
        params = {col.column_name: getattr(nt, col.column_name) for col in cls.columns()}
        return cls(**params)

    def as_namedtuple(self):
        nt = namedtuple(self.__class__.__name__, [c.column_name for c in self.columns()])
        for c in self.columns():
            setattr(nt, c.column_name, c.value)
        return nt

    @classmethod
    def tablename(cls):
        return cls.__tablename__

    @classmethod
    def objects(cls):
        if isinstance(cls._objects, type):
            cls._objects = cls._objects(cls)
        cls._objects.model = cls
        return cls._objects

    def _objects_placeholder(self):
        """Is needed to re-reference object attribute for instances of class"""
        return self._objects

    def _columns_placeholder(self):
        """Is needed to re-reference columns attribute for instances of class"""
        for item in dir(self):
            instance = getattr(self, item)
            if isinstance(instance, Column):
                yield instance
