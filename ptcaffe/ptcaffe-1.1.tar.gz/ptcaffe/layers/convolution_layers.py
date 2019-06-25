from __future__ import division, print_function
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict
import numpy as np
import copy

from ptcaffe.utils.config import cfg
from ptcaffe.utils.filler import xavier_init, msra_init
from ptcaffe.utils.logger import logger

__all__ = ['Convolution', 'Convolution3D', 'Deconvolution', 'SConvolution']


class Convolution(nn.Conv2d):
    def __init__(self, layer, input_shape):
        convolution_param = layer['convolution_param']
        channels = input_shape[1]
        out_filters = int(convolution_param['num_output'])
        if 'kernel_size' in convolution_param:
            kernel_size = int(convolution_param['kernel_size'])
            kernel_h = kernel_size
            kernel_w = kernel_size
        elif 'kernel_h' in convolution_param and 'kernel_w' in convolution_param:
            kernel_h = int(convolution_param['kernel_h'])
            kernel_w = int(convolution_param['kernel_w'])
        else:
            raise ValueError('missing kernel size')
        stride_h = 1
        stride_w = 1
        if 'stride' in convolution_param:
            stride = int(convolution_param['stride'])
            stride_h = stride
            stride_w = stride
        elif 'stride_h' in convolution_param and 'stride_w' in convolution_param:
            stride_h = int(convolution_param['stride_h'])
            stride_w = int(convolution_param['stride_w'])
        pad_h = 0
        pad_w = 0
        if 'pad' in convolution_param:
            pad = int(convolution_param['pad'])
            pad_h = pad
            pad_w = pad
        elif 'pad_h' in convolution_param and 'pad_w' in convolution_param:
            pad_h = int(convolution_param['pad_h'])
            pad_w = int(convolution_param['pad_w'])
        self.pad_lrtb = None
        if 'pad_l' in convolution_param or 'pad_r' in convolution_param or 'pad_t' in convolution_param or 'pad_b' in convolution_param:
            assert('pad_l' in convolution_param and 'pad_r' in convolution_param and 'pad_t' in convolution_param and 'pad_b' in convolution_param)
            pad_l = int(convolution_param['pad_l'])
            pad_r = int(convolution_param['pad_r'])
            pad_t = int(convolution_param['pad_t'])
            pad_b = int(convolution_param['pad_b'])
            self.pad_lrtb = [pad_l, pad_r, pad_t, pad_b]
        self.tf_padding = convolution_param.get('tf_padding', None)
        kernel_size = (kernel_h, kernel_w)
        stride = (stride_h, stride_w)
        padding = (pad_h, pad_w)
        group = int(convolution_param['group']) if 'group' in convolution_param else 1
        dilation = 1
        if 'dilation' in convolution_param:
            dilation = int(convolution_param['dilation'])
        bias = True
        if 'bias_term' in convolution_param and convolution_param['bias_term'] == 'false':
            bias = False
        super(Convolution, self).__init__(channels, out_filters, kernel_size, stride, padding=padding, dilation=dilation, groups=group, bias=bias)

        # init weights
        weight_filler = convolution_param.get('weight_filler', OrderedDict())
        weight_filler_type = weight_filler.get('type', cfg.DEFAULT_WEIGHT_FILLER_TYPE)
        #print('Init layer %s weight with %s' % (layer['name'], weight_filler_type))
        variance_norm = weight_filler.get('variance_norm', cfg.DEFAULT_VARIANCE_NORM)
        nonlinearity = weight_filler.get('nonlinearity', cfg.DEFAULT_NONLINEARITY)
        if weight_filler_type == 'xavier':
            xavier_init(self.weight, variance_norm, nonlinearity)
        elif weight_filler_type == 'msra':
            msra_init(self.weight, variance_norm, nonlinearity)
        elif weight_filler_type == 'gaussian':
            std = float(weight_filler['std'])
            torch.nn.init.normal_(self.weight, 0, std)
        elif weight_filler_type == 'unitzero':
            self.weight.data.zero_()
            kernel_h = kernel_size[0]
            kernel_w = kernel_size[1]
            assert(kernel_h % 2 == 1)
            assert(kernel_w % 2 == 1)
            print('conv_weight size:', self.weight.size())
            for n in range(self.weight.size(0)):
                c = n
                h = int((kernel_h - 1) / 2)
                w = int((kernel_w - 1) / 2)
                self.weight.data[n][c][h][w] = 1
        elif weight_filler_type == 'none':
            pass
        else:
            raise ValueError('Unknown filler type {!r}'.format(weight_filler))

        if bias:
            bias_filler = convolution_param.get('bias_filler', OrderedDict())
            bias_filler_type = bias_filler.get('type', cfg.DEFAULT_BIAS_FILLER_TYPE)
            if bias_filler_type == 'constant':
                value = float(bias_filler.get('value', 0.0))
                self.bias.data.fill_(value)
            elif bias_filler_type == 'yolo_bias':
                num_anchors = int(bias_filler['num_anchors'])
                self.bias.data.zero_()
                self.bias.data.view(num_anchors, -1)[:, 0:2].fill_(0.5)
            elif bias_filler_type == 'focal':
                pi = float(bias_filler['pi'])
                index = int(bias_filler['index'])
                self.bias.data.zero_()
                self.bias.data[index] = - math.log((1 - pi) / pi)
            elif bias_filler_type == 'none':
                pass
            else:
                raise ValueError('Unknown filler type {!r}'.format(weight_filler))

        # distributed params
        distributed_param = layer.get('distributed_param', OrderedDict())
        self.sync_params = (distributed_param.get('sync_params', 'true') == 'true')

    @staticmethod
    def calc_tf_padding(padding_method, height, width, stride, kernel_size):
        assert(isinstance(stride, tuple) and len(stride) == 2)
        assert(isinstance(kernel_size, tuple) and len(kernel_size) == 2)
        stride_h = stride[0]
        stride_w = stride[1]
        kernel_h = kernel_size[0]
        kernel_w = kernel_size[1]
        dilation_h = 1
        dilation_w = 1
        if padding_method == 'SAME':
            pad_w = kernel_w // 2
            pad_h = kernel_h // 2
            out_hei = (height + 2 * pad_h - dilation_h * (kernel_h - 1) - 1) // stride_h + 1
            out_wid = (width + 2 * pad_w - dilation_w * (kernel_w - 1) - 1) // stride_w + 1
            pad_hei = (out_hei - 1) * stride_h + (kernel_h - 1) * dilation_h + 1 - height
            pad_wid = (out_wid - 1) * stride_w + (kernel_w - 1) * dilation_w + 1 - width

            pad_l = pad_wid // 2
            pad_r = pad_wid - pad_l
            pad_t = pad_hei // 2
            pad_b = pad_hei - pad_t
            pad_lrtb = [pad_l, pad_r, pad_t, pad_b]
        elif padding_method == 'VALID':
            pad_lrtb = [0, 0, 0, 0]
        return pad_lrtb

    def forward(self, x):
        if self.pad_lrtb is not None:
            x = F.pad(x, self.pad_lrtb)
            return super(Convolution, self).forward(x)
        elif self.tf_padding is not None:
            pad_lrtb = self.calc_tf_padding(self.tf_padding, x.shape[2], x.shape[3], self.stride, self.kernel_size)
            x = F.pad(x, pad_lrtb)
            return super(Convolution, self).forward(x)
        else:
            return super(Convolution, self).forward(x)

    def forward_shape(self, input_shape):
        if self.pad_lrtb is not None:
            input_shape = copy.copy(input_shape) # to avoid modify original input_shape
            input_shape[2] += self.pad_lrtb[2] # height
            input_shape[2] += self.pad_lrtb[3] # height
            input_shape[3] += self.pad_lrtb[0] # width
            input_shape[3] += self.pad_lrtb[1] # width
        elif self.tf_padding is not None:
            input_shape = copy.copy(input_shape) # to avoid modify original input_shape
            pad_lrtb = self.calc_tf_padding(self.tf_padding, input_shape[2], input_shape[3], self.stride, self.kernel_size)
            input_shape[2] += pad_lrtb[2] # height
            input_shape[2] += pad_lrtb[3] # height
            input_shape[3] += pad_lrtb[0] # width
            input_shape[3] += pad_lrtb[1] # width

        kernel_h = self.kernel_size[0]
        kernel_w = self.kernel_size[1]
        pad_h = self.padding[0]
        pad_w = self.padding[1]
        stride_h = self.stride[0]
        stride_w = self.stride[1]
        dilation_h = self.dilation[0]
        dilation_w = self.dilation[1]
        input_width = input_shape[3]
        input_height = input_shape[2]
        output_width = int((input_width + 2 * pad_w - dilation_w * (kernel_w - 1) - 1) / stride_w) + 1
        output_height = int((input_height + 2 * pad_h - dilation_h * (kernel_h - 1) - 1) / stride_h) + 1
        output_shape = [input_shape[0], self.out_channels, output_height, output_width]
        return output_shape

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


