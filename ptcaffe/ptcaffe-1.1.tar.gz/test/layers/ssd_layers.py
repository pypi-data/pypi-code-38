import torch
import unittest
from torch.autograd import Variable
from ptcaffe.layers.ssd_layers import Slice


class TestSlice(unittest.TestCase):
    def setUp(self):
        self.layer = Slice(dict(top=['x', 'y', 'z'], slice_param=dict(axis=3, slice_point=[5, 10])), None)

    def test_forward_shape(self):
        xs = self.layer.forward_shape([4, 7, 11, 17])
        ys = [4, 7, 11, 5], [4, 7, 11, 5], [4, 7, 11, 7]
        self.assertEqual(xs, ys)

    def test_forward(self):
        xs = torch.arange(17).view(1, 1, 1, -1)
        xs = Variable(xs)
        y1 = torch.arange(5).view(1, 1, 1, -1)
        y2 = torch.arange(5).view(1, 1, 1, -1) + 5
        y3 = torch.arange(7).view(1, 1, 1, -1) + 10
        x1, x2, x3 = self.layer(xs)
        self.assertEqual(x1.data.tolist(), y1.tolist())
        self.assertEqual(x2.data.tolist(), y2.tolist())
        self.assertEqual(x3.data.tolist(), y3.tolist())
