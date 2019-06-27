'''InterpTest class definition'''

import unittest
import numpy
from ..interp_data import interp_data
from time import time


class InterpTest(unittest.TestCase):
    '''
    Test class for interp_data function.
    '''

    def setUp(self):
        self.data_t = numpy.random.rand(2, 3, 4)
        self.dims = self.data_t.shape
        self.x_t = numpy.linspace(1, 10, self.dims[2])
        self.y_t = numpy.linspace(4, 12, self.dims[1])

    def tearDown(self):
        pass

    def test_2d_x(self):

        x_t = self.x_t**2
        y_t = self.y_t
        data_t = self.data_t[0]

        x_int = numpy.min(numpy.diff(x_t))
        n_pts = int(numpy.round((x_t[-1] - x_t[0])/x_int)) + 1
        x_t_i = numpy.linspace(x_t[0], x_t[-1], n_pts)
        npts = x_t_i.size

        data_c = numpy.zeros([self.dims[1], npts])

        for yi in range(self.dims[1]):
            data_c[yi] = numpy.interp(x_t_i, x_t, data_t[yi])

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t_i))
        self.assertTrue(numpy.array_equal(test_y_t, y_t))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_2d_y(self):

        x_t = self.x_t
        y_t = self.y_t**2
        data_t = self.data_t[1]

        y_int = numpy.min(numpy.diff(y_t))
        n_pts = int(numpy.round((y_t[-1] - y_t[0])/y_int)) + 1
        y_t_i = numpy.linspace(y_t[0], y_t[-1], n_pts)
        npts = y_t_i.size

        data_c = numpy.zeros([npts, self.dims[2]])

        for xi in range(self.dims[2]):
            data_c[:, xi] = numpy.interp(y_t_i, y_t, data_t[:, xi])

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t))
        self.assertTrue(numpy.array_equal(test_y_t, y_t_i))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_2d_x_neg(self):

        x_t = -(self.x_t**2)
        y_t = self.y_t
        data_t = self.data_t[0]

        x_int = numpy.min(numpy.abs(numpy.diff(x_t)))
        n_pts = int(numpy.round((x_t[0] - x_t[-1])/x_int)) + 1
        x_t_i = numpy.linspace(-x_t[0], -x_t[-1], n_pts)
        npts = x_t_i.size

        data_c = numpy.zeros([self.dims[1], npts])

        for yi in range(self.dims[1]):
            data_c[yi] = numpy.interp(x_t_i, -x_t, data_t[yi])

        x_t_i = -x_t_i

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t_i))
        self.assertTrue(numpy.array_equal(test_y_t, y_t))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_2d_y_neg(self):

        x_t = self.x_t
        y_t = -(self.y_t**2)
        data_t = self.data_t[1]

        y_int = numpy.min(numpy.abs(numpy.diff(y_t)))
        n_pts = int(numpy.round((y_t[0] - y_t[-1])/y_int)) + 1
        y_t_i = numpy.linspace(-y_t[0], -y_t[-1], n_pts)
        npts = y_t_i.size

        data_c = numpy.zeros([npts, self.dims[2]])

        for xi in range(self.dims[2]):
            data_c[:, xi] = numpy.interp(y_t_i, -y_t, data_t[:, xi])

        y_t_i = -y_t_i

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t))
        self.assertTrue(numpy.array_equal(test_y_t, y_t_i))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_2d_x_rev(self):

        x_t = numpy.flipud(self.x_t**2)
        y_t = self.y_t
        data_t = self.data_t[1]

        x_int = numpy.min(numpy.abs(numpy.diff(x_t)))
        n_pts = int(numpy.round((x_t[0] - x_t[-1])/x_int)) + 1
        x_t_i = numpy.linspace(x_t[-1], x_t[0], n_pts)
        npts = x_t_i.size

        data_c = numpy.zeros([self.dims[1], npts])

        for yi in range(self.dims[1]):
            data_c[yi] = numpy.interp(x_t_i, numpy.flipud(x_t),
                                      numpy.flipud(data_t[yi]))

        x_t_i = numpy.flipud(x_t_i)
        data_c = numpy.fliplr(data_c)

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t_i))
        self.assertTrue(numpy.array_equal(test_y_t, y_t))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_2d_y_rev(self):

        x_t = self.x_t
        y_t = numpy.flipud(self.y_t**2)
        data_t = self.data_t[1]

        y_int = numpy.min(numpy.abs(numpy.diff(y_t)))
        n_pts = int(numpy.round((y_t[0] - y_t[-1])/y_int)) + 1
        y_t_i = numpy.linspace(y_t[-1], y_t[0], n_pts)
        npts = y_t_i.size

        data_c = numpy.zeros([npts, self.dims[2]])

        for xi in range(self.dims[2]):
            data_c[:, xi] = numpy.interp(y_t_i, numpy.flipud(y_t),
                                         numpy.flipud(data_t[:, xi]))

        y_t_i = numpy.flipud(y_t_i)
        data_c = numpy.flipud(data_c)

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t))
        self.assertTrue(numpy.array_equal(test_y_t, y_t_i))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_3d_x_neg(self):

        x_t = -(self.x_t**2)
        y_t = self.y_t
        data_t = self.data_t

        x_int = numpy.min(numpy.abs(numpy.diff(x_t)))
        n_pts = int(numpy.round((x_t[0] - x_t[-1])/x_int)) + 1
        x_t_i = numpy.linspace(-x_t[0], -x_t[-1], n_pts)
        npts = x_t_i.size

        data_c = numpy.zeros([self.dims[0], self.dims[1], npts])

        for zi in range(self.dims[0]):
            for yi in range(self.dims[1]):
                data_c[zi, yi] = numpy.interp(x_t_i, -x_t, data_t[zi, yi])

        x_t_i = -x_t_i

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t_i))
        self.assertTrue(numpy.array_equal(test_y_t, y_t))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_3d_y_rev(self):

        x_t = self.x_t
        y_t = numpy.flipud(self.y_t)
        data_t = self.data_t

        y_int = numpy.min(numpy.abs(numpy.diff(y_t)))
        n_pts = int(numpy.round((y_t[0] - y_t[-1])/y_int)) + 1
        y_t_i = numpy.linspace(y_t[-1], y_t[0], n_pts)
        npts = y_t_i.size

        data_c = numpy.zeros([self.dims[0], npts, self.dims[2]])

        for zi in range(self.dims[0]):
            for xi in range(self.dims[2]):
                data_c[zi, :, xi] = numpy.interp(y_t_i, numpy.flipud(y_t),
                                                 numpy.flipud(data_t[zi, :, xi]))

        y_t_i = numpy.flipud(y_t_i)
        for zi in range(self.dims[0]):
            data_c[zi] = numpy.flipud(data_c[zi])

        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t)

        self.assertTrue(numpy.array_equal(test_x_t, x_t))
        self.assertTrue(numpy.array_equal(test_y_t, y_t_i))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_3d_x_big(self):

        data_t = numpy.random.rand(10, 100, 100)
        dims = data_t.shape
        x_t = numpy.linspace(0, 100, dims[2])**2
        y_t = numpy.linspace(0, 100, dims[1])

        t0 = time()

        x_int = numpy.min(numpy.diff(x_t))
        n_pts = int(numpy.round((x_t[-1] - x_t[0])/x_int)) + 1
        x_t_i = numpy.linspace(x_t[0], x_t[-1], n_pts)
        npts = x_t_i.size

        data_c = numpy.zeros([dims[0], dims[1], npts])

        for zi in range(dims[0]):
            for yi in range(dims[1]):
                data_c[zi, yi] = numpy.interp(x_t_i, x_t, data_t[zi, yi])

        t1 = time()
        t_orig = t1 - t0

        t0 = time()
        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t,
                                                      nu_tol=1e-6)
        t1 = time()
        t_flat = t1 - t0

        print('Speedup factor (x) = ' + str(t_orig/t_flat))

        self.assertTrue(numpy.array_equal(test_x_t, x_t_i))
        self.assertTrue(numpy.array_equal(test_y_t, y_t))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

    def test_3d_y_big(self):

        data_t = numpy.random.rand(10, 100, 100)
        dims = data_t.shape
        x_t = numpy.linspace(0, 100, dims[2])
        y_t = numpy.linspace(0, 100, dims[1])**2

        t0 = time()

        y_int = numpy.min(numpy.diff(y_t))
        n_pts = int(numpy.round((y_t[-1] - y_t[0])/y_int)) + 1
        y_t_i = numpy.linspace(y_t[0], y_t[-1], n_pts)
        npts = y_t_i.size

        data_c = numpy.zeros([dims[0], npts, dims[2]])

        for zi in range(dims[0]):
            for xi in range(dims[2]):
                data_c[zi, :, xi] = numpy.interp(y_t_i, y_t, data_t[zi, :, xi])

        t1 = time()
        t_orig = t1 - t0

        t0 = time()
        test_x_t, test_y_t, test_data_t = interp_data(x_t, y_t, data_t,
                                                      nu_tol=1e-6)
        t1 = time()
        t_flat = t1 - t0

        print('Speedup factor (y) = ' + str(t_orig/t_flat))

        self.assertTrue(numpy.array_equal(test_x_t, x_t))
        self.assertTrue(numpy.array_equal(test_y_t, y_t_i))
        self.assertTrue(numpy.array_equal(test_data_t, data_c))

if __name__ == "__main__":
    unittest.main()
