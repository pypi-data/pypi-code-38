# encoding: UTF-8

from __future__ import division

import re
import unittest.mock
import ptcaffe.utils.filler
from ptcaffe.utils.config import cfg
import torch.nn.init
import torch.nn.functional as F
import torch.nn as nn

import random
import test.layers.boilerplate as bp
import test.layers.read_param as rp
#import boilerplate as bp
#import read_param as rp
import ptcaffe.layers.activation_layers as act
from collections import OrderedDict

class TestReLU(unittest.TestCase):
    def test_set_negative_slope(self):
        slope_param = [dict(), dict(negative_slope=random.random())]
        inputs = torch.randn(1,16,64,64)

        for param in slope_param:
            layer = act.ReLU(bp.layer('ReLU', param=param), [1,16,64,64])
            outputs = layer(inputs)
            if 'negative_slope' not in param:
                model = nn.ReLU()
                outputs_pt = model(inputs)
                self.assertEqual(outputs.tolist(), outputs_pt.tolist())
            else:
                outputs_pt = F.leaky_relu(inputs, negative_slope=param['negative_slope'])
                self.assertEqual(outputs.tolist(), outputs_pt.tolist())

    def test_set_inplace(self):
        layer_name = bp.random_name()
        layer_param = OrderedDict(name=layer_name,
                                  type='ReLU',
                                  top=layer_name,
                                  bottom=layer_name)
        inputs = torch.randn(1,16,64,64)
        layer = act.ReLU(layer_param, [1,6,64,64])
        outputs = layer(inputs)
        self.assertEqual(inputs.tolist(), outputs.tolist())

    def test_forward_shape(self):
        inputs = torch.randn(1,16,64,64)
        model = nn.ReLU()
        forward_shape_pt = model(inputs).numpy().shape
        layer = act.ReLU(bp.layer('ReLU', param=dict()), [1,16,64,64])
        self.assertEqual(layer.forward_shape((1,16,64,64)), forward_shape_pt)

class TestReLU6(unittest.TestCase):
    def test_set_inplace(self):
        layer_name = bp.random_name()
        layer_param = OrderedDict(name=layer_name,
                                  type='ReLU6',
                                  top=layer_name,
                                  bottom=layer_name)
        layer = act.ReLU6(layer_param, [1,16,64,64])

        inputs_leaf = torch.randn(1,16,64,64, requires_grad=True)
        inputs = inputs_leaf.add(0.0)

        outputs_leaf = layer(inputs_leaf)
        outputs_pytorch = F.relu6(inputs_leaf)
        self.assertEqual(outputs_pytorch.tolist(), outputs_leaf.tolist())
        outputs = layer(inputs)
        self.assertEqual(inputs.tolist(), outputs.tolist())

    def test_forward_shape(self):
        inputs = torch.randn(1,16,64,64)
        forward_shape_pt = F.relu6(inputs).numpy().shape
        layer = act.ReLU6(bp.layer('ReLU6', param=dict()), [1,16,64,64])
        self.assertEqual(layer.forward_shape((1,16,64,64)), forward_shape_pt)

class TestSigmoid(unittest.TestCase):
    def test_forward_shape(self):
        inputs = torch.randn(1,16,64,64)
        model = nn.Sigmoid()
        forward_shape_pt = model(inputs).numpy().shape
        layer = act.Sigmoid(bp.layer('Sigmoid', param=dict()), [1,16,64,64])
        self.assertEqual(layer.forward_shape((1,16,64,64)), forward_shape_pt)

class TestSoftmax(unittest.TestCase):
    def test_set_axis(self):
        inputs = torch.randn(1,16,64,64)

        for axis in [1,2,3]:
            layer = act.Softmax(bp.layer('Softmax', param=dict(axis=axis)), [1,16,64,64])
            outputs = layer(inputs)
            outputs_pytorch = F.softmax(inputs, dim=axis)
            self.assertEqual(outputs.tolist(), outputs_pytorch.tolist())

    def test_forward_shape(self):
        inputs = torch.randn(1,16,64,64)
        forward_shape_pt = F.softmax(inputs, dim=1).numpy().shape
        layer = act.Softmax(bp.layer('Softmax', param=dict(aixs=1)), [1,16,64,64])
        self.assertEqual(layer.forward_shape((1,16,64,64)), forward_shape_pt)

