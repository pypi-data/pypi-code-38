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
import ptcaffe.layers.normalization_layers as norm
from collections import OrderedDict

class TestBatchNorm(unittest.TestCase):
    def test_construction(self):
        for param in bp.generate_param(*bp.BATCHNORM_GENERATORS):
            layer_param = bp.layer('BatchNorm', param, param_key='batch_norm_param')
            modules = norm.BatchNorm(layer_param, [1,16,64,64])

            self.assertEqual(modules.momentum, 1.0 - param['moving_average_fraction'])
            self.assertEqual(modules.eps, param['eps'])
            if param['affine'] == 'true':
                if param['weight_filler']['type'] == 'constant':
                    self.assertTrue(modules.weight.mean() - param['weight_filler']['value'] < 1e-5)
                self.assertTrue(modules.bias.mean() - param['bias_filler']['value'] < 1e-5)
            else:
                self.assertTrue(modules.weight is None)
                self.assertTrue(modules.bias is None)

    def test_forward(self):
        num_features = random.randint(1,1024)
        input = torch.randn(1,num_features,64,64)

        param = dict(affine='true', weight_filler={'type':'constant', 'value':1.0},
                    use_global_stats='true', eps=1e-5, moving_average_fraction=0.99,
                    bias_filler={'type':'constant','value':1.0})
        layer_param = bp.layer('BatchNorm', param, param_key='batch_norm_param')
        modules = norm.BatchNorm(layer_param, [1,num_features,64,64])
        output = modules(input)

        input_mean = input.mean()
        input_var = input.var()
        input_norm = (input - input_mean)/torch.sqrt(input_var + 1e-5)
        output_pt = torch.ones(1,num_features,1,1) * input_norm + torch.ones(1,num_features,1,1)
        self.assertTrue((output.data.mean() - output_pt.mean()).abs() < 1e-2)

# Switch Norm : the layer is not tested
#class TestSwitchNorm(unittest.TestCase):
#    def test_construction(self):
#        switch_norm_generators = [bp.generate_batchnorm_eps, bp.generate_batchnorm_last_gamma,
#                                  bp.generate_batchnorm_using_moving_average]
#        for param in bp.generate_param(*switch_norm_generators):
#            param['momentum'] = random.random()
#            layer_param = bp.layer('SwitchNorm', param, param_key='switch_norm_param')
#            modules = norm.SwitchNorm(layer_param, [1,16,64,64])
#            
#            self.assertEqual(modules.eps, param['eps'])
#            self.assertEqual(modules.momentum, param['momentum'])
#            self.assertEqual(modules.using_moving_average, param['using_moving_average'])
#            self.assertEqual(modules.last_gamma, param['last_gamma'])

class TestNormalize(unittest.TestCase):
    def test_construction(self):
        num_features = random.randint(1,1024)
        scale_filler = bp.generate_batchnorm_filler_type('scale')

        layer_param = bp.layer('Normalize',dict(scale_filler=scale_filler), param_key='norm_param')
        modules = norm.Normalize(layer_param, [1,num_features,64,64])

        self.assertEqual(modules.channels, num_features)
        self.assertEqual(modules.scale, scale_filler['value'])
        self.assertTrue((modules.weight.data.mean() - scale_filler['value']).abs() < 1e-5)
    
    def test_forward(self):
        num_features = random.randint(1,1024)
        input = torch.randn(1,num_features,64,64)
        
        layer_param = bp.layer('Normalize',dict(scale_filler={'value':1}), param_key='norm_param')
        modules = norm.Normalize(layer_param, [1,num_features,64,64])

        output = modules(input)
        input_var = input.var()
        input_norm = (input)/torch.sqrt(input_var + 1e-10)
        output_pt = torch.ones(1,num_features,1,1) * input_norm
        self.assertTrue((output.data.mean() - output_pt.mean()).abs() < 1e-2)

# TODO: LRN, SyncBatchNorm