class Convolution3D(nn.Conv3d):
    def __init__(self, layer, input_shape):
        convolution_param = layer['convolution3d_param']
        channels = input_shape[1]
        out_filters = int(convolution_param['num_output'])

        kernel_d = 1
        if 'kernel_size' in convolution_param:
            kernel_size = int(convolution_param['kernel_size'])
            kernel_d = kernel_size
            kernel_h = kernel_size
            kernel_w = kernel_size
        elif 'kernel_h' in convolution_param and 'kernel_w' in convolution_param:
            kernel_h = int(convolution_param['kernel_h'])
            kernel_w = int(convolution_param['kernel_w'])

        if 'kernel_depth' in convolution_param:
            kernel_d = int(convolution_param['kernel_depth'])

        stride_d = 1
        stride_h = 1
        stride_w = 1
        if 'stride' in convolution_param:
            stride = int(convolution_param['stride'])
            stride_d = stride
            stride_h = stride
            stride_w = stride
        elif 'stride_h' in convolution_param and 'stride_w' in convolution_param:
            stride_d = int(convolution_param['stride_d'])
            stride_h = int(convolution_param['stride_h'])
            stride_w = int(convolution_param['stride_w'])
        if 'temporal_stride' in convolution_param:
            stride_d = int(convolution_param['temporal_stride'])

        pad_d = 0
        pad_h = 0
        pad_w = 0
        if 'pad' in convolution_param:
            pad = int(convolution_param['pad'])
            pad_h = pad
            pad_w = pad
        elif 'pad_h' in convolution_param and 'pad_w' in convolution_param:
            pad_h = int(convolution_param['pad_h'])
            pad_w = int(convolution_param['pad_w'])
        if 'temporal_pad' in convolution_param:
            pad_d = int(convolution_param['temporal_pad'])

        kernel_size = (kernel_d, kernel_h, kernel_w)
        stride = (stride_d, stride_h, stride_w)
        padding = (pad_d, pad_h, pad_w)
        group = int(convolution_param['group']) if 'group' in convolution_param else 1
        dilation = 1
        if 'dilation' in convolution_param:
            dilation = int(convolution_param['dilation'])
        dilation = (dilation)
        bias = True
        if 'bias_term' in convolution_param and convolution_param['bias_term'] == 'false':
            bias = False
        super(Convolution3D, self).__init__(channels, out_filters, kernel_size, stride, padding=padding, dilation=dilation, groups=group, bias=bias)

        # init weights
        weight_filler = convolution_param.get('weight_filler', OrderedDict())
        weight_filler_type = weight_filler.get('type', cfg.DEFAULT_WEIGHT_FILLER_TYPE)
        #print('Init layer %s weight with %s' % (layer['name'], weight_filler_type))
        if weight_filler_type == 'xavier':
            gain = cfg.DEFAULT_WEIGHT_FILLER_GAIN
            if 'gain' in weight_filler:
                gain = float(weight_filler['gain'])
            torch.nn.init.xavier_uniform_(self.weight, gain=gain)
        elif weight_filler_type == 'msra':
            variance_norm = weight_filler.get('variance_norm', cfg.DEFAULT_VARIANCE_NORM)
            if variance_norm == 'FAN_IN':
                torch.nn.init.kaiming_normal_(self.weight, mode='fan_in')
            else:  # if variance_norm == 'FAN_OUT':
                torch.nn.init.kaiming_normal_(self.weight, mode='fan_out')
        elif weight_filler_type == 'gaussian':
            std = float(weight_filler['std'])
            torch.nn.init.normal_(self.weight, 0, std)
        elif weight_filler_type == 'unitzero':
            self.weight.data.zero_()
            kernel_d = kernel_size[0]
            kernel_h = kernel_size[1]
            kernel_w = kernel_size[2]
            assert(kernel_h % 2 == 1)
            assert(kernel_w % 2 == 1)
            print('conv_weight size:', self.weight.size())
            for n in range(self.weight.size(0)):
                c = n
                d = int((kernel_d - 1) / 2)
                h = int((kernel_h - 1) / 2)
                w = int((kernel_w - 1) / 2)
                self.weight.data[n][c][d][h][w] = 1
        elif weight_filler_type == 'none':
            pass
        else:
            raise ValueError('Unknown filler type {!r}'.format(weight_filler))

        if bias:
            bias_filler = convolution_param.get('bias_filler', OrderedDict())
            bias_filler_type = bias_filler.get('type', cfg.DEFAULT_BIAS_FILLER_TYPE)
            if bias_filler_type == 'constant':
                value = float(bias_filler.get('value', 0.0))
                self.bias.data.zero_()
                self.bias.data += value
            elif bias_filler_type == 'yolo_bias':
                num_anchors = int(bias_filler['num_anchors'])
                self.bias.data.zero_()
                self.bias.data.view(num_anchors, -1)[:, 0:2].fill_(0.5)
            elif bias_filler_type == 'focal':
                pi = float(bias_filler['pi'])
                index = int(bias_filler['index'])
                self.bias.data.zero_()
                self.bias.data[index] = - math.log((1 - pi) / pi)
            elif bias_filler_type == 'none':
                pass
            else:
                raise ValueError('Unknown filler type {!r}'.format(weight_filler))

        # distributed params
        distributed_param = layer.get('distributed_param', OrderedDict())
        self.sync_params = (distributed_param.get('sync_params', 'true') == 'true')

    def forward_shape(self, input_shape):
        kernel_d = self.kernel_size[0]
        kernel_h = self.kernel_size[1]
        kernel_w = self.kernel_size[2]
        pad_d = self.padding[0]
        pad_h = self.padding[1]
        pad_w = self.padding[2]
        stride_d = self.stride[0]
        stride_h = self.stride[1]
        stride_w = self.stride[2]
        dilation_d = self.dilation[0]
        dilation_h = self.dilation[1]
        dilation_w = self.dilation[2]
        input_depth = input_shape[2]
        input_height = input_shape[3]
        input_width = input_shape[4]
        output_depth = int((input_depth + 2 * pad_d - dilation_d * (kernel_d - 1) - 1) / stride_d) + 1
        output_width = int((input_width + 2 * pad_w - dilation_w * (kernel_w - 1) - 1) / stride_w) + 1
        output_height = int((input_height + 2 * pad_h - dilation_h * (kernel_h - 1) - 1) / stride_h) + 1
        output_shape = [input_shape[0], self.out_channels, output_depth, output_height, output_width]
        return output_shape

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


