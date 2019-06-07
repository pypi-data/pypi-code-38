import numpy as np

from numbers import Number
from typing import (Optional, TypeVar, Union)

from .matrix import (Matrix, Vector)

TranslationType = TypeVar("D", bound="Translation")
TransformType = TypeVar("T", bound="Transform")
RotationType = TypeVar("R", bound="Rotation")


class Rotation(object):

    AXIS_X = Vector(1, 0, 0)
    AXIS_Y = Vector(0, 1, 0)
    AXIS_Z = Vector(0, 0, 1)

    def __init__(self, rotation: Optional[Matrix]=Matrix.identity(3)):

        self._rotation = rotation

    @classmethod
    def axis_angle(cls, axis: Union[tuple, Vector], angle: Number):

        if isinstance(axis, (list, tuple)):
            assert(len(axis) == 3)
            axis = Vector(*axis)

        assert(isinstance(axis, Vector))

        K = Matrix(3, 3)

        axis.normalize()

        x = axis[0, 0]
        y = axis[1, 0]
        z = axis[2, 0]

        K[0, 1] = -z
        K[0, 2] = y
        K[1, 2] = -x

        K[1, 0] = z
        K[2, 0] = -y
        K[2, 1] = x

        c = np.cos(angle)
        s = np.sin(angle)

        I = Matrix.identity(3)

        rot = I + (s * I + (1 - c) * K) * K

        return cls(rot)

    @classmethod
    def euler_angles(cls, roll, pitch, yaw):

        raise NotImplementedError()

    def __mul__(self, other: Union[RotationType, TranslationType]):

        if isinstance(other, Rotation):
            r = Rotation()
            r._rotation = self.matrix * other.matrix
            return r

        elif isinstance(other, Translation):
            t = Translation()
            t._translation = self.matrix * other.matrix
            return t

    def __imul__(self, other: RotationType):

        self._rotation *= other._rotation

        return self

    def invert(self):

        self._rotation.transpose()

    def inverse(self):

        return Rotation(self.matrix.transposed())

    @property
    def matrix(self):

        return self._rotation


class Translation(object):

    def __init__(self,
            x: Optional[Number]=0,
            y: Optional[Number]=0,
            z: Optional[Number]=0):

        self._translation = Vector(x, y, z)

    def __str__(self):
        return str(self._translation)

    @property
    def x(self):
        return self._translation[0, 0]

    @x.setter
    def x(self, value: Number):
        self._translation[0, 0] = value

    @property
    def y(self):
        return self._translation[1, 0]

    @y.setter
    def y(self, value: Number):
        self._translation[1, 0] = value

    @property
    def z(self):
        return self._translation[2, 0]

    @z.setter
    def z(self, value: Number):
        self._translation[2, 0] = value

    def __add__(self, other: TranslationType):

        return Translation(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z)

    def __neg__(self):

        return Translation(-self.x, -self.y, -self.z)

    def __sub__(self, other: TranslationType):

        return Translation(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z)

    def __mul__(self, value: Number):

        return Translation(
                value * self.x,
                value * self.y,
                value * self.z)

    def __rmul__(self, value: Number):

        return Translation(
                value * self.x,
                value * self.y,
                value * self.z)

    @property
    def matrix(self):
        return self._translation


class Transform(object):

    def __init__(self, rotation: Optional[RotationType]=None,
            translation: Optional[TranslationType]=None):

        self._rotation = rotation or Rotation()
        self._translation = translation or Translation()

    def __str__(self):
        return str(self.matrix)

    @property
    def rotation(self):
        return self._rotation

    @property
    def translation(self):
        return self._translation

    @property
    def matrix(self):
        m = Matrix.identity(4, 4)

        m[:3, :3] = self.rotation.matrix.data
        m[:3, 3:4] = self.translation.matrix.data

        return m
    def __mul__(self, other : TransformType):

        return Transform(
                self.rotation * other.rotation,
                self.rotation * other.translation + self.translation)

    def inverse(self):

        rotation = self.rotation.inverse()
        translation = rotation * (-self.translation)

        return Transform(rotation, translation)
