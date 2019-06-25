from __future__ import division, print_function
import warnings
import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parameter import Parameter
from collections import OrderedDict
from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.utils.utils import make_list

__all__ = ['Upsample', 'Eltwise', 'Scale', 'Concat', 'Reshape', 'Squeeze', 'Unsqueeze', 'Padding', 'ShuffleChannel', 'SwapChannels']


class Upsample(nn.Upsample):
    def __init__(self, layer, input_shape):
        upsample_param = layer.get('upsample_param', OrderedDict())
        scale_factor = int(upsample_param.get('scale_factor', 2))
        mode = upsample_param.get('mode', 'bilinear')
        align_corners = (upsample_param.get('upsample_param', 'true') == 'true')
        super(Upsample, self).__init__(scale_factor=scale_factor, mode=mode, align_corners=align_corners)

    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        output_shape[2] = int(self.scale_factor * input_shape[2])
        output_shape[3] = int(self.scale_factor * input_shape[3])
        return output_shape


class Eltwise(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(Eltwise, self).__init__()
        operation = 'SUM'
        if 'eltwise_param' in layer and 'operation' in layer['eltwise_param']:
            operation = layer['eltwise_param']['operation']
        self.operation = operation

    def __repr__(self):
        return 'Eltwise %s' % self.operation

    def forward_shape(self, *input_shapes):
        if self.operation == 'UPSUM':
            return copy.copy(input_shapes[1])
        else:
            return copy.copy(input_shapes[0])

    def forward_RF(self, *input_RFs):
        if self.operation == 'UPSUM':
            assert(False)
            return input_RFs[0]
        else:
            if len(input_RFs[0]) == 6:
                output_RF = copy.copy(input_RFs[0])
                for i in range(1, len(input_RFs)):
                    assert(output_RF[3] == input_RFs[i][3])
                    assert(output_RF[4] == input_RFs[i][4])
                    assert(output_RF[5] == input_RFs[i][5])
                    output_RF[0] = max(output_RF[0], input_RFs[i][0])
                    output_RF[1] = max(output_RF[1], input_RFs[i][1])
                    output_RF[2] = max(output_RF[2], input_RFs[i][2])
                return output_RF
            else:
                output_RF = copy.copy(input_RFs[0])
                for i in range(1, len(input_RFs)):
                    output_RF[0] = max(output_RF[0], input_RFs[i][0])
                    output_RF[1] = max(output_RF[1], input_RFs[i][1])
                    output_RF[2] = max(output_RF[2], input_RFs[i][2])
                    output_RF[3] = max(output_RF[3], input_RFs[i][3])
                return output_RF

    def forward(self, *inputs):
        if self.operation == '+' or self.operation == 'SUM':
            x = inputs[0]
            for i in range(1, len(inputs)):
                x = x + inputs[i]
            return x
        elif self.operation == '-' or self.operation == 'SUB':
            return inputs[0] - inputs[1]
        elif self.operation == '+' or self.operation == 'AVG':
            x = inputs[0]
            for i in range(1, len(inputs)):
                x = x + inputs[i]
            x = x / len(inputs)
            return x
        elif self.operation == '*' or self.operation == 'MUL_SWITCH':
            assert(len(inputs) == 2)
            x = inputs[0]
            switch = inputs[1].expand_as(x)
            x = x * switch
            return x
        elif self.operation == '*' or self.operation == 'MUL' or self.operation == 'PROD':
            x = inputs[0]
            for i in range(1, len(inputs)):
                x = x * inputs[i]
            return x
        elif self.operation == '/' or self.operation == 'DIV':
            x = inputs[0]
            for i in range(1, len(inputs)):
                x = x / inputs[i]
            return x
        elif self.operation == 'MAX':
            x = inputs[0]
            for i in range(1, len(inputs)):
                x = torch.max(x, inputs[i])
            return x
        elif self.operation == 'MAXPOS':
            assert(len(inputs) == 2)
            x1 = inputs[0]
            x2 = inputs[1]
            assert(x1.dim() == 4)
            assert(x2.dim() == 4)
            assert(x1.size(1) == 2)
            assert(x2.size(1) == 2)
            x1_pos = x1[:, 1, :, :] - x1[:, 0, :, :]
            x2_pos = x2[:, 1, :, :] - x2[:, 0, :, :]
            x1_mask = (x1_pos > x2_pos).unsqueeze(1).expand_as(x1).float()
            x2_mask = (x2_pos > x1_pos).unsqueeze(1).expand_as(x2).float()
            x = x1 * x1_mask + x2 * x2_mask
            return x
        elif self.operation == 'MINMAX':
            assert(len(inputs) == 2)
            x1 = inputs[0]
            x2 = inputs[1]
            assert(x1.dim() == 4)
            assert(x2.dim() == 4)
            assert(x1.size(1) == 2)
            assert(x2.size(1) == 2)
            min_vals = torch.min(x1[:, 0, :, :], x2[:, 0, :, :]).unsqueeze(1)
            max_vals = torch.max(x1[:, 1, :, :], x2[:, 1, :, :]).unsqueeze(1)
            x = torch.cat([min_vals, max_vals], 1)
            return x
        elif self.operation == 'MAXMIN':
            assert(len(inputs) == 2)
            x1 = inputs[0]
            x2 = inputs[1]
            assert(x1.dim() == 4)
            assert(x2.dim() == 4)
            assert(x1.size(1) == 2)
            assert(x2.size(1) == 2)
            max_vals = torch.max(x1[:, 0, :, :], x2[:, 0, :, :]).unsqueeze(1)
            min_vals = torch.min(x1[:, 1, :, :], x2[:, 1, :, :]).unsqueeze(1)
            x = torch.cat([max_vals, min_vals], 1)
            return x
        elif self.operation == 'UPSUM':
            low_res_feats = inputs[0]
            high_res_feats = inputs[1]
            high_res_width = high_res_feats.size(3)
            high_res_height = high_res_feats.size(2)
            low_res_feats_up = F.upsample(low_res_feats, (high_res_height, high_res_width), mode='bilinear')
            return low_res_feats_up + high_res_feats
        else:
            assert False, 'forward Eltwise, unknown operator %s' % self.operation

class ScaleFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x_norm, weight, bias):
        from ptcaffe import _C
        _C.scale_forward(x_norm, weight, bias)
        ctx.save_for_backward(x_norm, weight.data, bias.data)
        return x_norm

    @staticmethod
    def backward(ctx, grad_output):
        from ptcaffe import _C
        x_norm, weight, bias = ctx.saved_tensors
        _C.scale_backward(x_norm, weight, bias)

        grad_bias = grad_output.sum(0).sum(1).sum(1).squeeze(0)

        grad_weight = x_norm
        _C.tensor_multiply(grad_weight, grad_output)  # grad_weight = grad_weight * grad_output
        grad_weight = grad_weight.sum(0).sum(1).sum(1).squeeze(0)

        grad_x = grad_output
        _C.tensor_array_multiply(grad_x, weight)      # grad_x = grad_x * weight

        return grad_x, grad_weight, grad_bias

