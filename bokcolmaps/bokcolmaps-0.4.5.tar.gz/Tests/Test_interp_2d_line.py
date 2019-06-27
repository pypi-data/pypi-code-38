'''Test_interp_2d_line definition'''

import unittest
import numpy
from bokcolmaps.interp_2d_line import interp_2d_line


class Test_interp_2d_line(unittest.TestCase):

    def test_single_2d_inc(self):

        x = numpy.array([0, 1])
        y = numpy.array([2, 3])
        f = numpy.array([[4, 6],
                         [5, 7]])
        c_i = numpy.array([[0.25, 2.75]])
        f_i_ref = 5.75

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertEqual(f_i[0], f_i_ref)

    def test_single_2d_dec(self):

        x = numpy.array([1, 0])
        y = numpy.array([3, 2])
        f = numpy.array([[4, 6],
                         [5, 7]])
        c_i = numpy.array([[0.25, 2.75]])
        f_i_ref = 5.25

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertEqual(f_i[0], f_i_ref)

    def test_single_2d_inc_dec(self):

        x = numpy.array([0, 1])
        y = numpy.array([3, 2])
        f = numpy.array([[4, 6],
                         [5, 7]])
        c_i = numpy.array([[0.75, 2.25]])
        f_i_ref = 6.25

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertEqual(f_i[0], f_i_ref)

    def test_single_2d_dec_inc(self):

        x = numpy.array([1, 0])
        y = numpy.array([2, 3])
        f = numpy.array([[4, 6],
                         [5, 7]])
        c_i = numpy.array([[0.75, 2.25]])
        f_i_ref = 4.75

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertEqual(f_i[0], f_i_ref)

    def test_single_2d_inc_dec_neg_vals(self):

        x = numpy.array([0, 1])
        y = numpy.array([3, 2])
        f = numpy.array([[-4, -6],
                         [-5, -7]])
        c_i = numpy.array([[0.75, 2.25]])
        f_i_ref = -6.25

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertEqual(f_i[0], f_i_ref)

    def test_single_2d_dec_inc_neg_vals_axes(self):

        x = numpy.array([-1, 0])
        y = numpy.array([-2, -3])
        f = numpy.array([[-4, -6],
                         [-5, -7]])
        c_i = numpy.array([[-0.75, -2.25]])
        f_i_ref = -4.75

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertEqual(f_i[0], f_i_ref)

    def test_2by2_2d_inside(self):

        x = numpy.array([0, 1])
        y = numpy.array([2, 3])
        f = numpy.array([[4, 6],
                         [5, 7]])
        c_i = numpy.array([[0.25, 2.5],
                           [0.5, 2.75]])
        f_i_ref = numpy.array([5.25, 6])

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.array_equal(f_i, f_i_ref))

    def test_2by3_2d_outside(self):

        x = numpy.array([0, 1])
        y = numpy.array([2, 2.5, 3])
        f = numpy.array([[4, 5, 6],
                         [5, 6, 7]])
        c_i = numpy.array([[0.25, 2.5],
                           [0.5, 2.75]])
        f_i_ref = numpy.array([5.25, 6])

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.array_equal(f_i, f_i_ref))

    def test_3by3_3d(self):

        x = numpy.array([0, 0.5, 1])
        y = numpy.array([2, 2.5, 3])
        f = numpy.zeros([5, 3, 3])
        seq = numpy.array([4, 3, 10, -1, 5])
        f[:, 0, 0] = seq
        f[:, 1, 0] = seq + 0.5
        f[:, 2, 0] = seq + 1
        f[:, 0, 1] = seq + 1
        f[:, 1, 1] = seq + 1.5
        f[:, 2, 1] = seq + 2
        f[:, 0, 2] = seq + 2
        f[:, 1, 2] = seq + 2.5
        f[:, 2, 2] = seq + 3
        c_i = numpy.array([[0.25, 2.25],
                           [0.75, 2.75]])
        f_i_ref = numpy.zeros([5, 2])
        f_i_ref[:, 0] = seq + 0.75
        f_i_ref[:, 1] = seq + 2.25
        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.array_equal(f_i, f_i_ref))

    def test_4by4_3d(self):

        x = numpy.array([0, 0.5, 1, 1.5])
        y = numpy.array([2, 2.5, 3, 3.5])
        f = numpy.zeros([5, 4, 4])
        seq = numpy.array([4, 3, 10, -1, 5])
        f[:, 0, 0] = seq
        f[:, 1, 0] = seq + 0.5
        f[:, 2, 0] = seq + 1
        f[:, 3, 0] = seq + 1.5
        f[:, 0, 1] = seq + 1
        f[:, 1, 1] = seq + 1.5
        f[:, 2, 1] = seq + 2
        f[:, 3, 1] = seq + 2.5
        f[:, 0, 2] = seq + 2
        f[:, 1, 2] = seq + 2.5
        f[:, 2, 2] = seq + 3
        f[:, 3, 2] = seq + 3.5
        f[:, 0, 3] = seq + 3
        f[:, 1, 3] = seq + 3.5
        f[:, 2, 3] = seq + 4
        f[:, 3, 3] = seq + 4.5
        c_i = numpy.array([[0.25, 2.25],
                           [1.25, 3.25]])
        f_i_ref = numpy.zeros([5, 2])
        f_i_ref[:, 0] = seq + 0.75
        f_i_ref[:, 1] = seq + 3.75
        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.array_equal(f_i, f_i_ref))

    def test_4by4_3d_not_aligned_inc(self):

        x = numpy.array([0, 0.5, 1, 1.5])
        y = numpy.array([2, 2.5, 3, 3.5])
        f = numpy.zeros([5, 4, 4])
        seq = numpy.array([4, 3, 10, -1, 5])
        f[:, 0, 0] = seq
        f[:, 1, 0] = seq + 0.5
        f[:, 2, 0] = seq + 1
        f[:, 3, 0] = seq + 1.5
        f[:, 0, 1] = seq + 1
        f[:, 1, 1] = seq + 1.5
        f[:, 2, 1] = seq + 2
        f[:, 3, 1] = seq + 2.5
        f[:, 0, 2] = seq + 2
        f[:, 1, 2] = seq + 2.5
        f[:, 2, 2] = seq + 3
        f[:, 3, 2] = seq + 3.5
        f[:, 0, 3] = seq + 3
        f[:, 1, 3] = seq + 3.5
        f[:, 2, 3] = seq + 4
        f[:, 3, 3] = seq + 4.5
        c_i = numpy.array([[1.25, 3.25],
                           [0.25, 2.25]])
        f_i_ref = numpy.zeros([5, 2])
        f_i_ref[:, 0] = seq + 3.75
        f_i_ref[:, 1] = seq + 0.75
        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.array_equal(f_i, f_i_ref))

    def test_4by4_3d_not_aligned_dec(self):

        x = numpy.array([0, 0.5, 1, 1.5])
        y = numpy.array([2, 2.5, 3, 3.5])
        x = x[::-1]
        y = y[::-1]
        f = numpy.zeros([5, 4, 4])
        seq = numpy.array([4, 3, 10, -1, 5])
        f[:, 0, 0] = seq
        f[:, 1, 0] = seq + 0.5
        f[:, 2, 0] = seq + 1
        f[:, 3, 0] = seq + 1.5
        f[:, 0, 1] = seq + 1
        f[:, 1, 1] = seq + 1.5
        f[:, 2, 1] = seq + 2
        f[:, 3, 1] = seq + 2.5
        f[:, 0, 2] = seq + 2
        f[:, 1, 2] = seq + 2.5
        f[:, 2, 2] = seq + 3
        f[:, 3, 2] = seq + 3.5
        f[:, 0, 3] = seq + 3
        f[:, 1, 3] = seq + 3.5
        f[:, 2, 3] = seq + 4
        f[:, 3, 3] = seq + 4.5
        for n in range(f.shape[0]):
            f[n] = numpy.fliplr(numpy.flipud(f[n]))
        c_i = numpy.array([[1.25, 3.25],
                           [0.25, 2.25]])
        c_i = numpy.flipud(c_i)
        f_i_ref = numpy.zeros([5, 2])
        f_i_ref[:, 0] = seq + 0.75
        f_i_ref[:, 1] = seq + 3.75
        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.array_equal(f_i, f_i_ref))

    def test_3by3_3d_neg_vals_yaxes(self):

        x = numpy.array([0, 0.5, 1])
        y = numpy.array([-2, -2.5, -3])
        f = numpy.zeros([5, 3, 3])
        seq = -numpy.array([-3, -11.6, 0, 1.3, 20])
        f[:, 0, 0] = seq
        f[:, 1, 0] = seq - 0.5
        f[:, 2, 0] = seq - 1
        f[:, 0, 1] = seq - 1
        f[:, 1, 1] = seq - 1.5
        f[:, 2, 1] = seq - 2
        f[:, 0, 2] = seq - 2
        f[:, 1, 2] = seq - 2.5
        f[:, 2, 2] = seq - 3
        c_i = numpy.array([[0, -2],
                           [0.25, -2.75],
                           [0.75, -2.25]])
        f_i_ref = numpy.zeros([5, 3])
        f_i_ref[:, 0] = seq
        f_i_ref[:, 1] = seq - 1.75
        f_i_ref[:, 2] = seq - 1.25
        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.array_equal(f_i, f_i_ref))

    def test_single_2d_invalid(self):

        x = numpy.array([0, 1])
        y = numpy.array([2, 3])
        f = numpy.array([[4, 6],
                         [5, 7]])
        c_i = numpy.array([[1.25, 2.75]])

        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.isnan(f_i[0]))

    def test_3by3_3d_invalid(self):

        x = numpy.array([0, 0.5, 1])
        y = numpy.array([2, 2.5, 3])
        f = numpy.random.rand(5, 3, 3)
        c_i = numpy.array([[0.25, 3.00001],
                           [-1, 2.25]])
        f_i, _ = interp_2d_line(x, y, f, c_i)
        self.assertTrue(numpy.all(numpy.isnan(f_i)))

if __name__ == "__main__":
    unittest.main()
