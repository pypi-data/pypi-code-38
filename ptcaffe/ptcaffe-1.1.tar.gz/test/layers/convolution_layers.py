# encoding: UTF-8

from __future__ import division

import unittest.mock
import ptcaffe.utils.filler
from ptcaffe.utils.config import cfg
import torch.nn.init
import math


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
import ptcaffe.layers.convolution_layers as cc


class TestConvolution(unittest.TestCase):
    def test_construction_2d(self):
        for param in bp.dropout(0.01, bp.generate_param(*bp.CONVOLUTION_GENERATORS)):
            layer_param = bp.layer('Convolution', param)
            in_channels = random.randint(1, 1024)

            module = cc.Convolution(layer_param, [1, in_channels, 64, 64])
            self.assertEqual(module.in_channels, in_channels)
            self.assertEqual(module.out_channels, rp.num_output(param))
            self.assertEqual(module.kernel_size, rp.kernel_size(param))
            self.assertEqual(module.stride, rp.stride(param) or (1, 1))
            self.assertEqual(module.padding, rp.pad(param) or (0, 0))
            self.assertEqual(module.dilation[0], rp.dilation(param))
            self.assertEqual(module.bias is not None, rp.bias(param))

    def test_weight_filler_2d(self):
        param = dict(num_output=1, kernel_size=3, bias_term=False)
        vnn = cfg.DEFAULT_VARIANCE_NORM, cfg.DEFAULT_NONLINEARITY
        for weight_filler, mock, args in [
            (dict(type='xavier'), ptcaffe.utils.filler.xavier_init, vnn),
            (dict(type='msra'), ptcaffe.utils.filler.msra_init, vnn),
            (dict(type='gaussian', std='42'), torch.nn.init.normal_, (0, 42.)),
            (dict(type='unitzero'), None, ()),
            (dict(type='none'), None, ())]:
            param['weight_filler'] = weight_filler
            layer_param = bp.layer('Convolution', param)
            conv = cc.Convolution(layer_param, [1, param['num_output'], 64, 64])
            if mock is not None:
                call_args, _ = mock.call_args
                self.assertTrue(conv.weight is call_args[0] or conv.weight.data is call_args[0])
                for actual, expected in zip(call_args[1:], args):
                    self.assertEqual(actual, expected)
        param['weight_filler'] = dict(type='unknown filler type should trigger a ValueError')
        layer_param = bp.layer('Convolution', param)
        self.assertRaises(ValueError, cc.Convolution, layer_param, [1, 1, 64, 64])

    def test_bias_filler_2d(self):
        param = dict(num_output=6, kernel_size=3)

        value = 4172838-5
        param['bias_filler'] = dict(type='constant', value=str(value))
        conv = cc.Convolution(bp.layer('Convolution', param), [1, 1, 64, 64])
        self.assertTrue((conv.bias == value).all(), 'constant filler should fill bias as expected')

        param['bias_filler'] = dict(type='yolo_bias', num_anchors='2')
        conv = cc.Convolution(bp.layer('Convolution', param), [1, 1, 64, 64])
        bias = conv.bias.view(2, 3)
        self.assertTrue((bias[:, 2] == 0).all(), 'bias[:, 2:] should be set to 0')
        self.assertTrue((bias[:, 0:2] == 0.5).all(), 'bias[:, 0:2] should be set to 0.5')

        param['bias_filler'] = dict(type='focal', pi='0.25', index='1')
        conv = cc.Convolution(bp.layer('Convolution', param), [1, 16, 64, 64])
        self.assertAlmostEqual(conv.bias[1], -math.log(3), 5, 'focal filler set bias[index] = -log((1 - pi) / pi)')
        conv.bias[1] = 0
        self.assertTrue((conv.bias == 0).all(), 'and other elements to 0')

        param['bias_filler'] = dict(type='none')
        conv = cc.Convolution(bp.layer('Convolution', param), [1, 1, 64, 64])
        self.assertTrue(True, 'none filler leaves bias untouched')

        param['bias_filler'] = dict(type='unknown filler type should trigger a ValueError')
        layer_param = bp.layer('Convolution', param)
        self.assertRaises(ValueError, cc.Convolution, layer_param, [1, 1, 64, 64])

    def test_forward_shape_rf_2d(self):
        param = dict(num_output=5, kernel_size=3)
        conv = cc.Convolution(bp.layer('Convolution', param), [1, 1, 4, 4])
        fs = conv.forward_shape([1, 1, 4, 4])
        self.assertEqual(fs, [1, 5, 2, 2])
        rf = conv.forward_RF([1, 1, 1, 1])
        self.assertEqual(rf, [3, 3, 1, 1])


