"""Spatial resources for LF View API Python client"""
from . import base, data, elements, mappings, options, textures
from .data import (
    DataBasic,
    DataCategory,
)
from .elements import (
    ElementPointSet,
    ElementLineSet,
    ElementSurface,
    ElementSurfaceGrid,
    ElementVolumeGrid,
)
from .mappings import (
    MappingCategory,
    MappingContinuous,
    MappingDiscrete,
)
from .options import (
    OptionsPoints,
    OptionsLines,
    OptionsTubes,
    OptionsSurface,
    OptionsBlockModel,
    OptionsVolumeSlices,
)
from .textures import (
    TextureProjection,
)

__version__ = '0.0.4'

SPATIAL_REGISTRY = base._BaseResource._REGISTRY
