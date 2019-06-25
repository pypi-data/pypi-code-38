from __future__ import division, print_function
import math
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict

__all__ = ['Pooling', 'Pooling3D']


class Pooling(nn.Module):
    def __init__(self, layer, input_shape):
        nn.Module.__init__(self)

        kernel_h = input_shape[2]
        kernel_w = input_shape[3]
        pooling_param = layer.get('pooling_param', OrderedDict())
        if 'kernel_size' in pooling_param:
            kernel_size = int(pooling_param['kernel_size'])
            kernel_h = kernel_size
            kernel_w = kernel_size
        elif 'kernel_h' in pooling_param and 'kernel_w' in pooling_param:
            kernel_h = int(pooling_param['kernel_h'])
            kernel_w = int(pooling_param['kernel_w'])
        else:  # global pooling
            pass
            #assert(input_shape[2] == input_shape[3])
        stride_h = input_shape[2]
        stride_w = input_shape[3]
        if 'stride' in pooling_param:
            stride = int(pooling_param['stride'])
            stride_h = stride
            stride_w = stride
        elif 'stride_h' in pooling_param and 'stride_w' in pooling_param:
            stride_h = int(pooling_param['stride_h'])
            stride_w = int(pooling_param['stride_w'])
        else:
            pass
            #assert(input_shape[2] == input_shape[3])
        pad_h = 0
        pad_w = 0
        if 'pad' in pooling_param:
            pad = int(pooling_param['pad'])
            pad_h = pad
            pad_w = pad
        elif 'pad_h' in pooling_param and 'pad_w' in pooling_param:
            pad_h = int(pooling_param['pad_h'])
            pad_w = int(pooling_param['pad_w'])
        pool_type = pooling_param['pool']
        global_pooling = (pooling_param.get('global_pooling', 'false') == 'true')

        ceil_mode = (pooling_param.get('ceil_mode', 'true') == 'true')
        if pool_type == 'MAX':
            self.pooling = nn.MaxPool2d((kernel_h, kernel_w), (stride_h, stride_w), padding=(pad_h, pad_w), ceil_mode=ceil_mode)
        elif pool_type == 'AVE':
            self.pooling = nn.AvgPool2d((kernel_h, kernel_w), (stride_h, stride_w), padding=(pad_h, pad_w), ceil_mode=ceil_mode)
        self.padding = (pad_h, pad_w)
        self.kernel_size = (kernel_h, kernel_w)
        self.stride = (stride_h, stride_w)
        self.pool_type = pool_type
        self.global_pooling = global_pooling
        self.ceil_mode = ceil_mode

    def __repr__(self):
        if self.pool_type == 'MAX':
            return 'MaxPool2d (kernel_size=%s, stride=%s, padding=%s, ceil_mode=%s)' % (self.kernel_size, self.stride, self.padding, self.ceil_mode)
        else:
            return 'AvgPool2d (kernel_size=%s, stride=%s, padding=%s)' % (self.kernel_size, self.stride, self.padding)

    def forward_shape(self, input_shape):
        input_height = input_shape[2]
        input_width = input_shape[3]
        if self.global_pooling:
            output_height = 1
            output_width = 1
        elif self.ceil_mode:
            output_height = int(math.ceil((input_height + 2 * self.padding[0] - self.kernel_size[0]) / float(self.stride[0]))) + 1
            output_width = int(math.ceil((input_width + 2 * self.padding[1] - self.kernel_size[1]) / float(self.stride[1]))) + 1
        else:
            output_height = int(math.floor((input_height + 2 * self.padding[0] - self.kernel_size[0]) / float(self.stride[0]))) + 1
            output_width = int(math.floor((input_width + 2 * self.padding[1] - self.kernel_size[1]) / float(self.stride[1]))) + 1
        output_shape = [input_shape[0], input_shape[1], output_height, output_width]
        return output_shape

    def forward(self, x):
        if self.global_pooling:
            width = x.size(3)
            height = x.size(2)
            if self.pool_type == 'MAX':
                return F.max_pool2d(x, (height, width), stride=None, padding=0, ceil_mode=self.ceil_mode)
            elif self.pool_type == 'AVE':
                return F.avg_pool2d(x, (height, width), stride=None, padding=0, ceil_mode=self.ceil_mode)
        else:
            return self.pooling(x)

    def forward_RF(self, input_RF):
        in_rf_size_h = input_RF[0]
        in_rf_size_w = input_RF[1]
        in_rf_step_h = input_RF[2]
        in_rf_step_w = input_RF[3]
        kernel_h = self.kernel_size[0]
        kernel_w = self.kernel_size[1]
        stride_h = self.stride[0]
        stride_w = self.stride[1]
        out_rf_size_h = in_rf_size_h + (kernel_h - 1) * in_rf_step_h
        out_rf_size_w = in_rf_size_w + (kernel_w - 1) * in_rf_step_w
        out_rf_step_h = in_rf_step_h * stride_h
        out_rf_step_w = in_rf_step_w * stride_w
        return [out_rf_size_h, out_rf_size_w, out_rf_step_h, out_rf_step_w]


