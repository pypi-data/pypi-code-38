"""3D spatial element classes that hold object geometry and associated data"""

from lfview.resources.files import Array
import numpy as np
import properties
from properties.extras import Pointer
from six import string_types

from .base import _BaseResource, InstanceSnapshot
from .data import DataBasic, DataCategory
from .options import (
    OptionsPoints,
    OptionsLines,
    OptionsTubes,
    OptionsSurface,
    OptionsBlockModel,
    OptionsVolumeSlices,
)
from .textures import TextureProjection


class _BaseElement(_BaseResource):
    """Base class for elements"""

    BASE_TYPE = 'elements'

    data = properties.List(
        'Data defined on the element',
        prop=properties.Union(
            '',
            props=[
                Pointer('', DataBasic),
                Pointer('', DataCategory),
            ],
        ),
        max_length=100,
        default=list,
    )

    @property
    def num_nodes(self):
        """Number of nodes (vertices)"""
        raise NotImplementedError()

    @property
    def num_cells(self):
        """Number of cells"""
        raise NotImplementedError()

    @property
    def location_lengths(self):
        lengths = {
            'nodes': self.num_nodes,
            'cells': self.num_cells,
        }
        return lengths

    @properties.validator
    def _validate_data(self):
        """Check if element is built correctly"""
        if not self.data:
            return True
        for data in self.data:
            if isinstance(data, (string_types, TextureProjection)):
                continue
            if data.location not in self.location_lengths:
                raise properties.ValidationError(
                    message='Invalid location {} - valid values: {}'.format(
                        data.location, ', '.join(self.location_lengths)
                    ),
                    reason='invalid',
                    prop='data',
                    instance=self,
                )
            if isinstance(data.array, string_types):
                continue
            valid_length = self.location_lengths[data.location]
            if valid_length is None:
                continue
            if data.array.shape[0] != valid_length:
                raise properties.ValidationError(
                    message=(
                        'data {index} length {datalen} does not match '
                        '{loc} length {meshlen}'.format(
                            index=data.name,
                            datalen=data.array.shape[0],
                            loc=data.location,
                            meshlen=valid_length,
                        )
                    ),
                    reason='invalid',
                    prop='data',
                    instance=self,
                )
        return True


class _BaseElementPointSet(_BaseElement):
    """Base class for point-set elements"""

    data = properties.List(
        'Data defined on the element',
        prop=properties.Union(
            '',
            props=[
                Pointer('', DataBasic),
                Pointer('', DataCategory),
                Pointer('', TextureProjection),
            ],
        ),
        max_length=100,
        default=list,
    )

    defaults = InstanceSnapshot(
        'Default visualization options',
        OptionsPoints,
        default={
            'visible': True,
            'color': {
                'value': 'random'
            },
            'opacity': {
                'value': 1.
            },
        },
    )


class _BaseElementLineSet(_BaseElement):
    """Base class for line-set elements"""

    defaults = properties.Union(
        'Default visualization options',
        props=[
            InstanceSnapshot('', OptionsLines),
            InstanceSnapshot('', OptionsTubes),
        ],
        default={
            'visible': True,
            'color': {
                'value': 'random'
            },
            'opacity': {
                'value': 1.
            },
        },
    )


class _BaseElementSurface(_BaseElement):
    """Base class for surface elements"""

    data = properties.List(
        'Data defined on the element',
        prop=properties.Union(
            '',
            props=[
                Pointer('', DataBasic),
                Pointer('', DataCategory),
                Pointer('', TextureProjection),
            ],
        ),
        max_length=100,
        default=list,
    )
    defaults = InstanceSnapshot(
        'Default visualization options',
        OptionsSurface,
        default={
            'visible': True,
            'color': {
                'value': 'random'
            },
            'opacity': {
                'value': 1.
            },
            'wireframe': {
                'active': False
            },
            'textures': [],
        },
    )


class _BaseElementVolume(_BaseElement):
    """Base class for volume elements"""

    defaults = properties.Union(
        'Default visualization options',
        props=[
            InstanceSnapshot('', OptionsBlockModel),
            InstanceSnapshot('', OptionsVolumeSlices),
        ],
        default={
            'visible': True,
            'color': {
                'value': 'random'
            },
            'opacity': {
                'value': 1.
            },
            'wireframe': {
                'active': False
            },
        },
    )


class ElementPointSet(_BaseElementPointSet):
    """Point-set element with geometry defined array of vertices"""

    SUB_TYPE = 'pointset'

    vertices = Pointer(
        'Spatial coordinates of points, must be of shape N x 3',
        Array,
    )

    @property
    def num_nodes(self):
        """Number of nodes (vertices)"""
        try:
            return self.vertices.shape[0]
        except (AttributeError, IndexError, TypeError):
            return None

    @property
    def num_cells(self):
        """Number of cell centers (same as nodes)"""
        return self.num_nodes

    @properties.validator('vertices')
    def _validate_vertices(self, change):
        """Ensure vertices array is Nx3"""
        if (isinstance(change['value'], string_types)
                or change['value'] is properties.undefined):
            return True
        if len(change['value'].shape) != 2 or change['value'].shape[1] != 3:
            raise properties.ValidationError(
                message='PointSet vertices must be Nx3 array',
                reason='invalid',
                prop='vertices',
                instance=self,
            )
        return True


