from __future__ import division, print_function
import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.modules.batchnorm import _BatchNorm
from ptcaffe.nn.syncbn.batchnorm import _SynchronizedBatchNorm
from collections import OrderedDict

from ptcaffe.utils.config import cfg

__all__ = ['BatchNorm', 'SwitchNorm', 'Normalize', 'LRN', 'SyncBatchNorm']


class BatchNorm(_BatchNorm):
    def __init__(self, layer, input_shape):
        batch_norm_param = layer.get('batch_norm_param', OrderedDict())
        momentum = float(batch_norm_param.get('moving_average_fraction', 0.999))
        self.affine = cfg.DEFAULT_BATCHNORM_AFFINE
        if 'affine' in batch_norm_param:
            self.affine = (batch_norm_param['affine'] == 'true')
            self.affine_size = [1 for i in range(len(input_shape))]
            self.affine_size[1] = -1
        eps = float(batch_norm_param.get('eps', 1e-5))
        self.use_global_stats = (batch_norm_param.get('use_global_stats', 'false') == 'true')
        channels = input_shape[1]
        super(BatchNorm, self).__init__(channels, momentum=1.0 - momentum, affine=self.affine, eps=eps)
        if self.affine:
            weight_filler = OrderedDict()
            if 'filler' in batch_norm_param:
                weight_filler = batch_norm_param['filler']
            elif 'weight_filler' in batch_norm_param:
                weight_filler = batch_norm_param['weight_filler']

            weight_filler_type = weight_filler.get('type', 'gaussian')
            if weight_filler_type == 'gaussian':
                mean_val = float(weight_filler.get('mean', 1.0))
                std_val = float(weight_filler.get('std', 0.02))
                torch.nn.init.normal_(self.weight.data, mean_val, std_val)
            elif weight_filler_type == 'constant':
                value = float(weight_filler.get('value', 1.0))
                self.weight.data.fill_(value)
            else:
                mean_val = 1.0
                std_val = 0.02
                torch.nn.init.normal(self.weight.data, mean_val, std_val)

            bias_filler = batch_norm_param.get('bias_filler', OrderedDict())
            bias_filler_type = bias_filler.get('type', 'constant')
            if bias_filler_type == 'constant':
                value = float(bias_filler.get('value', 0.0))
                self.bias.data.fill_(value)
            else:
                self.bias.data.fill_(0.0)

        # distributed params
        distributed_param = layer.get('distributed_param', OrderedDict())
        self.sync_params = (distributed_param.get('sync_params', 'true') == 'true')

    def forward(self, x):
        training = False if self.use_global_stats else self.training
        return F.batch_norm(x, self.running_mean, self.running_var, self.weight, self.bias, training=training, momentum=self.momentum, eps=self.eps)

    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        return output_shape


class SwitchNorm(nn.Module):
    def __init__(self, layer, input_shape):
        super(SwitchNorm, self).__init__()
        assert False, "This layer is not tested"
        switch_norm_param = layer.get('switch_norm_param', OrderedDict())
        num_features = input_shape[1]
        eps = float(switch_norm_param.get('eps', 1e-5))
        momentum = float(switch_norm_param.get('momentum', 0.997))
        using_moving_average = (switch_norm_param.get('using_moving_average', 'true') == 'true')
        last_gamma = (switch_norm_param.get('last_gamma', 'true') == 'true')
        self.create(num_features, eps, momentum, using_moving_average, last_gamma)

    def create(self, num_features, eps, momentum, using_moving_average, last_gamma):
        self.weight = nn.Parameter(torch.ones(1, num_features, 1, 1))
        self.bias = nn.Parameter(torch.zeros(1, num_features, 1, 1))
        self.mean_weight = nn.Parameter(torch.ones(3))
        self.var_weight = nn.Parameter(torch.ones(3))
        self.eps = eps
        self.momentum = momentum
        self.using_moving_average = using_moving_average
        self.last_gamma = last_gamma
        self.register_buffer('running_mean', torch.zeros(1, num_features, 1))
        self.register_buffer('running_var', torch.zeros(1, num_features, 1))
        self.reset_parameters()

    def reset_parameters(self):
        self.running_mean.zero_()
        self.running_var.zero_()
        if self.last_gamma:
            self.weight.data.fill_(0)
        else:
            self.weight.data.fill_(1)
        self.bias.data.zero_()

    def forward(self, x):
        N, C, H, W = x.size()
        x = x.view(N, C, -1)
        mean_in = x.mean(-1, keepdim=True)
        var_in = x.var(-1, keepdim=True)

        mean_ln = mean_in.mean(1, keepdim=True)
        temp = var_in + mean_in ** 2
        var_ln = temp.mean(1, keepdim=True) - mean_ln ** 2

        if self.training:
            mean_bn = mean_in.mean(0, keepdim=True)
            var_bn = temp.mean(0, keepdim=True) - mean_bn ** 2
            if self.using_moving_average:
                self.running_mean.mul_(self.momentum)
                self.running_mean.add_((1 - self.momentum) * mean_bn.data)
                self.running_var.mul_(self.momentum)
                self.running_var.add_((1 - self.momentum) * var_bn.data)
            else:
                self.running_mean.add_(mean_bn.data)
                self.running_var.add_(mean_bn.data ** 2 + var_bn.data)
        else:
            mean_bn = self.running_mean
            var_bn = self.running_var

        softmax = nn.Softmax(0)
        mean_weight = softmax(self.mean_weight)
        var_weight = softmax(self.var_weight)

        mean = mean_weight[0] * mean_in + mean_weight[1] * mean_ln + mean_weight[2] * mean_bn
        var = var_weight[0] * var_in + var_weight[1] * var_ln + var_weight[2] * var_bn

        x = (x - mean) / (var + self.eps).sqrt()
        x = x.view(N, C, H, W)
        return x * self.weight + self.bias

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)