class Deconvolution(nn.ConvTranspose2d):
    def __init__(self, layer, input_shape):
        in_channels = input_shape[1]
        convolution_param = layer.get('convolution_param', OrderedDict())
        out_channels = int(convolution_param['num_output'])
        group = int(convolution_param.get('group', 1))
        if 'kernel_size' in convolution_param:
            kernel_size = int(convolution_param['kernel_size'])
            kernel_h = kernel_size
            kernel_w = kernel_size
        elif 'kernel_h' in convolution_param and 'kernel_w' in convolution_param:
            kernel_h = int(convolution_param['kernel_h'])
            kernel_w = int(convolution_param['kernel_w'])
        stride_h, stride_w = 1, 1
        if 'stride' in convolution_param:
            stride = int(convolution_param['stride'])
            stride_h = stride
            stride_w = stride
        elif 'stride_h' in convolution_param and 'stride_w' in convolution_param:
            stride_h = int(convolution_param['stride_h'])
            stride_w = int(convolution_param['stride_w'])
        pad_h = 0
        pad_w = 0
        if 'pad' in convolution_param:
            pad = int(convolution_param['pad'])
            pad_h = pad
            pad_w = pad
        elif 'pad_h' in convolution_param and 'pad_w' in convolution_param:
            pad_h = int(convolution_param['pad_h'])
            pad_w = int(convolution_param['pad_w'])
        kernel_size = (kernel_h, kernel_w)
        stride = (stride_h, stride_w)
        padding = (pad_h, pad_w)
        bias_term = (convolution_param.get('bias_term', 'true') == 'true')
        super(Deconvolution, self).__init__(in_channels, out_channels, kernel_size=kernel_size, stride=stride,
                                            padding=padding, groups=group, bias=bias_term)
        # init weights
        weight_filler = convolution_param.get('weight_filler', OrderedDict())
        weight_filler_type = weight_filler.get('type', 'bilinear')
        if weight_filler_type == 'bilinear':
            assert kernel_w == kernel_h
            if group == 1:
                assert in_channels == out_channels
                initial_weight = self.get_upsampling_weight(in_channels, out_channels, kernel_w)
                self.weight.data.copy_(initial_weight)
            elif group == in_channels:
                f = math.ceil(kernel_w / 2.0)
                c = (kernel_w - 1.0) / (2.0 * f)
                weight_data = self.weight.data.view(-1)
                for i in range(self.weight.numel()):
                    x = i % kernel_w
                    y = int(i / kernel_w) % kernel_h
                    weight_data[i] = (1.0 - abs(x / f - c)) * (1.0 - abs(y / f - c))
            else:
                logger.warning('unable to do bilinear initialize for deconvolution layer')

        # distributed params
        distributed_param = layer.get('distributed_param', OrderedDict())
        self.sync_params = (distributed_param.get('sync_params', 'true') == 'true')

    # https://github.com/wkentaro/pytorch-fcn/blob/master/torchfcn/models/fcn32s.py

    def get_upsampling_weight(self, in_channels, out_channels, kernel_size):
        """Make a 2D bilinear kernel suitable for upsampling"""
        factor = (kernel_size + 1) // 2
        if kernel_size % 2 == 1:
            center = factor - 1
        else:
            center = factor - 0.5
        og = np.ogrid[:kernel_size, :kernel_size]
        filt = (1 - abs(og[0] - center) / factor) * \
               (1 - abs(og[1] - center) / factor)
        weight = np.zeros((in_channels, out_channels, kernel_size, kernel_size),
                          dtype=np.float64)
        weight[range(in_channels), range(out_channels), :, :] = filt
        return torch.from_numpy(weight).float()

    def forward_shape(self, input_shape):
        output_shape = [input_shape[0], self.out_channels, self.stride[0] * input_shape[2], self.stride[1] * input_shape[3]]
        return output_shape

    def forward_RF(self, input_RF):
        in_rf_size_h = input_RF[0]
        in_rf_size_w = input_RF[1]
        in_rf_step_h = input_RF[2]
        in_rf_step_w = input_RF[3]
        kernel_h = self.kernel_size[0]
        kernel_w = self.kernel_size[1]
        stride_h = self.stride[0]
        stride_w = self.stride[1]
        out_rf_size_h = in_rf_size_h + in_rf_step_h
        out_rf_size_w = in_rf_size_w + in_rf_step_w
        out_rf_step_h = int(in_rf_step_h / stride_h)
        out_rf_step_w = int(in_rf_step_w / stride_w)
        return [out_rf_size_h, out_rf_size_w, out_rf_step_h, out_rf_step_w]


