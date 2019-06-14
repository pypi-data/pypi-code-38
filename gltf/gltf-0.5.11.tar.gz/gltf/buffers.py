import logging
from enum import Enum

import numpy as np

from .utils import BaseGLTFStructure, load_uri

logger = logging.getLogger(__name__)


class BufferView(object):
    class BufferTarget(Enum):
        ARRAY_BUFFER = 34962
        ELEMENT_ARRAY_BUFFER = 34963

    target = None
    name = None
    offset = 0
    component_size = 4

    def __init__(self, buffer_view=None, gltf=None,
                 target=None, byte_stride=None, component_size=None, buffer=None):
        if target:
            self.target = self.BufferTarget(target)
        self.byte_stride = byte_stride
        self.component_size = component_size
        self.data = bytearray()
        self.buffer = buffer
        if buffer_view:
            self.name = buffer_view.get('name')
            self.buffer = gltf.buffers[buffer_view['buffer']]
            offset = buffer_view.get('byteOffset', 0)
            self.data = self.buffer.data[offset:offset + buffer_view['byteLength']]
            if 'target' in buffer_view:
                self.target = self.BufferTarget(buffer_view['target'])
            if 'byteStride' in buffer_view:
                self.byte_stride = buffer_view['byteStride']

    def __repr__(self):
        return self.name or super(BufferView, self).__repr__()

    @property
    def byte_length(self):
        return len(self.data)

    def write(self, data):
        offset = self.byte_length
        self.data += data
        return offset

    def write_to_buffer(self):
        self.offset = self.buffer.write(self.data, alignment=self.component_size)

    def render(self, gltf):
        buffer_view = {
            'buffer': gltf.index('buffers', self.buffer),
            'byteLength': self.byte_length,
        }
        if self.offset:
            buffer_view['byteOffset'] = self.offset
        if self.name:
            buffer_view['name'] = self.name
        if self.target:
            buffer_view['target'] = self.target.value
        if self.byte_stride:
            buffer_view['byteStride'] = self.byte_stride
        return buffer_view


class Buffer(object):
    name = None

    def __init__(self, buffer=None, gltf=None):
        self.buffer_views = {}
        self.data = bytearray()

        if buffer:
            self.name = buffer.get('name')
            if 'data' in buffer:
                self.data = bytearray(buffer['data'])
            else:
                self.data = load_uri(buffer['uri'], folder=gltf.folder)
            if self.byte_length != buffer['byteLength']:
                raise ValueError('Buffer length does not match')

    def __repr__(self):
        return self.name or super(Buffer, self).__repr__()

    @property
    def byte_length(self):
        return len(self.data)

    def write(self, data, alignment=None):
        offset = self.byte_length
        if alignment and offset % alignment:
            self.data += bytes([0x00] * (alignment - offset % alignment))
            offset = self.byte_length
        self.data += data
        return offset

    def render(self):
        buffer = {
            'data': self.data,
            'byteLength': self.byte_length
        }
        if self.name:
            buffer['name'] = self.name
        return buffer

    def get_view(self, target=None, byte_stride=None, component_size=None, image=None):
        view_type = image or (target, byte_stride, component_size)
        if view_type not in self.buffer_views:
            self.buffer_views[view_type] = BufferView(target=target,
                                                      byte_stride=byte_stride,
                                                      component_size=component_size,
                                                      buffer=self)
        return self.buffer_views[view_type]