class ElementLineSet(_BaseElementLineSet):
    """Line-set element with geometry defined by vertices and segments"""

    SUB_TYPE = 'lineset'

    vertices = Pointer(
        'Spatial coordinates of vertices, must be of shape N x 3',
        Array,
    )
    segments = Pointer(
        'Pairs of zero-based vertex indices corresponding to line segment '
        'endpoints, must be integer values and of shape M x 2',
        Array,
    )

    @property
    def num_nodes(self):
        """Number of nodes (vertices)"""
        try:
            return self.vertices.shape[0]
        except (AttributeError, IndexError, TypeError):
            return None

    @property
    def num_cells(self):
        """Number of cells (segments)"""
        try:
            return self.segments.shape[0]
        except (AttributeError, IndexError, TypeError):
            return None

    @properties.validator('vertices')
    def _validate_vertices(self, change):
        """Ensure vertices array is Nx3"""
        if (isinstance(change['value'], string_types)
                or change['value'] is properties.undefined):
            return True
        if len(change['value'].shape) != 2 or change['value'].shape[1] != 3:
            raise properties.ValidationError(
                message='LineSet vertices must be Nx3 array',
                reason='invalid',
                prop='vertices',
                instance=self,
            )
        return True

    @properties.validator('segments')
    def _validate_segments(self, change):
        """Ensure segments array is Mx2 and non-negative integers"""
        segments = change['value']
        if (isinstance(segments, string_types)
                or segments is properties.undefined):
            return True
        if len(segments.shape) != 2 or segments.shape[1] != 2:
            raise properties.ValidationError(
                message='LineSet segments must be Mx2 array',
                reason='invalid',
                prop='segments',
                instance=self,
            )
        if 'int' not in segments.dtype.lower():
            raise properties.ValidationError(
                message='LineSet segments must be an integer array',
                reason='invalid',
                prop='segments',
                instance=self,
            )
        if (getattr(segments, 'array', None) is not None
                and np.min(segments.array) < 0):
            raise properties.ValidationError(
                message='Segments may only have non-negative integers',
                reason='invalid',
                prop='segments',
                instance=self,
            )
        return True

    @properties.validator
    def _validate_geometry(self):
        """Ensures segment indices are valid in conjunction with vertices"""
        if (isinstance(self.vertices, string_types)
                or getattr(self.segments, 'array', None) is None):
            return True
        if np.max(self.segments.array) >= self.vertices.shape[0]:
            raise properties.ValidationError(
                message='Segment indices are outside bounds for vertices',
                reason='invalid',
                prop='segments',
                instance=self,
            )
        return True


class ElementSurface(_BaseElementSurface):
    """Surface element with geometry defined by vertices and triangles"""

    SUB_TYPE = 'surface'

    vertices = Pointer(
        'Spatial coordinates of vertices, must be of shape N x 3',
        Array,
    )
    triangles = Pointer(
        'Trios of zero-based vertex indices corresponding to triangle '
        'corners, must be integer values and of shape M x 3',
        Array,
    )

    @property
    def num_nodes(self):
        """Number of nodes (vertices)"""
        try:
            return self.vertices.shape[0]
        except (AttributeError, IndexError, TypeError):
            return None

    @property
    def num_cells(self):
        """Number of cells (triangles)"""
        try:
            return self.triangles.shape[0]
        except (AttributeError, IndexError, TypeError):
            return None

    @properties.validator('vertices')
    def _validate_vertices(self, change):
        """Ensure vertices array is Nx3"""
        if (isinstance(change['value'], string_types)
                or change['value'] is properties.undefined):
            return True
        if len(change['value'].shape) != 2 or change['value'].shape[1] != 3:
            raise properties.ValidationError(
                message='Surface vertices must be Nx3 array',
                reason='invalid',
                prop='vertices',
                instance=self,
            )
        return True

    @properties.validator('triangles')
    def _validate_triangles(self, change):
        """Ensure segments array is Mx2 and non-negative integers"""
        triangles = change['value']
        if (isinstance(triangles, string_types)
                or triangles is properties.undefined):
            return True
        if len(triangles.shape) != 2 or triangles.shape[1] != 3:
            raise properties.ValidationError(
                message='Surface triangles must be Nx2 array',
                reason='invalid',
                prop='triangles',
                instance=self,
            )
        if 'int' not in triangles.dtype.lower():
            raise properties.ValidationError(
                message='Surface triangles must be an integer array',
                reason='invalid',
                prop='triangles',
                instance=self,
            )
        if (getattr(triangles, 'array', None) is not None
                and np.min(triangles.array) < 0):
            raise properties.ValidationError(
                message='Triangles may only have positive integers',
                reason='invalid',
                prop='triangles',
                instance=self,
            )
        return True

    @properties.validator
    def _validate_geometry(self):
        """Ensures triangle indices are valid in conjunction with vertices"""
        if (isinstance(self.vertices, string_types)
                or getattr(self.triangles, 'array', None) is None):
            return True
        if np.max(self.triangles.array) >= self.vertices.shape[0]:
            raise properties.ValidationError(
                message='Triangle indices are outside bounds for vertices',
                reason='invalid',
                prop='triangles',
                instance=self,
            )
        return True