class SConvolution(Convolution):
    def __init__(self, layer, input_shape):
        super(SConvolution, self).__init__(layer, input_shape)
        sparse_param = layer.get('sparse_param', OrderedDict())
        self.sparsity = 0.0
        if 'sparsity' in sparse_param:
            self.sparsity = float(sparse_param['sparsity'])
            assert(self.sparsity < 1.0 and self.sparsity >= 0)
        self.register_buffer('mask', torch.ones(self.weight.shape))
        self.RECOVER = False
        self.seen = 0

    def __repr__(self):
        return 'SConvolution(%d, %d, kernel_size=%s, stride=%s, sparsity=%f)' % (
            self.in_channels, self.out_channels, self.kernel_size, self.stride, self.sparsity)

    def set_sparsity(self):
        if self.sparsity > 0.0:
            num = self.weight.data.numel()
            k = max(int(num * (1 - self.sparsity)), 1)
            thresh = self.weight.data.abs().view(-1).topk(k)[0][-1]
            self.mask = (self.weight.data.abs() >= thresh).float()
            if not self.RECOVER:
                self.weight.data = self.weight.data * self.mask

    def forward(self, input):
        if self.seen == 0:
            self.set_sparsity()
        self.seen += 1
        weight = self.weight * self.mask
        return F.conv2d(input, weight, self.bias, self.stride,
                        self.padding, self.dilation, self.groups)
