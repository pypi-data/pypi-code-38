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
    msg = "tried to multiply a {} and {} matrix"


class MatrixSubtractionSizeError(MatrixSizeError):
    msg = "tried to subtract a {} matrix from a {} matrix"


class MatrixAdditionSizeError(MatrixSizeError):
    msg = "tried to add a {} matrix from a {} matrix"


class Matrix(object):

    def __init__(self, rows: int, cols: int):

        self._rows = rows
        self._cols = cols
        self._data = np.zeros((rows, cols))

    @classmethod
    def zero(cls, rows: int, cols: Optional[int]=1):
        m = cls(rows, cols)
        m._data = np.zeros((rows, cols))
        return m

    @classmethod
    def identity(cls, rows: int, cols: Optional[int]=None):
        if cols is None:
            cols = rows

        m = cls(rows, cols)
        m._data = np.eye(rows, cols)
        return m

    def __repr__(self):
        return repr(self._data)

    def __add__(self, other: MatrixType):

        if self.size != other.size:
            raise MatrixAdditionSizeError(self, other)

        m = Matrix(self.rows, self.cols)
        m._data = self._data + other._data

        return m

    def __iadd__(self, other: MatrixType):

        if self.size != other.size:
            raise MatrixAdditionSizeError(self, other)

        self._data += other._data

        return self

    def __sub__(self, other: MatrixType):

        if self.size != other.size:
            raise MatrixSubtractionSizeError(self, other)

        m = Matrix(self.rows, self.cols)
        m._data = self._data - other._data

        return m

    def __isub__(self, other: MatrixType):

        if self.size != other.size:
            raise MatrixSubtractionSizeError(self, other)

        self._data -= other._data

        return self

    def __mul__(self, other : Union[Number, MatrixType]):

        if self.cols != other.rows:
            raise MatrixMultiplySizeError(self, other)

        if isinstance(other, Number):

            m = Matrix(self.rows, self.cols)
            m._data = other * np.array(self._data)

            return m

        elif isinstance(other, Matrix):

            assert(self.cols == other.rows)

            m = Matrix(self.rows, other.cols)
            m._data = np.matmul(self._data, other._data)

            return m

    def __rmul__(self, other: Number):

        m = Matrix(self.rows, self.cols)
        m._data = other * np.array(self._data)

        return m

    def __truediv__(self, value: Number):

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
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def size(self):
        return (self.rows, self.cols)

    @property
    def data(self):
        return self._data

    def transpose(self):
        self._data.transpose()

    def transposed(self):

        m = Matrix(self.cols, self.rows)
        m._data = np.array(self._data).transpose()

        return m

    def norm(self):
        return np.linalg.norm(self._data)


class Vector(Matrix):

    def __init__(self, *values):

        super(Vector, self).__init__(len(values), 1)

        self._data[:,0] = values

    def normalize(self):

        assert(self.norm() != 0)

        self._data /= self.norm()

    @classmethod
    def e(cls, rows: int, index: int):

        return cls(*[0 if i != index else 1 for i in range(rows)])


def approx(A: Matrix, B: Matrix, tol: Optional[float]=0.001):

    return np.all(np.fabs(A._data - B._data) < tol)


def dot(u: Vector, v: Vector):

    return (u.transposed() * v)[0, 0]


def cross(u: Vector, v: Vector):

    return Vector(*list(np.cross(u._data.flatten(), v._data.flatten())))


def svd(A: Matrix):

    u, s, vh = np.linalg.svd(A._data, full_matrices=True)

    U = Matrix(A.rows, A.rows)
    S = Matrix(A.rows, A.cols)
    V = Matrix(A.cols, A.cols)

    U._data = u
    S._data = np.diag(s)
    V._data = vh.transpose()

    return (U, S, V)
