# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

from __future__ import division, print_function

import copy
from collections import OrderedDict

import torch.nn as nn


class PrintValue(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(PrintValue, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        self.print_device = int(print_param.get('device', '0'))
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))
        self.bottom = layer['bottom']
        assert 'top' not in layer
        self.device = -1

    def set_device(self, device):
        self.device = device

    def __repr__(self):
        return "PrintValue()"

    def forward_shape(self, input_shape):
        pass

    def forward(self, x):
        if self.device == -1 or self.device == self.print_device:
            if self.device == -1:
                print('%s size: %s' % (self.bottom + '_value_cpu', list(x.size())))
            else:
                print('%s size: %s' % (self.bottom + '_value_gpu%d' % self.device, list(x.size())))
            if x.numel() > self.num:
                print(list(x.data.view(-1)[self.start:self.start + self.num]))
            elif x.numel() == 1:
                print(x.item())
            else:
                print(x.data)


class PrintMean(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(PrintMean, self).__init__()
        self.bottom = layer['bottom']
        assert 'top' not in layer

    def __repr__(self):
        return "PrintMean()"

    def forward_shape(self, input_shape):
        pass

    def forward(self, x):
        print('%s: %f' % (self.bottom, x.mean().cpu().item()))


class PrintShape(nn.Module):
    def __init__(self, layer, input_shape):
        super(PrintShape, self).__init__()
        self.bname = layer['bottom']

    def __repr__(self):
        return "PrintShape()"

    def forward_shape(self, input_shape):
        pass

    def forward(self, x):
        print('%s shape: %s' % (self.bname, list(x.shape)))


class PrintMinMax(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(PrintMinMax, self).__init__()
        self.lname = layer['name']

    def __repr__(self):
        return "PrintMinMax()"

    def forward_shape(self, input_shape):
        pass

    def forward(self, x):
        min_val = float(x.data.min())
        max_val = float(x.data.max())
        print('%s: min_val = %f, max_val = %f' % (self.lname, min_val, max_val))


class PrintGrad(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(PrintGrad, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        self.print_device = int(print_param.get('device', '0'))
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))
        self.bottom = layer['bottom']
        assert 'top' in layer
        assert layer['top'] == layer['bottom']
        self.device = -1

    def __repr__(self):
        return "PrintGrad()"

    def set_device(self, device):
        self.device = device

    def forward(self, x):
        def hook_func(grad):
            if self.device == -1 or self.device == self.print_device:
                if self.device == -1:
                    print(self.bottom + '_grad_cpu')
                else:
                    print(self.bottom + '_grad_gpu%d' % self.device)
                print(grad.size())
                if grad.numel() > self.num:
                    print(list(grad.data.view(-1)[self.start:self.start + self.num]))
                else:
                    print(grad.data)
        x.register_hook(hook_func)
        return x

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

# no input and no output


class PrintMsg(nn.Module):
    def __init__(self, layer):
        super(PrintMsg, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        self.msg = print_param.get('msg', 'I am nothing')
        self.batch_idx = 0

    def __repr__(self):
        return 'PrintMsg()'

    def forward(self):
        print('batch_dix : %d, msg: %s' % (self.batch_idx, self.msg))
        self.batch_idx += 1
        pass

    def forward_shape(self):
        pass


class Silence(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(Silence, self).__init__()
        assert 'top' not in layer

    def __repr__(self):
        return 'Silence()'

    def forward(self, *inputs):
        pass

    def forward_shape(self, *input_shapes):
        pass


class PrintWeight(nn.Module):
    def __init__(self, layer):
        super(PrintWeight, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        assert 'layer_name' in print_param
        self.layer_name = print_param.get('layer_name')
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))

    def __repr__(self):
        return 'PrintWeight(layer=%s)' % self.layer_name

    def forward(self):
        pass

    def forward_shape(self):
        pass

    def forward_extra(self, net):
        print(self.layer_name + ' weight')
        wdata = net.models[self.layer_name].weight.data
        print(wdata.size())
        if wdata.numel() > self.num:
            print(list(wdata.view(-1)[self.start:self.start + self.num]))
        else:
            print(wdata)


class PrintBias(nn.Module):
    def __init__(self, layer):
        super(PrintBias, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        assert 'layer_name' in print_param
        self.layer_name = print_param.get('layer_name')
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))

    def __repr__(self):
        return 'PrintBias(layer=%s)' % self.layer_name

    def forward(self):
        pass

    def forward_shape(self):
        pass

    def forward_extra(self, net):
        print(self.layer_name + ' bias')
        bdata = net.models[self.layer_name].bias.data
        print(bdata.size())
        if bdata.numel() > self.num:
            print(list(bdata.view(-1)[self.start:self.start + self.num]))
        else:
            print(bdata)


class PrintWeightGrad(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(PrintWeightGrad, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        assert 'layer_name' in print_param
        self.layer_name = print_param.get('layer_name')
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))
        self.hook_func = self.create_hook_func()
        self.is_hooked = False

    def __repr__(self):
        return "PrintWeightGrad()"

    def create_hook_func(self):
        def hook_func(grad):
            print(self.layer_name + ' weight grad')
            print(grad.size())
            if grad.numel() > self.num:
                print(list(grad.data.view(-1)[self.start:self.start + self.num]))
            else:
                print(grad.data)
        return hook_func

    def forward_extra(self, net):
        if not self.is_hooked:
            weight = net.models[self.layer_name].weight
            hook = weight.register_hook(self.hook_func)
            self.is_hooked = True

    def forward(self):
        pass

    def forward_shape(self):
        pass


class PrintBiasGrad(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(PrintBiasGrad, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        assert 'layer_name' in print_param
        self.layer_name = print_param.get('layer_name')
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))
        self.hook_func = self.create_hook_func()
        self.is_hooked = False

    def __repr__(self):
        return "PrintBiasGrad()"

    def create_hook_func(self):
        def hook_func(grad):
            print(self.layer_name + ' bias grad')
            print(grad.size())
            if grad.numel() > self.num:
                print(list(grad.data.view(-1)[self.start:self.start + self.num]))
            else:
                print(grad.data)
        return hook_func

    def forward_extra(self, net):
        if not self.is_hooked:
            bias = net.models[self.layer_name].bias
            hook = bias.register_hook(self.hook_func)
            self.is_hooked = True

    def forward(self):
        pass

    def forward_shape(self):
        pass


class PrintWeightUpdate(nn.Module):
    def __init__(self, layer):
        super(PrintWeightUpdate, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        assert 'layer_name' in print_param
        self.layer_name = print_param.get('layer_name')
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))
        self.prev_weight = None

    def __repr__(self):
        return 'PrintWeightUpdate(layer=%s)' % self.layer_name

    def forward(self):
        pass

    def forward_shape(self):
        pass

    def forward_extra(self, net):
        wdata = net.models[self.layer_name].weight.data
        if self.prev_weight is not None:
            wdiff = wdata - self.prev_weight
            print(self.layer_name + ' weight update')
            print(wdiff.size())
            if wdiff.numel() > self.num:
                print(list(wdiff.view(-1)[self.start:self.start + self.num]))
            else:
                print(wdiff)
        self.prev_weight = wdata.clone()


class PrintBiasUpdate(nn.Module):
    def __init__(self, layer):
        super(PrintBiasUpdate, self).__init__()
        print_param = layer.get('print_param', OrderedDict())
        assert 'layer_name' in print_param
        self.layer_name = print_param.get('layer_name')
        self.num = int(print_param.get('num', 100))
        self.start = int(print_param.get('start', 0))
        self.prev_bias = None

    def __repr__(self):
        return 'PrintBiasUpdate(layer=%s)' % self.layer_name

    def forward(self):
        pass

    def forward_shape(self):
        pass

    def forward_extra(self, net):
        bdata = net.models[self.layer_name].bias.data
        if not isinstance(self.prev_bias, type(None)):
            bdiff = bdata - self.prev_bias
            print(self.layer_name + ' bias update')
            print(bdiff.size())
            if bdiff.numel() > self.num:
                print(list(bdiff.view(-1)[self.start:self.start + self.num]))
            else:
                print(bdiff)
        self.prev_bias = bdata.clone()


class Identity(nn.Module):
    def __init__(self, layer, input_shape):
        super(Identity, self).__init__()

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        return x

class CloneOutput(nn.Module):
    def __init__(self, layer, input_shape):
        super(CloneOutput, self).__init__()

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        return x.clone()

class MaxProb(nn.Module):
    def __init__(self, layer, input_shape):
        super(MaxProb, self).__init__()

    def forward(self, x):
        max_prob, max_idx = x.max(1)
        return max_prob, max_idx

    def forward_shape(self, input_shape):
        return [input_shape[0],], [input_shape[0],]
