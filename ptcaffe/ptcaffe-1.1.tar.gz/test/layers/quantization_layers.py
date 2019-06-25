# encoding: UTF-8

from __future__ import division

import torch
import unittest
import unittest.mock
import ptcaffe.layers.quantization_layers as Q
from ptcaffe.utils.config import cfg
import ptcaffe.layers.pooling_layers as pl


class TestQRound(unittest.TestCase):
    def test_behavior(self):
        x = torch.arange(16).float() / 4
        r = Q.QRound.apply(x).data
        y = [float(round(i / 4)) for i in range(16)]
        self.assertEqual(r.tolist(), y)

    def test_empty(self):
        x = torch.zeros(0)
        r = Q.QRound.apply(x).data
        y = []
        self.assertEqual(r.tolist(), y)

    def test_scaler(self):
        x = torch.ones(1).squeeze() / 3
        r = Q.QRound.apply(x).data
        y = 0.
        self.assertEqual(r.tolist(), y)


class TestBitsToBase(unittest.TestCase):
    def test_behavior(self):
        excepted = {1: 1, 2: 3, 3: 7, 4: 15, 8: 255}
        for x, y in excepted.items():
            self.assertEqual(Q.bits_to_base(x), y)
        self.assertRaises(TypeError, lambda: Q.bits_to_base(2333))
        self.assertRaises(TypeError, lambda: Q.bits_to_base('SOMETHING_ELSE'))


class TestQuantize(unittest.TestCase):
    def test_behavior(self):
        # should quantize following numbers ...
        xs = 42 + torch.FloatTensor([
            0, 1 / 23, 1 / 17, 1 / 13, 1 / 11, 1 / 7, 1 / 5, 1 / 3, 5 / 14,
            1 / 2, 24 / 35, 29 / 35, 1
        ])
        qs = Q.quantize(xs, bits=3).data
        # ... to 42 + k / 7 where 0 <= k <= 7
        ys = 42 + torch.FloatTensor([
            0, 0, 0, 1 / 7, 1 / 7, 1 / 7, 1 / 7, 2 / 7, 3 / 7, 4 / 7, 5 / 7,
            6 / 7, 1
        ])
        self.assertEqual(float(qs.min()), float(xs.min()), msg='it should find out correct minimum')
        self.assertEqual(float(qs.max()), float(xs.max()), msg='it should find out correct maximum')
        self.assertEqual(len(set(qs.tolist())), 8, msg='it should map `xs` to a discrate value set')
        self.assertEqual(qs.tolist(), ys.tolist(), msg='it should quantize `xs` as excepted')


class TestStructure(unittest.TestCase):
    def test_inheritance(self):
        self.assertTrue(issubclass(Q.QConvolution, Q.QuantizationMixin))
        self.assertTrue(issubclass(Q.QInnerProduct, Q.QuantizationMixin))
        self.assertTrue(issubclass(Q.QPooling, Q.QuantizationMixin))
        self.assertTrue(issubclass(Q.QReLU, Q.QuantizationMixin))


class TestMixin(unittest.TestCase):
    def setUp(self):
        class Mixin(torch.nn.Module, Q.QuantizationMixin):
            def __init__(self, *args):
                torch.nn.Module.__init__(self)
                Q.QuantizationMixin.__init__(self, *args)

        self.Mixin = Mixin

    def test_construction(self):
        layer, param = {}, {}
        mixin = self.Mixin(layer, None)
        self.assertTrue((mixin.minval == 0).all())
        self.assertEqual(mixin.minval.numel(), 1)
        self.assertTrue((mixin.maxval == 0).all())
        self.assertEqual(mixin.maxval.numel(), 1)

        layer['quantization_param'] = param
        self.assertEqual(self.Mixin(layer, None).momentum, 0.999)

        param['momentum'] = '0.125'
        self.assertEqual(self.Mixin(layer, None).momentum, 0.125)

    def test_update_minmax(self):
        x = torch.tensor([-1., 1.])
        mixin = self.Mixin(dict(quantization_param=dict(momentum=0.5)), None)
        for _ in range(10):
            mixin.update_min_max(x)
        self.assertAlmostEqual(mixin.maxval.item(), 1, delta=1e-3)
        self.assertAlmostEqual(mixin.minval.item(), -1, delta=1e-3)

    def test_post_process(self):
        x = torch.arange(4).float()
        mixin = self.Mixin(dict(quantization_param=dict(momentum=0.5)), None)

        cfg.QUANTIZATION = False
        mixin.update_min_max = unittest.mock.MagicMock()
        mixin.post_forward(x)
        mixin.update_min_max.assert_called_once()
        self.assertIs(mixin.update_min_max.call_args[0][0], x)

        cfg.QUANTIZATION = True
        quantize = Q.quantize
        Q.quantize = unittest.mock.MagicMock()
        mixin.post_forward(x)
        Q.quantize.assert_called_once()
        self.assertIs(Q.quantize.call_args[0][0], x)
        Q.quantize = quantize


class TestQLayers(unittest.TestCase):
    def test_conv(self):
        conv = Q.QConvolution(dict(convolution_param=dict(num_output=1, kernel_size=3)), [1, 1, 3, 3])
        x = torch.zeros(1, 1, 3, 3)
        cfg.QUANTIZATION = True
        conv(x).mean().backward()
        cfg.QUANTIZATION = False
        conv(x).mean().backward()
        self.assertTrue(repr(conv).startswith('QConvolution'))

    def test_linear(self):
        linear = Q.QInnerProduct(dict(inner_product_param=dict(num_output=1)), [1, 8])
        x = torch.zeros(1, 8)
        cfg.QUANTIZATION = True
        linear(x).mean().backward()
        cfg.QUANTIZATION = False
        linear(x).mean().backward()
        self.assertTrue(repr(linear).startswith('QInnerProduct'))

    def test_pool(self):
        pool = Q.QPooling(dict(top='x', bottom='x', pooling_param=dict(pool='MAX', kernel_size=2)), [1, 1, 4, 4])
        x = torch.rand(1, 1, 4, 4)
        rf = pl.Pooling.forward
        pl.Pooling.forward = unittest.mock.MagicMock()
        pool.post_forward = unittest.mock.MagicMock()

        cfg.QUANTIZATION = True
        pool(x).mean().backward()
        pl.Pooling.forward.assert_called_once()
        pool.post_forward.assert_called_once()

        pl.Pooling.forward = unittest.mock.MagicMock()
        pool.post_forward = unittest.mock.MagicMock()

        cfg.QUANTIZATION = False
        pool(x).mean().backward()
        pl.Pooling.forward.assert_called_once()
        pool.post_forward.assert_called_once()

        pl.Pooling.forward = rf
        self.assertTrue(repr(pool).startswith('QMaxPool2d'))

    def test_relu(self):
        relu = Q.QReLU(dict(top='x', bottom='x'), [])
        x = torch.rand(1, 2, 3, 4)
        rf = torch.nn.ReLU.forward
        torch.nn.ReLU.forward = unittest.mock.MagicMock()
        relu.post_forward = unittest.mock.MagicMock()

        cfg.QUANTIZATION = True
        relu(x).mean.backwad()

        cfg.QUANTIZATION = False
        torch.nn.ReLU.forward = unittest.mock.MagicMock()
        relu.post_forward = unittest.mock.MagicMock()
        relu(x).mean.backwad()

        torch.nn.ReLU.forward.assert_called_once()
        relu.post_forward.assert_called_once()
        torch.nn.ReLU.forward = rf
        self.assertTrue(repr(relu).startswith('QReLU'))

