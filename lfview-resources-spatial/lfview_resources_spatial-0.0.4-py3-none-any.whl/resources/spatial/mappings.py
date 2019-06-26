"""Objects that map a data array to attributes for visualization"""
from lfview.resources.files import Array
import numpy as np
import properties
from properties.extras import Pointer
from six import string_types

from .base import _BaseResource, ShortString, from_hex, to_hex


class _BaseMapping(_BaseResource):
    """Base class for all mapping types"""

    BASE_TYPE = 'mappings'


class _BaseDataMapping(_BaseMapping):
    """Base class for array-data mappings"""


class MappingContinuous(_BaseDataMapping):
    """Mapping of continuous data to a continuous gradient

    The most common use-case for continuous mappings is colormaps by
    specifying a N x 3 color gradient and a transfer function between
    data values and the gradient as sketched below.

    Note: Visualization clients may have limited support for complicated
    transfer functions. For best results, use
    :code:`mapping.data_controls = [0., 0, 1, 1]` or :code:`[1., 1, 0, 0]`.
    When combined with
    :code:`mapping.visibility = [False, True, True, True, False]`
    you get 5 color regions for your data:

    1) :code:`-Inf` to :code:`data_controls[0]` - Not visible
    2) :code:`data_controls[0]` to :code:`data_controls[1]` - Low gradient value
    3) :code:`data_controls[1]` to :code:`data_controls[2]` - Gradient dynamic range
    4) :code:`data_controls[2]` to :code:`data_controls[3]` - High gradient value
    5) :code:`data_controls[3]` to :code:`Inf` - Not visible

    .. code::

      #      gradient
      #          1
      #          -
      #         -|                      x - - - - - - ->
      # gradient |                     /
      # controls |                    /
      #          |                   /
      #         -|     <- - - - - - x
      #          |
      #          |
      #          -
      #          0
      #                <------------|---|--------------> data
      #                          data_controls
    """

    SUB_TYPE = 'continuous'

    gradient = Pointer(
        'Array defining the gradient',
        Array,
    )
    data_controls = properties.List(
        'Data values for data/gradient inflection points; '
        'these values must be increasing and -inf/inf are implicit '
        'lower/upper values',
        prop=properties.Float(''),
        min_length=2,
        max_length=4,
    )
    gradient_controls = properties.List(
        'Normalized gradient values for data/gradient inflection points; '
        'length must equal len(data_controls)',
        prop=properties.Float('', min=0, max=1),
        min_length=2,
        max_length=4,
        default=lambda: [0., 0., 1., 1.],
    )
    visibility = properties.List(
        'True if region between control points is visible; '
        'length must equal len(data_controls) + 1',
        prop=properties.Boolean('', cast=True),
        min_length=3,
        max_length=5,
        default=lambda: [False, True, True, True, False],
    )
    interpolate = properties.Boolean(
        'If True, interpolate the gradient values; if False, only '
        'use values explicitly in the gradient',
        cast=True,
        default=False,
    )

    @properties.validator
    def _validate_controls(self):
        """Validate lengths of data_controls/gradient_controls/visibility"""
        if len(self.data_controls) != len(self.gradient_controls):
            raise properties.ValidationError(
                message='data and gradient controls must be equal length',
                reason='invalid',
                prop='data_controls',
                instance=self,
            )
        if len(self.data_controls) != len(self.visibility) - 1:
            raise properties.ValidationError(
                message='visibility must be one longer than data controls',
                reason='invalid',
                prop='data_controls',
                instance=self,
            )

    @properties.validator('data_controls')
    def _validate_increasing(self, change):
        """Ensure data_controls are all increasing"""
        if change['value'] is properties.undefined:
            return
        diffs = np.array(change['value'][1:]) - np.array(change['value'][:-1])
        if not np.all(diffs >= 0):
            raise properties.ValidationError(
                message='data controls must not decrease: {}'.format(
                    change['value'],
                ),
                reason='invalid',
                prop='data_controls',
                instance=self,
            )