class Pooling3D(nn.Module):
    def __init__(self, layer, input_shape):
        nn.Module.__init__(self)

        kernel_d = 1
        kernel_h = input_shape[3]
        kernel_w = input_shape[4]
        pooling_param = layer.get('pooling3d_param', OrderedDict())
        if 'kernel_size' in pooling_param:
            kernel_size = int(pooling_param['kernel_size'])
            kernel_d = kernel_size
            kernel_h = kernel_size
            kernel_w = kernel_size
        elif 'kernel_h' in pooling_param and 'kernel_w' in pooling_param:
            kernel_h = int(pooling_param['kernel_h'])
            kernel_w = int(pooling_param['kernel_w'])

        if 'kernel_depth' in pooling_param:
            kernel_d = int(pooling_param['kernel_depth'])

        stride_d = 1
        stride_h = 1
        stride_w = 1
        if 'stride' in pooling_param:
            stride = int(pooling_param['stride'])
            stride_d = stride
            stride_h = stride
            stride_w = stride
        if 'stride_h' in pooling_param and 'stride_w' in pooling_param:
            stride_h = int(pooling_param['stride_h'])
            stride_w = int(pooling_param['stride_w'])
        if 'temporal_stride' in pooling_param:
            stride_d = int(pooling_param['temporal_stride'])
        if 'stride_d' in pooling_param:
            stride_d = int(pooling_param['stride_d'])

        pad_d = 0
        pad_h = 0
        pad_w = 0
        if 'pad' in pooling_param:
            pad = int(pooling_param['pad'])
            pad_h = pad
            pad_w = pad
        elif 'pad_h' in pooling_param and 'pad_w' in pooling_param:
            pad_h = int(pooling_param['pad_h'])
            pad_w = int(pooling_param['pad_w'])
        if 'temporal_pad' in pooling_param:
            pad_d = int(pooling_param['temporal_pad'])

        pool_type = pooling_param['pool']
        global_pooling = (pooling_param.get('global_pooling', 'false') == 'true')

        ceil_mode = (pooling_param.get('ceil_mode', 'true') == 'true')

        self.padding = (pad_d, pad_h, pad_w)
        self.kernel_size = (kernel_d, kernel_h, kernel_w)
        self.stride = (stride_d, stride_h, stride_w)
        self.pool_type = pool_type
        self.global_pooling = global_pooling
        self.ceil_mode = ceil_mode
        if pool_type == 'MAX':
            self.pooling = nn.MaxPool3d(self.kernel_size, self.stride, padding=self.padding, ceil_mode=ceil_mode)
        elif pool_type == 'AVE':
            self.pooling = nn.AvgPool3d(self.kernel_size, self.stride, padding=self.padding, ceil_mode=ceil_mode)

    def __repr__(self):
        if self.pool_type == 'MAX':
            return 'MaxPool3d (kernel_size=%s, stride=%s, padding=%s, ceil_mode=%s)' % (self.kernel_size, self.stride, self.padding, self.ceil_mode)
        else:
            return 'AvgPool3d (kernel_size=%s, stride=%s, padding=%s)' % (self.kernel_size, self.stride, self.padding)

    def forward_shape(self, input_shape):
        input_depth = input_shape[2]
        input_height = input_shape[3]
        input_width = input_shape[4]
        if self.global_pooling:
            output_depth = 1
            output_height = 1
            output_width = 1
        elif self.ceil_mode:
            output_depth = int(math.ceil((input_depth + 2 * self.padding[0] - self.kernel_size[0]) / float(self.stride[0]))) + 1
            output_height = int(math.ceil((input_height + 2 * self.padding[1] - self.kernel_size[1]) / float(self.stride[1]))) + 1
            output_width = int(math.ceil((input_width + 2 * self.padding[2] - self.kernel_size[2]) / float(self.stride[2]))) + 1
        else:
            output_depth = int(math.floor((input_depth + 2 * self.padding[0] - self.kernel_size[0]) / float(self.stride[0]))) + 1
            output_height = int(math.floor((input_height + 2 * self.padding[1] - self.kernel_size[1]) / float(self.stride[1]))) + 1
            output_width = int(math.floor((input_width + 2 * self.padding[2] - self.kernel_size[2]) / float(self.stride[2]))) + 1
        output_shape = [input_shape[0], input_shape[1], output_depth, output_height, output_width]
        return output_shape

    def forward(self, x):
        if self.global_pooling:
            depth = x.size(2)
            width = x.size(4)
            height = x.size(3)
            if self.pool_type == 'MAX':
                return F.max_pool3d(x, (depth, height, width), stride=None, padding=0, ceil_mode=self.ceil_mode)
            elif self.pool_type == 'AVE':
                return F.avg_pool3d(x, (depth, height, width), stride=None, padding=0, ceil_mode=self.ceil_mode)
        else:
            return self.pooling(x)

    def forward_RF(self, input_RF):
        in_rf_size_d = input_RF[0]
        in_rf_size_h = input_RF[1]
        in_rf_size_w = input_RF[2]
        in_rf_step_d = input_RF[3]
        in_rf_step_h = input_RF[4]
        in_rf_step_w = input_RF[5]
        kernel_d = self.kernel_size[0]
        kernel_h = self.kernel_size[1]
        kernel_w = self.kernel_size[2]
        stride_d = self.stride[0]
        stride_h = self.stride[1]
        stride_w = self.stride[2]
        out_rf_size_d = in_rf_size_d + (kernel_d - 1) * in_rf_step_d
        out_rf_size_h = in_rf_size_h + (kernel_h - 1) * in_rf_step_h
        out_rf_size_w = in_rf_size_w + (kernel_w - 1) * in_rf_step_w
        out_rf_step_d = in_rf_step_d * stride_d
        out_rf_step_h = in_rf_step_h * stride_h
        out_rf_step_w = in_rf_step_w * stride_w
        return [out_rf_size_d, out_rf_size_h, out_rf_size_w, out_rf_step_d, out_rf_step_h, out_rf_step_w]
