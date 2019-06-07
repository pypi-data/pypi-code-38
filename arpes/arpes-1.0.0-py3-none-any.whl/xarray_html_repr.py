"""
# For now, this is not in use because I am going to see what I can get done with the .S
# accessors, this way we can specialize to context

from arpes.config import SETTINGS
from arpes.xarray_extensions import ARPESDataArrayAccessor, ARPESDatasetAccessor

original_mods = {}

def patch_method(method, name=None):
    if name is None:
        name = method.__name__


def unpatch_method(method, name=None):
    if name is None:
        name = method.__name__


if SETTINGS.get('xarray_repr_mod'):
    pass
else:
    pass

def repr_html_arpes(self):
    return {
        'a': 5,
        'b': 8
    }

#ARPESDataArrayAccessor._repr_html_ = repr_html_arpes
ARPESDatasetAccessor._repr_html_ = repr_html_arpes
"""