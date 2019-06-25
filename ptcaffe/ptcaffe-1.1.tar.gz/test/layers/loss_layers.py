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
import ptcaffe.layers.loss_layers as loss
from collections import OrderedDict

class TestSoftmaxWithLoss(unittest.TestCase):
    def test_contruction(self):
        softmax_param = dict(axis=random.randint(1,3))
        for normalize in ['true', 'false']:
            ignore_label = random.randint(0,64)
            loss_param = dict(ignore_label=ignore_label, normalize=normalize)
            layer = loss.SoftmaxWithLoss(bp.layer('SoftmaxWithLoss',param=softmax_param,loss_param=loss_param,param_key='softmax_param'),[1,16,64,64])

            self.assertEqual(layer.ignore_label, ignore_label)
            self.assertEqual(layer.normalize, normalize=='true')
            self.assertEqual(layer.axis, softmax_param['axis'])

    def test_set_normalize(self):
        for normalize in ['true', 'false']:
            input = torch.randn(16,2)
            target = torch.LongTensor(16).random_(2)

            layer = loss.SoftmaxWithLoss(bp.layer('SoftmaxWithLoss',param=dict(normalize=normalize),param_key='loss_param'),[16,2])
            model = torch.nn.LogSoftmax(dim=-1)
            output = layer(input, target)
            output_pt = model(input).gather(1,target.view(-1,1)).sum().abs()
            if normalize == 'true':
                self.assertEqual(output, output_pt/input.size(0))
            else:
                self.assertEqual(output, output_pt)

    def test_set_ignore_label(self):
        ignore_label = 0
        input = torch.randn(16, 2)
        target = torch.zeros(16)

        layer = loss.SoftmaxWithLoss(bp.layer('SoftmaxWithLoss',param=dict(ignore_label=ignore_label),param_key='loss_param'),[16,2])
        output = layer(input, target)

class TestMimicLoss(unittest.TestCase):
    def test_construction(self):
        temperature = random.uniform(0, 1)
        axis = random.randint(1,3)

        layer = loss.MimicLoss(bp.layer('MimicLoss',param=dict(temperature=temperature,axis=axis),param_key='mimic_param'),[16,2])
        self.assertEqual(layer.T, temperature)
        self.assertEqual(layer.axis, axis)

    def test_set_axis(self):
        input = torch.randn(16,4)
        target = torch.randn(16,4)

        for axis in range(-2,2):
            layer = loss.MimicLoss(bp.layer('MimicLoss',param=dict(axis=axis),param_key='mimic_param'),[16,2])
            output = layer(input, target)
            output_pt = nn.KLDivLoss()(F.log_softmax(input, dim=axis), F.softmax(target,dim=axis)).view(1)
            self.assertEqual(output, output_pt)

class TestEuclideanLoss(unittest.TestCase):
    def test_construction(self):
        for normalization in ['NONE', 'FULL', 'BATCH_SIZE']:
            layer = loss.EuclideanLoss(bp.layer('EuclideanLoss',param=dict(normalization=normalization),param_key='loss_param'), [16,2])
            self.assertEqual(layer.normalization, normalization)

    def test_set_normalization(self):
        input = torch.randn(16,4)
        target = torch.randn(16,4)

        for normalization in ['NONE', 'FULL', 'BATCH_SIZE']:
            layer = loss.EuclideanLoss(bp.layer('EuclideanLoss',param=dict(normalization=normalization),param_key='loss_param'), [16,2])
            output = layer(input, target)
            if normalization == 'NONE':
                self.assertTrue((output[0] - torch.sum((input-target)**2)*0.5).abs() <= 1e-5)
            elif normalization == 'FULL':
                self.assertTrue((output[0] - torch.mean((input-target)**2)*0.5).abs() <= 1e-5)
            else:
                self.assertTrue((output[0] - torch.sum((input-target)**2)*0.5/16).abs() <= 1e-5)

