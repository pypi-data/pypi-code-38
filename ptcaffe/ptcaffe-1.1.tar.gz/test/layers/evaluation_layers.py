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
import ptcaffe.layers.evaluation_layers as eval
from collections import OrderedDict

class TestAccuracy(unittest.TestCase):
    def test_contruction(self):
        top_k = random.choice([1,5])
        ignore_label = random.randint(0,5)
        layer = eval.Accuracy(bp.layer('Accuracy',param=dict(top_k=top_k,ignore_label=ignore_label),param_key='accuracy_param',
                                        include=dict(phase='TEST')),[16,2])
        self.assertEqual(layer.top_k, top_k)
        self.assertEqual(layer.ignore_label, ignore_label)

    def test_set_topk(self):
        input = torch.randn(16,100)
        target = torch.empty(16, dtype=torch.long).random_(100)
        for top_k in [1,5]:
            layer = eval.Accuracy(bp.layer('Accuracy',param=dict(top_k=top_k),param_key='accuracy_param',
                                        include=dict(phase='TEST')),[16,2])
            output = layer(input, target)
            
            _, pred = input.topk(top_k, 1, True, True)
            pred = pred.t()
            correct = pred.eq(target.view(1, -1).expand_as(pred)) 
            output_pt = correct[:top_k].view(-1).float().sum(0, keepdim=True)/16

            self.assertEqual(output, output_pt)

    def test_set_ignore_label(self):
        input = torch.randn(16,2)
        target = torch.zeros(16)
        layer = eval.Accuracy(bp.layer('Accuracy',param=dict(ignore_label=0),param_key='accuracy_param',
                                        include=dict(phase='TEST')),[[16,2], [16]])
        output = layer(input, target)
        self.assertEqual(output, torch.zeros(1))

class TestAccuracyEvaluator(unittest.TestCase):
    def test_construction(self):
        top_k = random.choice([1,5])
        ignore_label = random.randint(0,5)
        layer = eval.AccuracyEvaluator(bp.layer('AccuracyEvaluator',param=dict(top_k=top_k,ignore_label=ignore_label),param_key='evaluator_param',
                                        include=dict(phase='TEST')),[16,2])
        self.assertEqual(layer.metric.top_k, top_k)
        self.assertEqual(layer.metric.ignore_label, ignore_label)

    def test_set_topk(self):
        input = torch.randn(16,100)
        target = torch.empty(16, dtype=torch.long).random_(100)
        for top_k in [1,5]:
            layer = eval.AccuracyEvaluator(bp.layer('AccuracyEvaluator',param=dict(top_k=top_k),param_key='evaluator_param',
                                        include=dict(phase='TEST')),[16,100])
            layer(input, target)
            output = layer.metric.get()

            _, pred = input.topk(top_k, 1, True, True)
            pred = pred.t()
            correct = pred.eq(target.view(1, -1).expand_as(pred)) 
            output_pt = correct[:top_k].view(-1).float().sum(0, keepdim=True)/16
            self.assertEqual(output, output_pt)

    def test_set_ignore_label(self):
        input = torch.randn(16,2)
        target = torch.zeros(16, dtype=torch.long)
        layer = eval.AccuracyEvaluator(bp.layer('AccuracyEvaluator',param=dict(ignore_label=0),param_key='evaluator_param',
                                        include=dict(phase='TEST')),[16,2])
        layer(input, target)
        output = layer.metric.get()
        self.assertEqual(output, torch.zeros(1))

