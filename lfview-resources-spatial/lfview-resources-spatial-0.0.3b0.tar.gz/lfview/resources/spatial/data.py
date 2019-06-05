"""Data objects that hold numeric attributes and mapping to elements"""
from lfview.resources.files import Array
import properties
from properties.extras import Pointer
from six import string_types

from .base import _BaseResource
from .mappings import MappingCategory, MappingDiscrete, MappingContinuous


class _BaseData(_BaseResource):
    """Base class for data objects"""


class DataBasic(_BaseData):
    """Basic numeric attribute data

    This data type is defined by an array that directly maps
    to an element geometry. For no-data values, use NaN.

    Currently, this only accepts 1D arrays and, when applied to a grid,
    the array must be stored in row-major order.
    """
    BASE_TYPE = 'data'
    SUB_TYPE = 'basic'

    array = Pointer(
        'Array of numeric values at locations on an element geometry, '
        'specified by the location property',
        Array,
    )
    location = properties.StringChoice(
        'Location of the data on geometry',
        choices={
            'nodes': ['N', 'node', 'vertices', 'corners'],
            'cells': ['CC', 'cell', 'segments', 'faces', 'blocks'],
        }
    )
    mappings = properties.List(
        'Mappings associated with the data',
        prop=properties.Union(
            '',
            props=[
                Pointer('', MappingContinuous),
                Pointer('', MappingDiscrete),
            ],
        ),
        max_length=100,
        default=list,
    )

    @properties.validator('array')
    def _validate_array_1d(self, change):
        """Ensure the array is 1D"""
        if (isinstance(change['value'], string_types)
                or change['value'] is properties.undefined):
            return
        if not change['value'].is_1d():
            raise properties.ValidationError(
                message='{} must use 1D array'.format(
                    self.__class__.__name__,
                ),
                reason='invalid',
                prop='array',
                instance=self,
            )


class DataCategory(DataBasic):
    """Category attribute data

    This data type requires the array to be integer values that
    that correspond to the indices defined by the categories
    mapping object. Any values in the array that do not have a
    corresponding category index are assumed to be no-data.

    Similar to DataBasic, arrays must be 1D and row-major ordered when
    applied to grids.
    """

    SUB_TYPE = 'category'

    categories = Pointer(
        'Category mappings that define indices and corresponding data values',
        MappingCategory,
    )
    mappings = properties.List(
        'Other mappings associated with the categories',
        prop=Pointer('', MappingCategory),
        max_length=100,
        default=list,
    )

    @properties.validator('array')
    def _validate_array_int(self, change):
        """Ensure the array is only integers"""
        if (isinstance(change['value'], string_types)
                or change['value'] is properties.undefined):
            return
        if 'int' not in change['value'].dtype.lower():
            raise properties.ValidationError(
                message='{} must use integer array'.format(
                    self.__class__.__name__,
                ),
                reason='invalid',
                prop='array',
                instance=self,
            )
