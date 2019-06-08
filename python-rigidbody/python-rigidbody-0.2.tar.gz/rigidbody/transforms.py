import numpy as np

from numbers import Number
from typing import (Optional, TypeVar, Union)

from .matrix import (Matrix, Vector)

TranslationType = TypeVar("D", bound="Translation")
TransformType = TypeVar("T", bound="Transform")
RotationType = TypeVar("R", bound="Rotation")


class Rotation(object):
    """
    The class is used to represent a rigid body rotation in 3D.
    """

    AXIS_X = Vector(1, 0, 0)
    AXIS_Y = Vector(0, 1, 0)
    AXIS_Z = Vector(0, 0, 1)

    def __init__(self, rotation: Optional[Matrix]=Matrix.identity(3)):

        self._rotation = rotation

    @classmethod
    def axis_angle(cls, axis: Union[tuple, Vector], angle: Number):
        """ Returns the rotation defined by an axis and an angle

        :param axis: a Vector defining the axis of the rotation
        :param angle: a scalar defining the angle of the rotation (radians)

        :returns: a Rotation object

        """
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

    def __mul__(self, other: Union[RotationType, TranslationType]):
        """ Returns an object rotated by this rotation

        The argument passed to this function can either a Rotation or a
        Translation. The provided object is pre-multiplied by this rotation,
        and the corresponding object type is returned (a Rotation is returned
        for a Rotation, and a Translation is returned for a Translation).

        :param other: the object to be rotated

        :returns: a Rotation or a Translation object

        """
        if isinstance(other, Rotation):
            r = Rotation()
            r._rotation = self.matrix * other.matrix
            return r

        elif isinstance(other, Translation):
            t = Translation()
            t._translation = self.matrix * other.matrix
            return t

    def __imul__(self, other: RotationType):
        """ Post-multiplies this rotation by another rotation

        :param other: the rotation to apply to this rotation

        """
        self._rotation *= other._rotation

    def invert(self):
        """ Inverts this rotation """
        self._rotation.transpose()

    def inverse(self):
        """ Returns a copy of the inverse of this rotation"""
        return Rotation(self.matrix.transposed())

    @property
    def matrix(self):
        """ The matrix that represents this rotation """
        return self._rotation


class Translation(object):
    """
    This class represents a rigid body translation in 3D.
    """

    def __init__(self,
            x: Optional[Number]=0,
            y: Optional[Number]=0,
            z: Optional[Number]=0):
        """ Creates a Translation object

        :param x: the translation in the x co-ordinate
        :param y: the translation in the y co-ordinate
        :param z: the translation in the z co-ordinate

        """
        self._translation = Vector(x, y, z)

    def __repr__(self):
        """ Returns a string representing this object """
        return repr(self._translation)

    @property
    def x(self):
        """ The x co-ordinate of the translation """
        return self._translation[0, 0]

    @x.setter
    def x(self, value: Number):
        """ Sets the value of x co-ordinate of the translation

        :param x: the new value of the x co-ordinate

        """
        self._translation[0, 0] = value

    @property
    def y(self):
        """ The y co-ordinate of the translation """
        return self._translation[1, 0]

    @y.setter
    def y(self, value: Number):
        """ Sets the value of y co-ordinate of the translation

        :param y: the new value of the y co-ordinate

        """
        self._translation[1, 0] = value

    @property
    def z(self):
        """ The z co-ordinate of the translation """
        return self._translation[2, 0]

    @z.setter
    def z(self, value: Number):
        """ Sets the value of z co-ordinate of the translation

        :param z: the new value of the z co-ordinate

        """
        self._translation[2, 0] = value

    def __add__(self, other: TranslationType):
        """ Returns the sum of this translation and another

        :param other: the translation to add to this one

        :returns: a Translation object

        """
        return Translation(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z)

    def __neg__(self):
        """ Returns the negative of this translation """
        return Translation(-self.x, -self.y, -self.z)

    def __sub__(self, other: TranslationType):
        """ Returns the difference between this translation and another

        :param other: the translation to subtract from this one

        :returns: a Translation object

        """
        return Translation(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z)

    def __mul__(self, value: Number):
        """ Returns a scaled copy of this translation

        :param value: the value to scale this translation by

        :returns: a Translation object

        """
        return Translation(
                value * self.x,
                value * self.y,
                value * self.z)

    def __rmul__(self, value: Number):
        """ Returns a scaled copy of this translation

        :param value: the value to scale this translation by

        :returns: a Translation object

        """
        return Translation(
                value * self.x,
                value * self.y,
                value * self.z)

    @property
    def matrix(self):
        """ The matrix that represents this translation """
        return self._translation


class Transform(object):
    """
    This class represents a rigid body transformation in 3D.
    """

    def __init__(self, rotation: Optional[RotationType]=None,
            translation: Optional[TranslationType]=None):
        """ Creates a Transform

        :param rotation: the rotation of the transform
        :param translation: the translation of the transform

        """
        self._rotation = rotation or Rotation()
        self._translation = translation or Translation()

    def __repr__(self):
        """ Returns a string representing the transform """
        return repr(self.matrix)

    @property
    def rotation(self):
        """ The rotation of the transform """
        return self._rotation

    @property
    def translation(self):
        """ The translation of the transform """
        return self._translation

    @property
    def matrix(self):
        """ The matrix that represents the transform """
        m = Matrix.identity(4, 4)

        m[:3, :3] = self.rotation.matrix.data
        m[:3, 3:4] = self.translation.matrix.data

        return m

    def __mul__(self, other : TransformType):
        """ Returns the product of post-multiplying this transform by another

        :param other: the transform to multiply this transform by

        :returns: a Transform object

        """
        return Transform(
                self.rotation * other.rotation,
                self.rotation * other.translation + self.translation)

    def inverse(self):
        """ Returns the inverse of this transform """
        rotation = self.rotation.inverse()
        translation = rotation * (-self.translation)

        return Transform(rotation, translation)