class MappingDiscrete(_BaseDataMapping):
    """Mapping of continuous data to discrete intervals

    These mappings are used to categorize continuous numeric data.
    Define the limits of the intervals by specifying end points, and
    specify if the end points are inclusive in the lower or upper bucket.
    Then assign values to each interval.

    .. code::

      #       values
      #
      #         --                          x - - - - ->
      #
      #         --                  x - - - o
      #
      #         --     <- - - - - - o
      #
      #                <------------|--------|------------> data
      #                             end_points
    """

    SUB_TYPE = 'discrete'

    values = properties.Union(
        'Values corresponding to intervals',
        props=[
            properties.List(
                '',
                properties.Color('', serializer=to_hex, deserializer=from_hex),
                max_length=256,
            ),
            properties.List('', properties.Float(''), max_length=256),
            properties.List(
                '',
                ShortString('', max_length=300),
                max_length=256,
            ),
        ],
    )
    end_points = properties.List(
        'Data end values of discrete intervals; these also correspond to '
        'the start of the next interval. First start and final end are '
        'fixed at -inf and inf, respectively.',
        prop=properties.Float(''),
        max_length=255,
    )
    end_inclusive = properties.List(
        'True if corresponding end is inclusive for lower range and false if '
        'it is inclusive for upper range; must be specified for each interval',
        prop=properties.Boolean('', cast=True),
        max_length=255,
    )
    visibility = properties.List(
        'True if interval is visible; must be specified for each interval',
        prop=properties.Boolean('', cast=True),
        max_length=256,
    )

    @properties.validator
    def _validate_lengths(self):
        """Validate lengths of values/end_points/end_inclusive/visibility"""
        if len(self.values) != len(self.visibility):
            raise properties.ValidationError(
                message='values and visibility must be equal length',
                reason='invalid',
                prop='visibility',
                instance=self,
            )
        if len(self.values) != len(self.end_points) + 1:
            raise properties.ValidationError(
                message='values must be one longer than end points',
                reason='invalid',
                prop='end_points',
                instance=self,
            )
        if len(self.values) != len(self.end_inclusive) + 1:
            raise properties.ValidationError(
                message='values must be one longer than end inclusive',
                reason='invalid',
                prop='end_inclusive',
                instance=self,
            )

    @properties.validator('end_points')
    def _validate_increasing(self, change):
        """Ensure end_points are increasing"""
        if change['value'] is properties.undefined:
            return
        diffs = np.array(change['value'][1:]) - np.array(change['value'][:-1])
        if not np.all(diffs >= 0):
            raise properties.ValidationError(
                message='end points must not decrease: {}'.format(
                    change['value']
                ),
                reason='invalid',
                prop='end_points',
                instance=self,
            )


class MappingCategory(_BaseDataMapping):
    """Mapping of integer index values to categories

    These mappings are used to define categories on
    :class:`spatial.resources.spatial.data.DataCategory` as
    well as color and other visual aspects. Data array values
    correspond to indices which then map to the values. If an
    array value is not present in indices, it is assumed there
    is no data at that location.

    .. code::

      #       values
      #
      #         --                          x
      #
      #         --            x
      #
      #         --       x
      #
      #                  |    |             |
      #                        indices
    """
    SUB_TYPE = 'category'

    values = properties.Union(
        'Values corresponding to indices',
        props=[
            properties.List(
                '',
                properties.Color('', serializer=to_hex, deserializer=from_hex),
                max_length=256,
            ),
            properties.List('', properties.Float(''), max_length=256),
            properties.List(
                '',
                ShortString('', max_length=300),
                max_length=256,
            ),
        ],
    )
    indices = properties.List(
        'Array indices for values',
        properties.Integer('', min=0),
        max_length=256,
    )
    visibility = properties.List(
        'True if category is visible',
        prop=properties.Boolean('', cast=True),
        max_length=256,
    )

    @properties.validator
    def _validate_lengths(self):
        """Validate lengths of values/indices/visibility"""
        if len(self.values) != len(self.indices):
            raise properties.ValidationError(
                message='values and indices must be equal length',
                reason='invalid',
                prop='indices',
                instance=self,
            )
        if len(self.values) != len(self.visibility):
            raise properties.ValidationError(
                message='values and visibility must be equal length',
                reason='invalid',
                prop='visibility',
                instance=self,
            )

    @properties.validator('indices')
    def _validate_indices_unique(self, change):
        """Ensure indices are unique"""
        if change['value'] is properties.undefined:
            return
        if len(change['value']) != len(set(change['value'])):
            raise properties.ValidationError(
                message='indices must be unique: {}'.format(change['value']),
                reason='invalid',
                prop='indices',
                instance=self,
            )
