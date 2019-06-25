# encoding: UTF-8

from __future__ import division

import unittest
import torch.nn.init

import test.layers.boilerplate as bp
import test.layers.read_param as rp
import ptcaffe.layers.pooling_layers as pl


class TestPooling(unittest.TestCase):
    def test_aio(self):
        shape = [1, 1, 64, 64]
        x = torch.zeros(*shape)
        for param in bp.dropout(0.05, bp.generate_param(*bp.POOLING_GENERATORS)):
            layer_param = bp.layer('Pooling', param)

            module = pl.Pooling(layer_param, shape)
            self.assertEqual(module.kernel_size, rp.kernel_size(param))
            self.assertEqual(module.stride, rp.stride(param) or (64, 64))
            self.assertEqual(module.padding, rp.pad(param) or (0, 0))
            self.assertIsInstance(repr(module), str)
            if all(map(lambda p: p[0] < p[1] // 2, zip(module.padding, module.kernel_size))):
                h = module(x)
                self.assertEqual(module.forward_shape(shape), list(h.size()))
                self.assertEqual(module.forward_RF([0, 0, 1, 1]),
                                 [k - 1 for k in module.kernel_size] + list(module.stride))


class TestPooling3D(unittest.TestCase):
    def test_aio(self):
        shape = [1, 1, 64, 64, 64]
        x = torch.zeros(*shape)
        for param in bp.dropout(0.01, bp.generate_param(*bp.POOLING_GENERATORS, ndim=3)):
            if 'pad_d' in param:
                param['temporal_pad'] = param['pad_d']
            if 'kernel_d' in param:
                param['kernel_depth'] = param['kernel_d']
            if 'stride_d' in param:
                param['temporal_stride'] = param['stride_d']
            layer_param = bp.layer('Pooling3D', param)

            module = pl.Pooling3D(layer_param, shape)
            self.assertEqual(module.kernel_size, rp.kernel_size(param, ndim=3))
            self.assertEqual(module.stride, rp.stride(param, ndim=3) or (1, 1, 1))
            self.assertEqual(module.padding, rp.pad(param, ndim=3) or (0, 0, 0))
            self.assertIsInstance(repr(module), str)
            if all(map(lambda p: p[0] < p[1] // 2, zip(module.padding, module.kernel_size))):
                h = module(x)
                self.assertEqual(module.forward_shape(shape), list(h.size()))
                self.assertEqual(module.forward_RF([0, 0, 0, 1, 1, 1]),
                                 [k - 1 for k in module.kernel_size] + list(module.stride))
