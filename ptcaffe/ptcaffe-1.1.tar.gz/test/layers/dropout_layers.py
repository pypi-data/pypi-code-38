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
import ptcaffe.layers.dropout_layers as dp
from collections import OrderedDict

class TestDropout(unittest.TestCase):
    def test_forward(self):
        inputs = torch.randn(1,16,64,64)
        layer = dp.Dropout(bp.layer('Dropout', param=dict()), [1,16,64,64])
        layer.eval()
        model = nn.Dropout(0.5)
        model.eval()
        self.assertEqual(model(inputs).tolist(), layer(inputs).tolist())

    def test_forward_shape(self):
        inputs = torch.randn(1,16,64,64)
        model = nn.Dropout(0.5)
        forward_shape_pt = model(inputs).numpy().shape
        layer = dp.Dropout(bp.layer('Dropout', param=dict()), [1,16,64,64])
        self.assertEqual(layer.forward_shape((1,16,64,64)), forward_shape_pt)

class TestDropout3D(unittest.TestCase):
    def test_forward(self):
        inputs = torch.randn(1,16,64,64)
        layer = dp.Dropout3D(bp.layer('Dropout3D', param=dict()), [1,16,64,64])
        layer.eval()
        model = nn.Dropout3d(0.5)
        model.eval()
        self.assertEqual(model(inputs).tolist(), layer(inputs).tolist())

    def test_forward_shape(self):
        inputs = torch.randn(1,16,64,64)
        model = nn.Dropout3d(0.5)
        forward_shape_pt = model(inputs).numpy().shape
        layer = dp.Dropout3D(bp.layer('Dropout3D', param=dict()), [1,16,64,64])
        self.assertEqual(layer.forward_shape((1,16,64,64)), forward_shape_pt)

# TODO: DropBlock2d

