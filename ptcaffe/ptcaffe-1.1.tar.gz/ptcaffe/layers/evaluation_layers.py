# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

from __future__ import division, print_function

import abc
import torch
import torch.nn as nn
import threading
from ptcaffe.utils.logger import logger
from collections import OrderedDict
from .evaluation_metrics import AccuracyMetric

__all__ = ['BaseEvaluator', 'AccuracyEvaluator', 'Accuracy']


class BaseEvaluator(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(BaseEvaluator, self).__init__()
        phase = layer['include']['phase']
        assert phase == 'TEST', "Evaluator should be in TEST phase"
        self.metric = self.create_metric(layer, *input_shapes)
        self.lock = threading.Lock()
        self.device = -1
        self.devices = [-1]
        assert('top' in layer)
        self.tops = layer['top'] if isinstance(layer['top'], list) else [layer['top']]

    def __repr__(self):
        return "BaseEvaluator()"

    @abc.abstractmethod
    def create_metric(self, layer, *input_shapes):
        pass

    def set_devices(self, devices):
        self.devices = devices

    def set_device(self, device):
        self.device = device

    def forward_shape(self, *input_shapes):
        if len(self.tops) == 1:
            return [1,]
        else:
            if len(self.tops) == 1: 
                return [1,]
            else:
                return tuple([1,] for i in range(len(self.tops)))

    def get_metric(self):
        result = self.metric.get()
        metric_dict = dict()
        if isinstance(result, float):
            assert(len(self.tops) == 1)
            metric_dict = {self.tops[0]: torch.Tensor([result]).cuda()}
        elif isinstance(result, (list, tuple)):
            assert(len(self.tops) == len(result))
            for i, val in enumerate(result):
                metric_dict[self.tops[i]] = torch.Tensor([val]).cuda()
        elif isinstance(result, (dict, OrderedDict)):
            assert(len(self.tops) == len(result.keys()))
            # if self.tops cannot match result keys, error!
            for key in result.keys():
                assert(key in self.tops)
            for key, val in result.items():
                metric_dict[key] = torch.Tensor([val]).cuda()
        return metric_dict

    def reset_metric(self):
        self.metric.reset()

    def forward(self, *inputs):
        self.lock.acquire()
        self.metric.update(*inputs)
        self.lock.release()
        if len(self.tops) == 1:
            return torch.zeros(1).cuda()
        else:
            if len(self.tops) == 1:
                return torch.zeros(1).cuda()
            else:
                return tuple(torch.zeros(1).cuda() for i in range(len(self.tops)))



class AccuracyEvaluator(BaseEvaluator):
    def __init__(self, layer, *input_shapes):
        super(AccuracyEvaluator, self).__init__(layer, *input_shapes)

    def create_metric(self, layer, *input_shapes):
        evaluator_param = layer.get('evaluator_param', OrderedDict())
        top_k = int(evaluator_param.get('top_k', 1))
        ignore_label = None
        if 'ignore_label' in evaluator_param:
            ignore_label = int(evaluator_param['ignore_label'])
        metric = AccuracyMetric(top_k, ignore_label)
        return metric

    def __repr__(self):
        return 'AccuracyEvaluator()'


class Accuracy(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(Accuracy, self).__init__()
        accuracy_param = layer.get('accuracy_param', OrderedDict())
        self.top_k = int(accuracy_param.get('top_k', 1))
        self.ignore_label = None
        if 'ignore_label' in accuracy_param:
            self.ignore_label = int(accuracy_param['ignore_label'])

    def __repr__(self):
        return 'Accuracy()'

    def forward_shape(self, input_shape1, input_shape2):
        return [1, ]

    def forward(self, output, label):
        if self.top_k == 1:
            if self.ignore_label is None:
                max_vals, max_ids = output.data.max(1)
                if label.dim() > 1 and label.numel() == output.size(0):
                    label = label.view(-1)
                n_correct = (max_ids.view(-1).long() == label.data.long()).sum()
                batchsize = output.data.size(0)
                accuracy = float(n_correct) / batchsize
                accuracy = output.data.new().resize_(1).fill_(accuracy)
                return accuracy
            else:
                max_vals, max_ids = output.data.max(1)
                non_ignore_mask = (label.data.long() != self.ignore_label)
                n_correct = ((max_ids.view(-1).long() == label.data.long()) & non_ignore_mask).sum()
                non_ignore_num = float(non_ignore_mask.sum())
                accuracy = float(n_correct) / (non_ignore_num + 1e-6)
                accuracy = output.data.new().resize_(1).fill_(accuracy)
                return accuracy
        else:
            assert self.top_k == 5
            max_vals, max_ids = output.data.topk(self.top_k, 1)
            label_size = label.numel()
            label_ext = label.data.long().view(label_size, 1).expand(label_size, self.top_k)
            compare = (max_ids.view(-1, self.top_k) == label_ext)
            n_correct = compare.sum()
            batchsize = output.data.size(0)
            accuracy = float(n_correct) / batchsize
            accuracy = output.data.new().resize_(1).fill_(accuracy)
            return accuracy
