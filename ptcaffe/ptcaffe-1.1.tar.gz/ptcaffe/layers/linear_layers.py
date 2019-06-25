from __future__ import division, print_function
import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict

from ptcaffe.utils.config import cfg
from ptcaffe.utils.filler import xavier_init, msra_init

__all__ = ['InnerProduct', 'SInnerProduct']


class InnerProduct(nn.Linear):
    def __init__(self, layer, input_shape):
        inner_product_param = layer.get('inner_product_param', OrderedDict())
        bias = True
        if 'bias_term' in inner_product_param and inner_product_param['bias_term'] == 'false':
            bias = False
        self.out_channels = int(inner_product_param.get('num_output', 0))
        if len(input_shape) == 5:
            channels = input_shape[1]
            length = input_shape[2]
            input_height = input_shape[3]
            input_width = input_shape[4]
            self.in_channels = channels * length * input_height * input_width
        elif len(input_shape) == 4:
            channels = input_shape[1]
            input_height = input_shape[2]
            input_width = input_shape[3]
            self.in_channels = channels * input_height * input_width
        elif len(input_shape) == 3:
            self.in_channels = input_shape[2]
        else:
            self.in_channels = input_shape[1]
        super(InnerProduct, self).__init__(self.in_channels, self.out_channels, bias)
        self.input_shape = copy.copy(input_shape)  # used in forward_RF
        weight_filler = inner_product_param.get('weight_filler', OrderedDict())
        weight_filler_type = weight_filler.get('type', cfg.DEFAULT_WEIGHT_FILLER_TYPE)
        variance_norm = weight_filler.get('variance_norm', cfg.DEFAULT_VARIANCE_NORM)
        nonlinearity = weight_filler.get('nonlinearity', cfg.DEFAULT_NONLINEARITY)
        if weight_filler_type == 'xavier':
            xavier_init(self.weight, variance_norm, nonlinearity)
        elif weight_filler_type == 'msra':
            msra_init(self.weight, variance_norm, nonlinearity)
        else:
            torch.nn.init.xavier_uniform_(self.weight)
        if bias:
            bias_filler = inner_product_param.get('bias_filler', OrderedDict())
            bias_filler_type = bias_filler.get('type', cfg.DEFAULT_BIAS_FILLER_TYPE)
            if bias_filler_type == 'constant':
                value = float(bias_filler.get('value', 0.0))
                self.bias.data.fill_(value)
            else:
                assert(False)

        # distributed params
        distributed_param = layer.get('distributed_param', OrderedDict())
        self.sync_params = (distributed_param.get('sync_params', 'true') == 'true')

    def __repr__(self):
        return 'InnerProduct(%d, %d)' % (self.in_channels, self.out_channels)

    def forward_shape(self, input_shape):
        if len(input_shape) == 2 or len(input_shape) == 4 or len(input_shape) == 5:
            output_shape = [input_shape[0], self.out_features]
        elif len(input_shape) == 3:
            output_shape = list(input_shape)
            output_shape[2] = self.out_channels
        return output_shape

    def forward(self, x):
        if x.dim() == 2:
            x = F.linear(x, self.weight, self.bias)
        elif x.dim() == 3:
            nT = x.size(0)
            nB = x.size(1)
            x = x.view(nT * nB, -1)
            x = F.linear(x, self.weight, self.bias)
            x = x.view(nT, nB, -1)
        elif x.dim() >= 4:
            nB = x.data.size(0)
            x = x.view(nB, -1)
            x = F.linear(x, self.weight, self.bias)
        return x

    def forward_RF(self, input_RF):
        if len(self.input_shape) == 5:
            length = self.input_shape[2]
            width = self.input_shape[4]
            height = self.input_shape[3]
            in_rf_size_d = input_RF[0]
            in_rf_size_h = input_RF[1]
            in_rf_size_w = input_RF[2]
            in_rf_step_d = input_RF[3]
            in_rf_step_h = input_RF[4]
            in_rf_step_w = input_RF[5]
            out_rf_step_d = in_rf_step_d * length
            out_rf_step_h = in_rf_step_h * height
            out_rf_step_w = in_rf_step_w * width
            out_rf_size_d = in_rf_size_d + (length - 1) * in_rf_step_d
            out_rf_size_h = in_rf_size_h + (height - 1) * in_rf_step_h
            out_rf_size_w = in_rf_size_w + (width - 1) * in_rf_step_w
            return [out_rf_size_d, out_rf_size_h, out_rf_size_w, out_rf_step_d, out_rf_step_h, out_rf_step_w]
        elif len(self.input_shape) == 4:
            width = self.input_shape[3]
            height = self.input_shape[2]
            in_rf_size_h = input_RF[0]
            in_rf_size_w = input_RF[1]
            in_rf_step_h = input_RF[2]
            in_rf_step_w = input_RF[3]
            out_rf_step_h = in_rf_step_h * height
            out_rf_step_w = in_rf_step_w * width
            out_rf_size_h = in_rf_size_h + (height - 1) * in_rf_step_h
            out_rf_size_w = in_rf_size_w + (width - 1) * in_rf_step_w
            return [out_rf_size_h, out_rf_size_w, out_rf_step_h, out_rf_step_w]
        elif len(self.input_shape) == 3:
            return copy.copy(input_RF)
        elif len(self.input_shape) == 2:
            return copy.copy(input_RF)


class SInnerProduct(InnerProduct):
    def __init__(self, layer, input_shape):
        super(SInnerProduct, self).__init__(layer, input_shape)
        sparse_param = layer.get('sparse_param', OrderedDict())
        self.sparsity = 0.0
        if 'sparsity' in sparse_param:
            self.sparsity = float(sparse_param['sparsity'])
            assert(self.sparsity < 1.0 and self.sparsity >= 0)
        self.register_buffer('mask', torch.ones(self.weight.shape))
        self.RECOVER = False
        self.seen = 0

    def __repr__(self):
        return 'SInnerProduct(in_channel=%d, out_channels%d, sparsity=%f)' % (self.in_channels, self.out_channels, self.sparsity)

    def set_sparsity(self):
        if self.sparsity > 0.0:
            num = self.weight.data.numel()
            k = max(int(num * (1 - self.sparsity)), 1)
            thresh = self.weight.data.abs().view(-1).topk(k)[0][-1]
            self.mask = (self.weight.data.abs() >= thresh).float()
            if not self.RECOVER:
                self.weight.data = self.weight.data * self.mask

    def forward(self, x):
        if self.seen == 0:
            self.set_sparsity()
        self.seen += 1
        weight = self.weight * self.mask
        if x.dim() == 2:
            x = F.linear(x, weight, self.bias)
        elif x.dim() == 3:
            nT = x.size(0)
            nB = x.size(1)
            x = x.view(nT * nB, -1)
            x = F.linear(x, weight, self.bias)
            x = x.view(nT, nB, -1)
        elif x.dim() >= 4:
            nB = x.data.size(0)
            x = x.view(nB, -1)
            x = F.linear(x, weight, self.bias)
        return x
