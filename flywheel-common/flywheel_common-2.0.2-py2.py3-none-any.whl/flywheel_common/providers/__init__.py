"""Provides interfaces for providers and sub provider types"""
from __future__ import print_function
from enum import Enum
from pkg_resources import iter_entry_points

from .creds import Creds
from .compute.base import BaseComputeProvider
from .storage.base import BaseStorageProvider
from .provider import BaseProviderSchema
from ..errors import ValidationError

class ProviderClass(Enum):
    """Enumeration of provider classes"""
    compute = 'compute'  # Compute resource provider
    storage = 'storage'  # Storage resource provider


CRED_TYPES = {}
PROVIDER_TYPES = {}
LOADED_CREDS = {}
LOADED_PROVIDERS = {}

def create_provider(class_, type_, label, config, creds, id_=None):
    """ Will instantiate and return a domain model object of the specified provider class and type"""
    values = set(item.value for item in ProviderClass)
    if not class_ in values:
        raise ValueError('Unregistered provider class specified')

    # Load the entry points registered system wide
    if not CRED_TYPES:
        for entry_point in iter_entry_points('flywheel.credentials'):
            CRED_TYPES[entry_point.name] = entry_point

    if not PROVIDER_TYPES:
        for entry_point in iter_entry_points('flywheel.providers'):
            PROVIDER_TYPES[entry_point.name] = entry_point

    # Local, static, and gc are a special case but we could force an empty object in the schema
    if type_ == 'local' or type_ == 'static' or (type_ == 'gc' and class_ == 'storage'):
        creds = None
    else:
        if not LOADED_CREDS.get(type_):
            if not CRED_TYPES.get(type_):
                raise ValidationError('No Provider is registered for {}'.format(type_))
            LOADED_CREDS[type_] = CRED_TYPES[type_].load()
        creds = LOADED_CREDS[type_](provider_class=class_, provider_type=type_, provider_label=label, config=creds)
        creds._id = id_
        creds.provider_id = id_
        creds.validate()

    pro_name = class_ + "_" + type_
    if not LOADED_PROVIDERS.get(pro_name):
        if not PROVIDER_TYPES.get(pro_name):
            raise ValidationError('No provider is registered for {}'.format(pro_name))
        LOADED_PROVIDERS[pro_name] = PROVIDER_TYPES[pro_name].load()
    provider = LOADED_PROVIDERS[pro_name](provider_class=class_, provider_type=type_, provider_label=label, creds=creds, config=config)
    provider._id  = id_
    provider.provider_id = id_
    return provider