class ElementSurfaceGrid(_BaseElementSurface):
    """Surface element with geometry defined by a grid

    The grid is defined by two axes and cell spacing along these
    axes.
    """

    SUB_TYPE = 'surfacegrid'

    origin = properties.Vector3(
        'Grid origin, where axis_u and axis_v vectors extend from',
    )
    tensor_u = properties.List(
        'Grid cell widths, u-direction',
        properties.Float('', min=0),
        max_length=10000,
        coerce=True,
    )
    tensor_v = properties.List(
        'Grid cell widths, v-direction',
        properties.Float('', min=0),
        max_length=10000,
        coerce=True,
    )
    axis_u = properties.Vector3(
        'Vector orientation of u-direction',
        length=1,
    )
    axis_v = properties.Vector3(
        'Vector orientation of v-direction',
        length=1,
    )
    offset_w = Pointer(
        'Node offset perpendicular to the two axes; this must be an array '
        'of shape len(tensor_u)+1 x len(tensor_v)+1, flattened with '
        'row-major order',
        Array,
        required=False,
    )

    @property
    def num_nodes(self):
        """Number of nodes (vertices)"""
        try:
            return (len(self.tensor_u) + 1) * (len(self.tensor_v) + 1)
        except (AttributeError, IndexError, TypeError):
            return None

    @property
    def num_cells(self):
        """Number of cells (faces)"""
        try:
            return len(self.tensor_u) * len(self.tensor_v)
        except (AttributeError, IndexError, TypeError):
            return None

    @properties.validator
    def _validate_geometry(self):
        """Ensure offset_w shape is consistent with tensor lengths"""
        if self.offset_w is None or isinstance(self.offset_w, string_types):
            return True
        if len(self.offset_w.shape) != 1:
            raise properties.ValidationError(
                message='offset_w must be 1D array, not of shape {}'.format(
                    self.offset_w.shape
                ),
                reason='invalid',
                prop='offset_w',
                instance=self,
            )
        if self.offset_w.shape[0] != self.num_nodes:
            raise properties.ValidationError(
                message=(
                    'Length of offset_w, {zlen}, must equal number of nodes, '
                    '{nnode}'.format(
                        zlen=self.offset_w.shape[0],
                        nnode=self.num_nodes,
                    )
                ),
                reason='invalid',
                prop='offset_w',
                instance=self,
            )
        return True


class ElementVolumeGrid(_BaseElementVolume):
    """Volume element with geometry defined by a grid

    The grid is defined by three axes and cell spacing along these
    axes.
    """

    SUB_TYPE = 'volumegrid'

    origin = properties.Vector3(
        'Grid origin, where axis_u, axis_v, and axis_w vectors extend from',
    )
    tensor_u = properties.List(
        'Tensor cell widths, u-direction',
        properties.Float('', min=0),
        max_length=2000,
        coerce=True,
    )
    tensor_v = properties.List(
        'Tensor cell widths, v-direction',
        properties.Float('', min=0),
        max_length=2000,
        coerce=True,
    )
    tensor_w = properties.List(
        'Tensor cell widths, w-direction',
        properties.Float('', min=0),
        max_length=2000,
        coerce=True,
    )
    axis_u = properties.Vector3(
        'Vector orientation of u-direction',
        length=1,
    )
    axis_v = properties.Vector3(
        'Vector orientation of v-direction',
        length=1,
    )
    axis_w = properties.Vector3(
        'Vector orientation of w-direction',
        length=1,
    )

    @property
    def num_nodes(self):
        """Number of nodes (vertices)"""
        try:
            nodes = (
                (len(self.tensor_u) + 1) * (len(self.tensor_v) + 1) *
                (len(self.tensor_w) + 1)
            )
            return nodes
        except (AttributeError, IndexError, TypeError):
            return None

    @property
    def num_cells(self):
        """Number of cells (faces)"""
        try:
            cells = (
                len(self.tensor_u) * len(self.tensor_v) * len(self.tensor_w)
            )
            return cells
        except (AttributeError, IndexError, TypeError):
            return None