class TestConvolution3D(unittest.TestCase):
    def test_construction_3d(self):
        for param in bp.dropout(0.0001, bp.generate_param(*bp.CONVOLUTION_GENERATORS, ndim=3)):
            if 'stride_d' in param and random.random() > 0.5:
                param['temporal_stride'] = param['stride_d']
            layer = bp.layer('Convolution3D', bp.rename(param, dict(kernel_d='kernel_depth', pad_d='temporal_pad')))
            in_channels = random.randint(1, 1024)

            module = cc.Convolution3D(layer, [1, in_channels, 64, 64, 64])
            self.assertEqual(module.in_channels, in_channels)
            self.assertEqual(module.out_channels, rp.num_output(param))
            self.assertEqual(module.kernel_size, rp.kernel_size(param, ndim=3))
            self.assertEqual(module.stride, rp.stride(param, ndim=3) or (1, 1, 1))
            self.assertEqual(module.padding, rp.pad(param, ndim=3) or (0, 0, 0))
            self.assertEqual(module.dilation[0], rp.dilation(param))
            self.assertEqual(module.bias is not None, rp.bias(param))

    def test_weight_filler_3d(self):
        param = dict(num_output=1, kernel_size=3, bias_term=False)
        layer_param = bp.layer('Convolution3D', param)

        for weight_filler, mock, args in [
            (dict(type='xavier'), torch.nn.init.xavier_uniform_, ()),
            (dict(type='xavier'), torch.nn.init.xavier_uniform_, (87.3365,)),
            (dict(type='msra', variance_norm='FAN_IN'), torch.nn.init.kaiming_normal_, ('FAN_IN',)),
            (dict(type='msra', variance_norm='ANY_THING_ELSE'), torch.nn.init.kaiming_normal_, ('FAN_OUT',)),
            (dict(type='gaussian', std='42'), torch.nn.init.normal_, (0, 42.)),
            (dict(type='unitzero'), None, ()),
            (dict(type='none'), None, ())]:
            param['weight_filler'] = weight_filler
            conv = cc.Convolution3D(layer_param, [1, 64, param['num_output'], 64, 64])
            if mock is not None:
                call_args, _ = mock.call_args
                self.assertTrue(conv.weight is call_args[0] or conv.weight.data is call_args[0])
                for actual, expected in zip(call_args[1:], args):
                    self.assertEqual(actual, expected)
        param['weight_filler'] = dict(type='unknown filler type should trigger a ValueError')
        layer_param = bp.layer('Convolution', param)
        self.assertRaises(ValueError, cc.Convolution, layer_param, [1, 1, 64, 64])

    def test_bias_filler_3d(self):
        param = dict(num_output=6, kernel_size=3)

        value = 4172838-5
        param['bias_filler'] = dict(type='constant', value=str(value))
        conv = cc.Convolution3D(bp.layer('Convolution3D', param), [1, 1, 64, 64])
        self.assertTrue((conv.bias == value).all(), 'constant filler should fill bias as expected')

        param['bias_filler'] = dict(type='yolo_bias', num_anchors='2')
        conv = cc.Convolution3D(bp.layer('Convolution3D', param), [1, 1, 64, 64])
        bias = conv.bias.view(2, 3)
        self.assertTrue((bias[:, 2] == 0).all(), 'bias[:, 2:] should be set to 0')
        self.assertTrue((bias[:, 0:2] == 0.5).all(), 'bias[:, 0:2] should be set to 0.5')

        param['bias_filler'] = dict(type='focal', pi='0.25', index='1')
        conv = cc.Convolution3D(bp.layer('Convolution3D', param), [1, 16, 64, 64])
        self.assertAlmostEqual(conv.bias[1], -math.log(3), 5, 'focal filler set bias[index] = -log((1 - pi) / pi)')
        conv.bias[1] = 0
        self.assertTrue((conv.bias == 0).all(), 'and other elements to 0')

        param['bias_filler'] = dict(type='none')
        conv = cc.Convolution3D(bp.layer('Convolution3D', param), [1, 1, 64, 64])
        self.assertTrue(True, 'none filler leaves bias untouched')

        param['bias_filler'] = dict(type='unknown filler type should trigger a ValueError')
        layer_param = bp.layer('Convolution3D', param)
        self.assertRaises(ValueError, cc.Convolution3D, layer_param, [1, 1, 64, 64])

    def test_forward_shape_rf_3d(self):
        for param in bp.dropout(0.0001, bp.generate_param(*bp.CONVOLUTION_GENERATORS, ndim=3)):
            if 'stride_d' in param and random.random() > 0.5:
                param['temporal_stride'] = param['stride_d']
            layer = bp.layer('Convolution3D', bp.rename(param, dict(kernel_d='kernel_depth', pad_d='temporal_pad')))

            input_shape = [1, 1, 8, 8, 8]
            module = cc.Convolution3D(layer, input_shape)
            x = torch.zeros(*input_shape)
            forward_shape = list(module(x).shape)
            self.assertEqual(module.forward_shape(input_shape), forward_shape)
            self.assertEqual(module.forward_RF([1] * 6), list(module.kernel_size) + list(module.stride))


