# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by liuyufei and xiaohang
# --------------------------------------------------------


# encoding: UTF-8

from __future__ import division, print_function
import torch
import torch.nn.functional as F
from collections import OrderedDict
from torch.autograd import Function
from .convolution_layers import Convolution
from .linear_layers import InnerProduct
from .pooling_layers import Pooling
from .activation_layers import ReLU
from ..utils.config import cfg


__all__ = ['QConvolution', 'QInnerProduct', 'QPooling', 'QReLU']


class QRound(Function):
    @staticmethod
    def forward(ctx, input):
        return input.round()

    @staticmethod
    def backward(ctx, grad):
        return grad


def bits_to_base(bits):
    if not isinstance(bits, int):
        raise TypeError('quantization reuqires bits as type int, got {!r}'.format(type(bits)))
    # 32-bits IEEE-754 floats has ~24 bits signed int
    if not 1 <= bits < 24:
        raise TypeError('quantization requires 0 <= bits < 24, got {}'.format(bits))
    return 2**bits - 1


def quantize(x, minimum=None, maximum=None, bits=8, clamp_outlier=True):
    """
    quantize `x` to `(1 - k/Q) min(x) + k/Q max(x)` where Q = 2^bits - 1 and 0 <= k <= Q
    """
    if minimum is None:
        minimum = x.min().item()
    if maximum is None:
        maximum = x.max().item()

    Q, amplitude = bits_to_base(bits), maximum - minimum
    scaled = (x - minimum) / amplitude
    if clamp_outlier:
        scaled = scaled.clamp(0, 1)
    quantized = QRound.apply(scaled * Q)
    quantized = quantized / Q * amplitude + minimum
    return quantized


class QuantizationMixin:
    def __init__(self, layer, input_shape):
        quantization_param = layer.get('quantization_param', OrderedDict())
        self.momentum = float(quantization_param.get('momentum', 0.999))
        self.register_buffer('minval', torch.zeros(1))
        self.register_buffer('maxval', torch.zeros(1))

    def update_min_max(self, input):
        minval = input.data.min()
        maxval = input.data.max()
        self.minval = self.minval * self.momentum + minval * (1 - self.momentum)
        self.maxval = self.maxval * self.momentum + maxval * (1 - self.momentum)

    def post_forward(self, input):
        if cfg.QUANTIZATION:
            return quantize(input, self.minval, self.maxval, cfg.QUANT_BITS)
        else:
            self.update_min_max(input)
            return input


class QConvolution(Convolution, QuantizationMixin):
    def __init__(self, layer, input_shape):
        Convolution.__init__(self, layer, input_shape)
        output_shape = Convolution.forward_shape(self, input_shape)
        QuantizationMixin.__init__(self, layer, output_shape)

    def forward(self, input):
        if cfg.QUANTIZATION:
            weights = quantize(
                self.weight, bits=cfg.QUANT_BITS, clamp_outlier=False)
            output = F.conv2d(input, weights, self.bias, self.stride,
                              self.padding, self.dilation, self.groups)
        else:
            output = Convolution.forward(self, input)
        return self.post_forward(output)

    def __repr__(self):
        return Convolution.__repr__(self)


class WeightContext:
    def __init__(self, weight, bias):
        self.weight = weight
        self.bias = bias


class QInnerProduct(InnerProduct, QuantizationMixin):
    def __init__(self, layer, input_shape):
        InnerProduct.__init__(self, layer, input_shape)
        output_shape = InnerProduct.forward_shape(self, input_shape)
        QuantizationMixin.__init__(self, layer, output_shape)

    def forward(self, input):
        if cfg.QUANTIZATION:
            weight = quantize(self.weight, bits=cfg.QUANT_BITS, clamp_outlier=False)
            output = InnerProduct.forward(WeightContext(weight, self.bias), input)
        else:
            output = InnerProduct.forward(self, input)
        return self.post_forward(output)

    def __repr__(self):
        return 'Q' + InnerProduct.__repr__(self)


class QPooling(Pooling, QuantizationMixin):
    def __init__(self, layer, input_shape):
        Pooling.__init__(self, layer, input_shape)
        QuantizationMixin.__init__(self, layer, input_shape)

    def forward(self, input):
        output = Pooling.forward(self, input)
        return self.post_forward(output)

    def __repr__(self):
        return 'Q' + Pooling.__repr__(self)


class QReLU(ReLU, QuantizationMixin):
    def __init__(self, layer, input_shape):
        ReLU.__init__(self, layer, input_shape)
        QuantizationMixin.__init__(self, layer, input_shape)

    def forward(self, input):
        output = ReLU.forward(self, input)
        return self.post_forward(output)

    def __repr__(self):
        return 'Q' + ReLU.__repr__(self)
