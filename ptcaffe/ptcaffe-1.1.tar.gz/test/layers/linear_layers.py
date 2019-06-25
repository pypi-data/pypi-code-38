# encoding: UTF-8

from __future__ import division

import re
import unittest.mock
import ptcaffe.utils.filler
from ptcaffe.utils.config import cfg
import torch.nn.init

__XAVIER__ = ptcaffe.utils.filler.xavier_init
__MSRA__ = ptcaffe.utils.filler.msra_init
__NORMAL__ = torch.nn.init.normal_
__KAIMING__ = torch.nn.init.kaiming_normal_
__XUNIFORM__ = torch.nn.init.xavier_uniform_

ptcaffe.utils.filler.xavier_init = unittest.mock.MagicMock()
ptcaffe.utils.filler.msra_init = unittest.mock.MagicMock()
torch.nn.init.normal_ = unittest.mock.MagicMock()
torch.nn.init.kaiming_normal_ = unittest.mock.MagicMock()
torch.nn.init.xavier_uniform_ = unittest.mock.MagicMock()

import random
import test.layers.boilerplate as bp
import test.layers.read_param as rp
import ptcaffe.layers.linear_layers as ln


class TestInnerProduct(unittest.TestCase):
    def test_construction_forward_rf(self):
        for param in bp.generate_param(*bp.LINEAR_GENERATORS):
            layer_param = bp.layer('InnerProduct', param, param_key='inner_product_param')
            for ndim in [2, 3, 4, 5]:
                in_shape = [random.randint(1, 4) for _ in range(ndim)]
                module = ln.InnerProduct(layer_param, in_shape)
                if ndim <= 3:
                    self.assertEqual(module.in_channels, in_shape[-1])
                    self.assertEqual(module.forward_RF(in_shape), in_shape)
                else:
                    self.assertEqual(module.in_channels, torch.tensor(in_shape[1:]).prod().item())
                    if ndim == 4:
                        h, w = in_shape[2:]
                        self.assertEqual(module.forward_RF([0, 0, 1, 1]), [h - 1, w - 1, h, w])
                    else:
                        d, h, w = in_shape[2:]
                        self.assertEqual(module.forward_RF([0, 0, 0, 1, 1, 1]), [d - 1, h - 1, w - 1, d, h, w])
                self.assertEqual(module.out_channels, rp.num_output(param))
                self.assertEqual(module.bias is not None, rp.bias(param))
                x = torch.zeros(*in_shape)
                y = module(x)
                self.assertEqual(module.forward_shape(in_shape), list(y.size()))
                self.assertIsNotNone(re.match('InnerProduct', repr(module)))

    def test_weight_filler(self):
        param = dict(num_output=1, kernel_size=3, bias_term=False)
        vnn = cfg.DEFAULT_VARIANCE_NORM, cfg.DEFAULT_NONLINEARITY
        for weight_filler, mock, args in [
            (dict(type='xavier'), ptcaffe.utils.filler.xavier_init, vnn),
            (dict(type='msra'), ptcaffe.utils.filler.msra_init, vnn),
            (dict(type='anything_else'), torch.nn.init.xavier_uniform_, ())]:
            param['weight_filler'] = weight_filler
            layer_param = bp.layer('InnerProduct', param, param_key='inner_product_param')
            ip = ln.InnerProduct(layer_param, [1, param['num_output'], 64, 64])
            if mock is not None:
                call_args, _ = mock.call_args
                self.assertIs(ip.weight, call_args[0])

    def test_bias_filler(self):
        param = dict(num_output=6, kernel_size=3)

        value = 4172838-5
        param['bias_filler'] = dict(type='constant', value=str(value))
        layer_param = bp.layer('InnerProduct', param, param_key='inner_product_param')
        ip = ln.InnerProduct(layer_param, [1, param['num_output'], 64, 64])
        self.assertTrue((ip.bias == value).all(), 'constant filler should fill bias as expected')


class TestSparseInnerProduct(unittest.TestCase):
    def test_construction(self):
        in_channels = random.randint(1, 1024)
        param = next(bp.generate_param(*bp.POOLING_GENERATORS))
        layer_param = bp.layer('SConvolution', param, param_key='convolution_param')

        module = ln.SInnerProduct(layer_param, [1, in_channels, 64, 64])
        self.assertEqual(module.sparsity, 0.)

        sparsity = random.random()
        param['sparsity'] = str(sparsity)
        layer_param['sparse_param'] = dict(sparsity=sparsity)

        module = ln.SInnerProduct(layer_param, [1, in_channels, 64, 64])
        self.assertEqual(module.sparsity, sparsity)

    def test_set_sparsity(self):
        param = dict(num_output=1, bias_term='false')
        layer = ln.SInnerProduct(bp.layer('SInnerProduct', param, param_key='inner_product_param'), [1, 16])
        r = torch.arange(16.)
        for sparsity in [0.25, 0.5, 0.75]:
            layer.sparsity = sparsity
            with torch.no_grad():
                layer.weight.copy_(r)
            layer.set_sparsity()
            threshold = 16 * sparsity
            pivot = int(threshold)
            kernel = layer.weight.view(-1)
            self.assertTrue((kernel[:pivot] == 0).all())
            self.assertTrue((kernel[pivot:] == r[pivot:]).all())

    def test_forward(self):
        param = dict(num_output=1, bias_term='false')
        ones = torch.ones(1, 16)
        for shape in [[1, 16], [1, 1, 16], [1, 1, 4, 4], [1, 1, 2, 2, 4]]:
            layer = ln.SInnerProduct(bp.layer('SInnerProduct', param, param_key='inner_product_param'), shape)
            r = torch.arange(16.)
            for sparsity in [0.25, 0.5, 0.75]:
                layer.sparsity = sparsity
                layer.seen = 0
                with torch.no_grad():
                    layer.weight.copy_(r.view(*layer.weight.size()))
                for i in range(3):
                    h = layer(ones.view(shape))
                    if len(shape) != 5:
                        self.assertEqual(h.sum().item(), layer.weight.sum().item())
                    else:
                        self.assertTrue((h == 1).all())

