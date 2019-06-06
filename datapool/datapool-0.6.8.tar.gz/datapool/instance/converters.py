# encoding: utf-8
from __future__ import print_function, division, absolute_import

from functools import singledispatch

from .db_objects import SiteDbo, SourceTypeDbo, ParameterDbo
from .domain_objects import DomainObject, Site, SourceType
from . import db_objects


@singledispatch
def domain_object_to_dbo(domain_object):
    assert isinstance(domain_object, DomainObject)
    dbo = getattr(db_objects, domain_object.dbo)
    return _domain_object_to_dbo(domain_object, dbo)


def _domain_object_to_dbo(domain_object, dbo_class):
    dd = {k: v for (k, v) in domain_object.items() if not k.startswith("_")}
    return dbo_class(**dd)


@domain_object_to_dbo.register(Site)
def site_to_dbo(site):
    site = site.copy()
    site.pictures = [domain_object_to_dbo(p) for p in site.pictures]
    return _domain_object_to_dbo(site, SiteDbo)


@domain_object_to_dbo.register(SourceType)
def source_type_to_dbo(source_type):
    source_type = source_type.copy()
    source_type.special_values = [
        domain_object_to_dbo(sv) for sv in source_type.special_values
    ]
    return _domain_object_to_dbo(source_type, SourceTypeDbo)