class TestDeconvolution(unittest.TestCase):
    def test_construction(self):
        for param in bp.dropout(0.01, bp.generate_param(*bp.CONVOLUTION_GENERATORS)):
            # TODO: adapt further work
            if param.get('kernel_w', None) != param.get('kernel_h', None):
                continue
            layer_param = bp.layer('Deconvolution', param, param_key='convolution_param')
            in_channels = rp.num_output(param)

            module = cc.Deconvolution(layer_param, [1, in_channels, 64, 64])
            self.assertEqual(module.in_channels, in_channels)
            self.assertEqual(module.out_channels, rp.num_output(param))
            self.assertEqual(module.kernel_size, rp.kernel_size(param))
            # TODO: adapt further work
            self.assertEqual(module.dilation, (1, 1), 'by now, Deconv does not support dilation')
            self.assertEqual(module.bias is not None, rp.bias(param))

    def test_weight_filler(self):
        param = dict(num_output='3', kernel_size='4', stride='2', pad='1', bias_term='false', group='1',
                     weight_filler=dict(type='bilinear'))
        original = cc.Deconvolution.get_upsampling_weight
        cc.Deconvolution.get_upsampling_weight = unittest.mock.MagicMock(return_value=original(None, 1, 3, 4))
        dec = cc.Deconvolution(bp.layer('Deconvolution', param, param_key='convolution_param'), [1, 3, 5, 5])
        self.assertIsNone(dec.bias)
        cc.Deconvolution.get_upsampling_weight.assert_called_once()
        cc.Deconvolution.get_upsampling_weight = original

    def test_forward_shape_rf(self):
        # TODO: Update this case when Deconvolution is fully implemented
        input_shape = [1, 2, 4, 4]
        param = dict(num_output=2, kernel_size=4, stride=2, pad=1)
        layer_param = bp.layer('Deconvolution', param, param_key='convolution_param')
        module = cc.Deconvolution(layer_param, input_shape)
        x = torch.zeros(*input_shape)
        forward_shape = list(module(x).size())
        self.assertEqual(module.forward_shape(input_shape), forward_shape)
        self.assertEqual(module.forward_RF([1, 1, 2, 2]), [3, 3, 1, 1])


class TestSparseConvolution(unittest.TestCase):
    def test_sparse_convolution(self):
        for param in bp.dropout(0.01, bp.generate_param(*bp.CONVOLUTION_GENERATORS)):
            sparsity = random.random()
            param['sparsity'] = str(sparsity)
            layer_param = bp.layer('SConvolution', param, param_key='convolution_param')
            layer_param['sparse_param'] = dict(sparsity=sparsity)
            in_channels = random.randint(1, 1024)

            module = cc.SConvolution(layer_param, [1, in_channels, 64, 64])
            self.assertEqual(module.in_channels, in_channels)
            self.assertEqual(module.out_channels, rp.num_output(param))
            self.assertEqual(module.kernel_size, rp.kernel_size(param))
            self.assertEqual(module.dilation[0], rp.dilation(param))
            self.assertEqual(module.bias is not None, rp.bias(param))
            self.assertEqual(module.sparsity, sparsity)
            self.module = module

    def test_set_sparsity(self):
        param = dict(num_output=1, kernel_size=5)
        layer = cc.SConvolution(bp.layer('SConvolution', param, param_key='convolution_param'), [1, 1, 5, 5])
        r = torch.arange(25.)
        for sparsity in [0.25, 0.5, 0.75]:
            layer.sparsity = sparsity
            with torch.no_grad():
                layer.weight.copy_(r.view(1, 1, 5, 5))
            layer.set_sparsity()
            threshold = math.ceil(25 * sparsity)
            pivot = int(threshold)
            kernel = layer.weight.view(-1)
            self.assertTrue((kernel[:pivot] == 0).all())
            self.assertTrue((kernel[pivot:] == r[pivot:]).all())

    def test_forward(self):
        param = dict(num_output=1, kernel_size=3, bias_term='false')
        layer = cc.SConvolution(bp.layer('SConvolution', param, param_key='convolution_param'), [1, 1, 3, 3])
        r = torch.arange(9.)
        ones = torch.ones(1, 1, 3, 3)
        for sparsity in [0.25, 0.5, 0.75]:
            layer.sparsity = sparsity
            layer.seen = 0
            with torch.no_grad():
                layer.weight.copy_(r.view(1, 1, 3, 3))
            for i in range(3):
                h = layer(ones)
                self.assertEqual(h.sum().item(), layer.weight.sum().item())