class Normalize(nn.Module):
    def __init__(self, layer, input_shape):
        super(Normalize, self).__init__()
        channels = input_shape[1]
        scale = float(layer['norm_param']['scale_filler']['value'])
        self.channels = channels
        self.scale = scale
        self.eps = 1e-10
        self.weight = nn.Parameter(torch.Tensor(self.channels))
        # self.weight.data.fill_(self.scale)
        torch.nn.init.constant_(self.weight.data, self.scale)
        self.register_parameter('bias', None)

        # distributed params
        distributed_param = layer.get('distributed_param', OrderedDict())
        self.sync_params = (distributed_param.get('sync_params', 'true') == 'true')

    def __repr__(self):
        return 'Normalize(channels=%d, scale=%f)' % (self.channels, self.scale)

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        norm = x.pow(2).sum(dim=1, keepdim=True).sqrt() + self.eps
        #print('norm_sum = %f' % norm.data.sum())
        #print('self.weight = ', list(self.weight.data))
        x = x / norm * self.weight.view(1, -1, 1, 1)
        #x = x / norm * self.scale
        return x


# use this one instead
class LRN(nn.LocalResponseNorm):
    def __init__(self, layer, input_shape):
        size = int(layer['lrn_param']['local_size'])
        alpha = float(layer['lrn_param']['alpha'])
        beta = float(layer['lrn_param']['beta'])
        super(LRN, self).__init__(size, alpha, beta)

    def __repr__(self):
        return 'LRN(size=%d, alpha=%f, beta=%f, k=%d)' % (self.size, self.alpha, self.beta, self.k)

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)


class SyncBatchNorm(_SynchronizedBatchNorm):
    def __init__(self, layer, input_shape):
        batch_norm_param = layer.get('batch_norm_param', OrderedDict())
        momentum = float(batch_norm_param.get('moving_average_fraction', 0.999))
        self.affine = cfg.DEFAULT_BATCHNORM_AFFINE
        if 'affine' in batch_norm_param:
            self.affine = (batch_norm_param['affine'] == 'true')
            self.affine_size = [1] * len(input_shape)
            self.affine_size[1] = -1
        eps = float(batch_norm_param.get('eps', 1e-5))
        self.use_global_stats = (batch_norm_param.get('use_global_stats', 'false') == 'true')
        channels = input_shape[1]
        super(SyncBatchNorm, self).__init__(channels, momentum=1.0 - momentum, affine=self.affine, eps=eps)

        if self.affine:
            weight_filler = batch_norm_param.get('weight_filler', OrderedDict())
            weight_filler_type = weight_filler.get('type', 'gaussian')
            if weight_filler_type == 'gaussian':
                mean_val = float(weight_filler.get('mean', 1.0))
                std_val = float(weight_filler.get('std', 0.02))
                torch.nn.init.normal(self.weight.data, mean_val, std_val)
            else:
                mean_val = 1.0
                std_val = 0.02
                torch.nn.init.normal(self.weight.data, mean_val, std_val)

            bias_filler = batch_norm_param.get('bias_filler', OrderedDict())
            bias_filler_type = bias_filler.get('type', 'constant')
            if bias_filler_type == 'constant':
                value = float(bias_filler.get('value', 0.0))
                self.bias.data.fill_(value)
            else:
                self.bias.data.fill_(0.0)

    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        return output_shape
