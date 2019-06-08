import numpy as np

from numbers import Number
from typing import (Optional, TypeVar, Union)

MatrixType = TypeVar("M", bound="Matrix")


class MatrixSizeError(Exception):
    def __init__(self, a, b):
        super(MatrixSizeError, self).__init__(self.msg.format(
                "{}x{}".format(a.rows, a.cols),
                "{}x{}".format(b.rows, b.cols),
                ))


class MatrixMultiplySizeError(MatrixSizeError):
    msg = "tried to multiply a {} and a {} matrix"


class MatrixSubtractionSizeError(MatrixSizeError):
    msg = "tried to subtract a {} matrix from a {} matrix"


class MatrixAdditionSizeError(MatrixSizeError):
    msg = "tried to add a {} matrix from a {} matrix"


class Matrix(object):
    """
    The Matrix class represents the M x N array numbers commonly used in linear
    algebra.
    """

    def __init__(self, rows: int, cols: int):
        """ Creates an instance of Matrix

        :param rows: the number of rows in the matrix
        :param cols: the number of columns in the matrix

        """
        self._rows = rows
        self._cols = cols
        self._data = np.zeros((rows, cols))

    @classmethod
    def zero(cls, rows: int, cols: Optional[int]=1):
        """ Returns a zero matrix

        The matrix returns by this function contains zeros in all of its
        elements.

        :param rows: the number of rows in the matrix
        :param cols: the number of columns in the matrix

        :returns: a Matrix object

        """
        m = cls(rows, cols)
        m._data = np.zeros((rows, cols))
        return m

    @classmethod
    def identity(cls, rows: int, cols: Optional[int]=None):
        """ Returns the identity matrix

        The matrix returned by this function contains zeros in all of its
        elements except for those along the diagonal, which are all ones.


        :param rows: the number of rows in the matrix
        :param cols: the number of columns in the matrix

        :returns: a Matrix object

        """
        # By default, the matrix is square
        if cols is None:
            cols = rows

        m = cls(rows, cols)
        m._data = np.eye(rows, cols)

        return m

    def __repr__(self):
        """Returns a string representing the object"""
        return repr(self._data)

    def __add__(self, other: MatrixType):
        """ Returns the sum of this matrix and another

        :param other: the matrix to add to this one.
        :raises MatrixAdditionSizeError: if the matrix sizes are not equal

        :returns: a Matrix object

        """
        if self.size != other.size:
            raise MatrixAdditionSizeError(self, other)

        m = Matrix(self.rows, self.cols)
        m._data = self._data + other._data

        return m

    def __iadd__(self, other: MatrixType):
        """ Adds a matrix to this one

        :param other: the matrix to add to this one.
        :raises MatrixAdditionSizeError: if the matrix sizes are not equal

        """
        if self.size != other.size:
            raise MatrixAdditionSizeError(self, other)

        self._data += other._data

    def __sub__(self, other: MatrixType):
        """ Returns the difference between this matrix and another

        :param other: the matrix to subtracted from this one.
        :raises MatrixAdditionSizeError: if the matrix sizes are not equal

        :returns: a Matrix object

        """
        if self.size != other.size:
            raise MatrixSubtractionSizeError(self, other)

        m = Matrix(self.rows, self.cols)
        m._data = self._data - other._data

        return m

    def __isub__(self, other: MatrixType):
        """ Subtracts a matrix from this one

        :param other: the matrix to subtract from this one.
        :raises MatrixAdditionSizeError: if the matrix sizes are not equal

        """
        if self.size != other.size:
            raise MatrixSubtractionSizeError(self, other)

        self._data -= other._data

        return self

    def __mul__(self, other : Union[Number, MatrixType]):
        """ Returns the product of this matrix and another matrix or scalar

        If a scalar is passed as the argument to this function, the matrix
        returned is a scaled version of this matrix. If the argument is a
        matrix, the result is the product of this matrix post-multiplied by the
        other matrix.


        :param other: the matrix/scalar to multiply with this matrix
        :raises MatrixMultiplySizeError: if the matrices have different sizes

        :returns: a Matrix object

        """
        if isinstance(other, Number):

            m = Matrix(self.rows, self.cols)
            m._data = other * np.array(self._data)

            return m

        elif isinstance(other, Matrix):

            if self.cols != other.rows:
                raise MatrixMultiplySizeError(self, other)

            m = Matrix(self.rows, other.cols)
            m._data = np.matmul(self._data, other._data)

            return m

    def __rmul__(self, other: Number):
        """ Returns a scaled version of this matrix

        :param other: a scalar

        :returns: a Matrix object

        """
        m = Matrix(self.rows, self.cols)
        m._data = other * np.array(self._data)

        return m

    def __truediv__(self, value: Number):
        """ Returns a copy of this matrix divided by a scalar

        :param value: the scalar to divide the matrix by
        :raises ZeroDivisionError: if the value is zero

        :returns: a Matrix object

        """
        if value == 0:
            raise ZeroDivisionError()

        m = Matrix(self.rows, self.cols)
        m._data = self._data / value

        return m

    def __neg__(self):

        m = Matrix(self.rows, self.cols)
        m._data = -self._data

        return m

    def __eq__(self, other: MatrixType):

        return np.all(self._data == other._data)

    def __getitem__(self, range: tuple):
        return self._data.__getitem__(range)

    def __setitem__(self, range: tuple, value):

        if isinstance(value, Matrix):

            data = value._data

            if min(data.shape) == 1:
                data = data.flatten()

            return self._data.__setitem__(range, data)

        return self._data.__setitem__(range, value)

    @property
    def rows(self):
        """The number of rows in the matrix"""
        return self._rows

    @property
    def cols(self):
        """The number of columns in the matrix"""
        return self._cols

    @property
    def size(self):
        """The size (tuple of rows and columns) of the matrix"""
        return (self.rows, self.cols)

    @property
    def data(self):
        """The underlying numpy array containing the matrix data"""
        return self._data

    def transpose(self):
        """Transposes the matrix"""
        self._data.transpose()

    def transposed(self):
        """Returns a transposed copy of the matrix"""
        m = Matrix(self.cols, self.rows)
        m._data = np.array(self._data).transpose()

        return m

    def norm(self):
        """Returns the L2 norm of the matrix"""
        return np.linalg.norm(self._data)