class Accessor(BaseGLTFStructure):
    class ComponentType(Enum):
        int8 = 5120
        uint8 = 5121
        int16 = 5122
        uint16 = 5123
        uint32 = 5125
        float32 = 5126

    _valid_component_types = list(ComponentType)
    _data = None
    component_type = None
    type = str()
    target = BufferView.BufferTarget.ARRAY_BUFFER
    byte_stride = None
    size = 1

    def __init__(self, data=None, gltf=None):
        if type(data) is dict:
            self.name = data.get('name')
            component_type = data.get('componentType')
            if component_type is not None:
                self.component_type = self.ComponentType(component_type)
            else:
                logger.warning('Accessor has no component type')

            buffer_view = data.get('bufferView')
            if buffer_view is not None:
                bv = gltf.buffer_views[buffer_view]
            else:
                logger.warning('Accessor has no buffer view')
                return

            dtype = np.dtype(self.component_type.name)
            offset = data.get('byteOffset', 0)
            byte_size = data['count'] * (bv.byte_stride or self.size * dtype.itemsize)
            arr = np.frombuffer(bv.data[offset:offset + byte_size], dtype=dtype)

            if self.size != 1:
                arr = arr.reshape(len(arr) // self.size, self.size)

            if bv.byte_stride is not None and bv.byte_stride != self.size * dtype.itemsize:
                arr = arr[::bv.byte_stride // (self.size * dtype.itemsize)]

            self.data = arr
            self.target = bv.target

            if data['count'] != self.count:
                raise ValueError('Accessor count does not match! Expected {}, got {}'
                                 ''.format(data['count'], self.count))

            if 'min' in data and not np.allclose(data['min'], self.min, rtol=1e-07):
                logger.warning('Accessor minimum did not match! Expected {}, got {}'
                               ''.format(data['min'], self.min))

            if 'max' in data and not np.allclose(data['max'], self.max, rtol=1e-07):
                logger.warning('Accessor maximum did not match! Expected {}, got {}'
                               ''.format(data['max'], self.max))
        else:
            self.data = [] if data is None else data

    def __repr__(self):
        return self.name or super(Accessor, self).__repr__()

    def __eq__(self, other):
        if not ((isinstance(other, type(self))
                and (self.component_type, self.type, self.target,
                     self.byte_stride, self.size, self.name) ==
                (other.component_type, other.type, other.target,
                 other.byte_stride, other.size, other.name))):
            return False

        return np.array_equal(self._data, other._data)

    def check_component_type(self, dtype):
        if self.ComponentType[dtype] not in self._valid_component_types:
            raise TypeError(dtype + ' is an invalid data type for accessor of type ' + self.type)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, np.ndarray):
            self.check_component_type(str(data.dtype))
            self.component_type = Accessor.ComponentType[str(data.dtype)]
            self._data = data.copy()
        else:
            self._data = np.array(data, dtype=self.component_type.name)

    def render(self, buffer, gltf):
        view = buffer.get_view(self.target, self.byte_stride, self.data.itemsize)
        offset = view.write(self.data.tobytes())
        acc = {
            'componentType': self.component_type.value,
            'type': self.type,
            'count': self.count,
            'min': self.min,
            'max': self.max,
            'bufferView': gltf.index('buffer_views', view),
        }
        if self.name:
            acc['name'] = self.name
        if offset:
            acc['byteOffset'] = offset
        return acc

    @property
    def min(self):
        return np.nanmin(self.data, axis=0).tolist()

    @property
    def max(self):
        return np.nanmax(self.data, axis=0).tolist()

    @property
    def count(self):
        return len(self.data)


class ScalarArray(Accessor):
    type = 'SCALAR'
    component_type = Accessor.ComponentType.uint16
    target = BufferView.BufferTarget.ELEMENT_ARRAY_BUFFER
    _valid_component_types = [
        Accessor.ComponentType.uint8,
        Accessor.ComponentType.uint16,
        Accessor.ComponentType.uint32,
        Accessor.ComponentType.float32,
    ]

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, np.ndarray):
            data = np.array(data)

        if np.issubdtype(data.dtype, np.floating):
            self.component_type = Accessor.ComponentType.float32
            data = data.astype(Accessor.ComponentType.float32.name)
        elif data.max() < 255:
            self.component_type = Accessor.ComponentType.uint8
            data = data.astype(Accessor.ComponentType.uint8.name)
        elif data.max() < 65535:
            self.component_type = Accessor.ComponentType.uint16
            data = data.astype(Accessor.ComponentType.uint16.name)
        elif data.max() < 4294967295:
            self.component_type = Accessor.ComponentType.uint32
            data = data.astype(Accessor.ComponentType.uint32.name)
        else:
            raise ValueError('Invalid maximum for ScalarArray: ' + str(data.max()))

        self._data = data.copy()

    @property
    def min(self):
        return [float(np.min(self.data))]

    @property
    def max(self):
        return [float(np.max(self.data))]

    @property
    def count(self):
        return self.data.size


class Vec2Array(Accessor):
    type = 'VEC2'
    size = 2
    byte_stride = size * 4
    component_type = Accessor.ComponentType.float32
    _valid_component_types = [Accessor.ComponentType.float32]


class Vec3Array(Accessor):
    type = 'VEC3'
    size = 3
    byte_stride = size * 4
    component_type = Accessor.ComponentType.float32
    _valid_component_types = [Accessor.ComponentType.float32]


class Vec4Array(Accessor):
    type = 'VEC4'
    size = 4
    component_type = Accessor.ComponentType.float32
    _valid_component_types = [
        Accessor.ComponentType.uint8,
        Accessor.ComponentType.uint16,
        Accessor.ComponentType.float32,
    ]

    @property
    def byte_stride(self):
        if self.component_type == Accessor.ComponentType.float32:
            return self.size * 4
        if self.component_type == Accessor.ComponentType.uint16:
            return self.size * 2
        return self.size


class Mat4Array(Accessor):
    type = 'MAT4'
    size = 16
    byte_stride = size * 4
    component_type = Accessor.ComponentType.float32
    _valid_component_types = [Accessor.ComponentType.float32]
