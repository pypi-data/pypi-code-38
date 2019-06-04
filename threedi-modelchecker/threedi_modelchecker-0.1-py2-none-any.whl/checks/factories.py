from geoalchemy2.types import Geometry

from .base import ForeignKeyCheck
from .base import EnumCheck
from .base import GeometryCheck
from .base import GeometryTypeCheck
from .base import TypeCheck
from .base import NotNullCheck
from .base import UniqueCheck
from ..threedi_model import custom_types


def generate_foreign_key_checks(table):
    foreign_key_checks = []
    for fk_column in table.foreign_keys:
        foreign_key_checks.append(
            ForeignKeyCheck(
                reference_column=fk_column.column,
                column=fk_column.parent)
        )
    return foreign_key_checks


def generate_unique_checks(table):
    unique_checks = []
    for column in table.columns:
        if column.unique or column.primary_key:
            unique_checks.append(UniqueCheck(column))
    return unique_checks


def generate_not_null_checks(table):
    not_null_checks = []
    for column in table.columns:
        if not column.nullable:
            not_null_checks.append(NotNullCheck(column))
    return not_null_checks


def generate_type_checks(table):
    data_type_checks = []
    for column in table.columns:
        data_type_checks.append(TypeCheck(column))
    return data_type_checks


def generate_geometry_checks(table):
    geometry_checks = []
    for column in table.columns:
        if type(column.type) == Geometry:
            geometry_checks.append(GeometryCheck(column))
    return geometry_checks


def generate_geometry_type_checks(table):
    geometry_type_checks = []
    for column in table.columns:
        if type(column.type) == Geometry:
            geometry_type_checks.append(GeometryTypeCheck(column))
    return geometry_type_checks


def generate_enum_checks(table):
    enum_checks = []
    for column in table.columns:
        if issubclass(type(column.type), custom_types.IntegerEnum):
            enum_checks.append(EnumCheck(column))
    return enum_checks