class Scale(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(Scale, self).__init__()
        bnames = layer['bottom']
        self.bnames = bnames if isinstance(bnames, list) else [bnames]
        scale_param = layer.get('scale_param', OrderedDict())

        if len(self.bnames) == 2:  # for SENet
            scale_param = layer.get('scale_param', OrderedDict())
            self.axis = int(scale_param.get('axis', 0))
            self.bias_term = (scale_param.get('bias_term', 'false') == 'true')
        else:  # for BatchNorm
            channels = input_shapes[0][1]
            self.weight = Parameter(torch.Tensor(channels))

            bias_term = cfg.DEFAULT_SCALE_BIAS
            if 'bias_term' in scale_param:
                bias_term = (scale_param['bias_term'] == 'true')

            if bias_term:
                self.bias = Parameter(torch.Tensor(channels))
            else:
                self.register_parameter('bias', None)
            self.channels = channels

            scale_param = layer.get('scale_param', OrderedDict())
            if 'weight_filler' in scale_param:
                logger.warning("Please use filler instead of weight_filler in scale_param")

            weight_filler = OrderedDict()
            if 'filler' in scale_param:
                weight_filler = scale_param['filler']
            elif 'weight_filler' in scale_param:
                weight_filler = scale_param['weight_filler']

            weight_filler_type = weight_filler.get('type', 'gaussian')
            if weight_filler_type == 'gaussian':
                mean_val = float(weight_filler.get('mean', 1.0))
                std_val = float(weight_filler.get('std', 0.02))
                torch.nn.init.normal(self.weight.data, mean_val, std_val)
            elif weight_filler_type == 'constant':
                value = float(weight_filler['value'])
                self.weight.data.fill_(value)
            elif weight_filler_type == 'none':
                pass
            else:
                mean_val = 1.0
                std_val = 0.02
                torch.nn.init.normal(self.weight.data, mean_val, std_val)

            if bias_term:
                bias_filler = scale_param.get('bias_filler', OrderedDict())
                bias_filler_type = bias_filler.get('type', 'constant')
                if bias_filler_type == 'constant':
                    value = float(bias_filler.get('value', 0.0))
                    self.bias.data.fill_(value)
                elif bias_filler_type == 'none':
                    pass
                else:
                    self.bias.data.fill_(0.0)

        # distributed params
        distributed_param = layer.get('distributed_param', OrderedDict())
        self.sync_params = (distributed_param.get('sync_params', 'true') == 'true')

    def __repr__(self):
        if len(self.bnames) == 1:
            return 'Scale(channels = %d)' % self.channels
        else:
            return 'Scale(axis = %d)' % self.axis

    def forward_shape(self, *input_shapes):
        return copy.copy(input_shapes[0])

    def forward(self, *inputs):
        if len(self.bnames) == 2:
            x = inputs[0]
            y = inputs[1]
            assert(x.size(1) == y.size(1))
            nB = y.size(0)
            nC = y.size(1)
            y = y.view(nB, nC, 1, 1)
            return x * y
        else:
            x = inputs[0]
            if x.dim() == 5:
                nB = x.size(0)
                nC = x.size(1)
                nD = x.size(2)
                nH = x.size(3)
                nW = x.size(4)
                x = x * self.weight.view(1, nC, 1, 1, 1) + self.bias.view(1, nC, 1, 1, 1)
                return x
            elif x.dim() == 4:
                nB = x.size(0)
                nC = x.size(1)
                nH = x.size(2)
                nW = x.size(3)
                if self.bias is not None:
                    try:
                        from ptcaffe import _C
                        return ScaleFunction.apply(x, self.weight, self.bias)
                    except:
                        warnings.warn('Unable to import ptcaffe._C, the scale layer after batch norm will be very slow and time consuming. You\'d better set affine = True in batch norm layer, instead of using scale layer.')
                        x = x * self.weight.view(1, nC, 1, 1) + self.bias.view(1, nC, 1, 1)
                else:
                    x = x * self.weight.view(1, nC, 1, 1)
                return x
            elif x.dim() == 2:
                nB = x.size(0)
                nC = x.size(1)
                if cfg.VERBOSE_LEVEL >= 2:
                    print('Scale implemention changed for torch 0.4.0')
                x = x * self.weight.view(1, nC) + self.bias.view(1, nC)
                return x
            else:
                assert(False)


class Concat(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(Concat, self).__init__()
        axis = 1
        if 'concat_param' in layer and 'axis' in layer['concat_param']:
            axis = int(layer['concat_param']['axis'])
        self.axis = axis

    def __repr__(self):
        return 'Concat(axis=%d)' % self.axis

    def forward_shape(self, *input_shapes):
        output_shape = copy.copy(input_shapes[0])
        for i in range(1, len(input_shapes)):
            output_shape[self.axis] += input_shapes[i][self.axis]
        return output_shape

    def forward_RF(self, *input_RFs):
        output_RF = copy.copy(input_RFs[0])
        for i in range(1, len(input_RFs)):
            output_RF[0] = max(output_RF[0], input_RFs[i][0])
            output_RF[1] = max(output_RF[1], input_RFs[i][1])
            output_RF[2] = max(output_RF[2], input_RFs[i][2])
            output_RF[3] = max(output_RF[3], input_RFs[i][3])
        return output_RF

    def forward(self, *inputs):
        return torch.cat(inputs, self.axis)


class Reshape(nn.Module):
    def __init__(self, layer, input_shape):
        super(Reshape, self).__init__()
        reshape_dims = layer['reshape_param']['shape']['dim']
        if type(reshape_dims) is list:
            reshape_dims = [int(item) for item in reshape_dims]
        else:
            reshape_dims = [int(reshape_dims)]
        self.dims = reshape_dims

    def __repr__(self):
        return 'Reshape(dims=%s)' % (self.dims)

    def forward_shape(self, input_shape):
        orig_dims = input_shape
        orig_total = 1
        for dim in input_shape:
            orig_total *= dim
        new_dims = [orig_dims[i] if self.dims[i] == 0 else self.dims[i] for i in range(len(self.dims))]
        new_total = 1
        for dim in new_dims:
            if dim != -1:
                new_total *= dim
        for i in range(len(new_dims)):
            if new_dims[i] == -1:
                assert(orig_total % new_total == 0)
                new_dims[i] = int(orig_total / new_total)
                break
        return new_dims

    def forward(self, x):
        orig_dims = x.size()
        #assert(len(orig_dims) == len(self.dims))
        new_dims = [orig_dims[i] if self.dims[i] == 0 else self.dims[i] for i in range(len(self.dims))]

        return x.view(*new_dims)  # .contiguous()


class Squeeze(nn.Module):
    def __init__(self, layer, input_shape):
        super(Squeeze, self).__init__()
        self.squeeze_dims = make_list(layer['squeeze_param']['dim'])
        self.squeeze_dims = [int(dim) for dim in self.squeeze_dims]

        # check
        for idx, dim in enumerate(self.squeeze_dims):
            if idx < len(self.squeeze_dims) -1:
                assert(self.squeeze_dims[idx] < self.squeeze_dims[idx+1])

    def __repr__(self):
        return 'Squeeze(%s)' % self.squeeze_dims

    def forward_shape(self, input_shape):
        output_shape =[] # copy.copy(input_shape)
        for dim in range(len(input_shape)):
            if dim not in self.squeeze_dims:
                output_shape.append(input_shape[dim])
            else:
                assert(input_shape[dim] == 1)
        return output_shape

    def forward(self, x):
        for idx, dim in enumerate(self.squeeze_dims):
            x = x.squeeze(dim - idx)
        return x

class Unsqueeze(nn.Module):
    def __init__(self, layer, input_shape):
        super(Unsqueeze, self).__init__()
        self.unsqueeze_dim = int(layer['unsqueeze_param']['dim'])

    def __repr__(self):
        return 'Unsqueeze(%d)' % self.unsqueeze_dim

    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        output_shape.insert(self.unsqueeze_dim, 1)
        return output_shape

    def forward(self, x):
        return x.unsqueeze(self.unsqueeze_dim)


class Padding(nn.Module):
    def __init__(self, layer, input_shape):
        super(Padding, self).__init__()
        padding_param = layer.get('padding_param', OrderedDict())
        self.pad_left = int(padding_param.get('left', 0))
        self.pad_right = int(padding_param.get('right', 0))
        self.pad_top = int(padding_param.get('top', 0))
        self.pad_bottom = int(padding_param.get('bottom', 0))
        self.mode = padding_param.get('mode', 'replicate')  # 'constant'

    def __repr__(self):
        return "Padding(left=%d, right=%d, top=%d, bottom=%d, mode=%s)" % (self.pad_left, self.pad_right, self.pad_top, self.pad_bottom, self.mode)

    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        output_shape[2] += self.pad_top + self.pad_bottom
        output_shape[3] += self.pad_left + self.pad_right
        return output_shape

    def forward(self, x):
        return F.pad(x, (self.pad_left, self.pad_right, self.pad_top, self.pad_bottom), mode=self.mode)

class SwapChannels(nn.Module):
    def __init__(self, input, input_shape):
        super(SwapChannels, self).__init__()

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x): 
        channels = x.shape[1]
        inds = torch.linspace(channels-1, 0, channels).long().cuda(x.device)
        return x.index_select(1, inds)

class ShuffleChannel(nn.Module):
    def __init__(self, layer, input_shape):
        super(ShuffleChannel, self).__init__()
        shuffle_channel_param = layer.get('shuffle_channel_param', OrderedDict())
        self.groups = int(shuffle_channel_param.get('group', 1))

    def __repr__(self):
        return "ShuffleChannel(groups = %d)" % self.groups

    def forward(self, x):
        batchsize, num_channels, height, width = x.data.size()

        assert(num_channels % self.groups == 0)
        channels_per_group = int(num_channels / self.groups)

        # reshape
        x = x.view(batchsize, self.groups,
                   channels_per_group, height, width)

        # transpose
        # - contiguous() required if transpose() is used before view().
        #   See https://github.com/pytorch/pytorch/issues/764
        x = torch.transpose(x, 1, 2).contiguous()

        # flatten
        x = x.view(batchsize, -1, height, width)

        return x

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)