class Vector(Matrix):
    """
    The Vector class is a special case of a matrix where the number of columns
    equals one.
    """

    def __init__(self, *values):
        """ Creates a Vector from the provided values

        :param values: the elements of the vector

        """
        super(Vector, self).__init__(len(values), 1)

        self._data[:,0] = values

    def normalize(self):
        """ Ensures the Vector is unit length """
        assert(self.norm() != 0)

        self._data /= self.norm()

    @classmethod
    def e(cls, rows: int, index: int):
        """ Returns a one-hot Vector

        This function creates a Vector object where every element is zero
        except for one, which is equal to one.

        :param rows: the number of rows in the Vector
        :param index: the index of the element that contains the one

        :returns: a Vector object

        """
        return cls(*[0 if i != index else 1 for i in range(rows)])


def approx(A: Matrix, B: Matrix, tol: Optional[float]=0.001):
    """Returns True if the matrices are approximately equal

    :param A: a Matrix object
    :param B: a Matrix object
    :param tol: the tolerance used to determine the near equality of elements

    :returns: a boolean

    """
    return np.all(np.fabs(A._data - B._data) < tol)


def dot(u: Vector, v: Vector):
    """Returns the dot product of two vectors

    :param u: a vector
    :param v: a vector

    :returns: a scalar value

    """
    return (u.transposed() * v)[0, 0]


def cross(u: Vector, v: Vector):
    """Returns the cross product of two vectors

    :param u: a vector
    :param v: a vector

    :returns: a Vector object

    """
    return Vector(*list(np.cross(u._data.flatten(), v._data.flatten())))


def svd(A: Matrix):
    """Returns the singular value decomposition of a matrix

    :param A: the matrix to decompose

    :returns: a tuple of the (U, S, V) matrices

    """
    u, s, vh = np.linalg.svd(A._data, full_matrices=True)

    U = Matrix(A.rows, A.rows)
    S = Matrix(A.rows, A.cols)
    V = Matrix(A.cols, A.cols)

    U._data = u
    S._data = np.diag(s)
    V._data = vh.transpose()

    return (U, S, V)
