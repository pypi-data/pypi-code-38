# encoding: utf-8
from __future__ import absolute_import, division, print_function

import datetime
import importlib
import os

from sqlalchemy.sql.sqltypes import Date, DateTime, Float, Integer, LargeBinary, String

from datapool.bunch import Bunch
from datapool.errors import FormatError

from ..errors import FormatError
from .db_objects import (
    ParameterAveragingDbo,
    ParameterDbo,
    PictureDbo,
    SignalDbo,
    SiteDbo,
    SourceDbo,
    SourceTypeDbo,
    SpecialValueDefinitionDbo,
)

backmap = {
    Integer: int,
    String: str,
    Float: float,
    Date: datetime.date,
    DateTime: datetime.datetime,
    LargeBinary: bytes,
}


def _check_attribute_types(obj):
    """
    checks domain objects attribute types based on declarations in db_objects.py
    """
    from . import db_objects

    dbo = getattr(db_objects, obj.dbo)

    for name, value in dbo._sa_class_manager.mapper.c.items():
        if value.primary_key:
            # these are automatically assigend when committin a dbo:
            continue
        if value.foreign_keys:
            # foreign keys have no pure python type but point to other dbos,
            # we do not check here but rely on other checks when commiting the
            # final object to the database:
            continue

        attribute_value = getattr(obj, name)
        if value.nullable and attribute_value is None:
            continue

        python_type = backmap.get(value.type.__class__)
        if python_type is None:
            raise RuntimeError("no idea how to check for type {}".format(value.type))

        if not isinstance(attribute_value, python_type):
            raise FormatError(
                "{!r} is not of type {}".format(attribute_value, python_type)
            )


"""
# Some principles:

- We implement "duplicate" classes for domain objects (which eg are created by parsing yaml files)
and dbo objects from sqlalchemy, because sqlalchemy objects sometimes do some confusing "magic".
Althouth this can be circumvented the resulting fixes makes code hard to understand and dangerous
to modify if someone is not aware of this "magic".

- We try to keep the domain objects and dbo objects as slick as possible.
"""


class DomainObject:

    dbo = None

    def check_attributes(self):
        _check_attribute_types(self)


class RelPathMixin:
    def set_rel_path(self, rel_path):
        self._rel_path = rel_path

    @property
    def file_name(self):
        if self._rel_path is not None:
            return os.path.basename(self._rel_path)

    @property
    def rel_path(self):
        return self._rel_path


class BunchBasedDomainObject(Bunch, RelPathMixin, DomainObject):
    def __init__(self, bunch, rel_path=None):
        super().__init__(bunch)
        self.set_rel_path(rel_path)


class Site(BunchBasedDomainObject):

    dbo = "SiteDbo"

    def check_attributes(self):
        _check_attribute_types(self)
        for p in self.pictures:
            _check_attribute_types(p)


class Signal(Bunch, DomainObject):

    dbo = "SignalDbo"

    def __init__(self, dd):
        assert isinstance(dd, dict)
        for key in ("value", "parameter", "timestamp"):
            if key not in dd:
                raise ValueError("{} has no key {}".format(dd, key))
        if "site" not in dd or dd["site"] is None:
            if not all("coord_" + k in dd for k in "xyz"):
                raise ValueError(
                    "{} must either have key 'site' or 'x', 'y' and 'z'".format(dd)
                )
            dd["site"] = None
        else:
            if any("coord_" + k in dd and dd["coord_" + k] is not None for k in "xyz"):
                raise ValueError(
                    "{} must either have key 'site' or 'x', 'y' and 'z'".format(dd)
                )
            dd["coord_x"] = dd["coord_y"] = dd["coord_z"] = None
        super().__init__(dd)

    def __str__(self):
        if "site" in self:
            return (
                "value={self.value} parameter={self.parameter} timestamp={self.timestamp} "
                "source={self.source} site={self.site}".format(self=self)
            )
        else:
            return (
                "value={self.value} parameter={self.parameter} timestamp={self.timestamp} "
                "source={self.source} x={self.x!r} y={self.y!r} "
                "z={self.z!r}".format(self=self)
            )


class Picture(Bunch, DomainObject):

    dbo = "PictureDbo"


class Parameter(Bunch, DomainObject):

    dbo = "ParameterDbo"

    def __init__(self, *a, **d):
        super().__init__(*a, **d)
        self.unit = str(self.unit)


class Parameters(RelPathMixin, DomainObject):
    def __init__(self, parameters, rel_path):
        self.parameters = parameters
        self.set_rel_path(rel_path)

    def __str__(self):
        return str(self.parameters)

    def __repr__(self):
        return repr(self.parameters)

    def __iter__(self):
        return iter(self.parameters)

    def check_attributes(self):
        for p in self.parameters:
            _check_attribute_types(p)


class ParameterAveraging(BunchBasedDomainObject):

    dbo = "ParameterAveragingDbo"


class Source(BunchBasedDomainObject):

    dbo = "SourceDbo"


class SourceType(BunchBasedDomainObject):

    dbo = "SourceTypeDbo"

    def check_attributes(self):
        super().check_attributes()
        for p in self.special_values:
            _check_attribute_types(p)


class SpecialValueDefinition(BunchBasedDomainObject):

    dbo = "SpecialValueDefinitionDbo"
