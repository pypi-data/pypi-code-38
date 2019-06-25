from __future__ import division, print_function

from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict

from ptcaffe.utils.config import cfg
from ptcaffe.nn import CtcLossPytorch, CtcLossWarpctc

__all__ = ['SoftmaxWithLoss', 'CtcLoss', 'MimicLoss', 'EuclideanLoss']


class SoftmaxWithLoss(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(SoftmaxWithLoss, self).__init__()
        loss_param = layer.get('loss_param', OrderedDict())
        self.ignore_label = None
        if 'ignore_label' in loss_param:
            self.ignore_label = int(loss_param['ignore_label'])
        self.normalize = (loss_param.get('normalize', 'true') == 'true')
        softmax_param = layer.get('softmax_param', OrderedDict())
        self.axis = int(softmax_param.get('axis', 1))
        assert(self.axis > 0)

    def __repr__(self):
        if self.ignore_label is not None:
            return 'SoftmaxWithLoss(ignore_label=%d)' % self.ignore_label
        else:
            return 'SoftmaxWithLoss()'

    def forward_shape(self, *input_shapes):
        return [1]

    def forward(self, input, targets):
        assert input.dim() == 2 or input.dim() == 4
        if input.dim() == 4:
            if self.axis == input.dim() - 1:
                input = input.view(-1, input.size(self.axis))
            else:
                lsize = 1
                for i in range(self.axis):
                    lsize *= input.size(i)
                rsize = 1
                for i in range((self.axis + 1), input.dim()):
                    rsize *= input.size(i)
                cls = input.size(self.axis)
                assert(lsize * cls * rsize == input.numel())
                input = input.view(lsize, cls, rsize).permute(0, 2, 1).contiguous().view(-1, cls)
        targets = targets.long().view(-1)
        assert input.numel() % targets.numel() == 0
        if self.ignore_label is not None:
            return F.cross_entropy(input, targets, size_average=self.normalize, ignore_index=self.ignore_label).view(1)
        else:
            return F.cross_entropy(input, targets, size_average=self.normalize).view(1)


class CtcLoss(nn.Module):
    def __init__(self, layer, *input_shape):
        super(CtcLoss, self).__init__()
        param = layer['ctc_param']
        self.ctc_type = param.get( 'ctc_type', None )
        if self.ctc_type is None:
            if torch.__version__.split('.')[0] == '0':
                self.ctc_type = "warpctc"
            else: self.ctc_type = "pytorch"
        if self.ctc_type == "warpctc":
            self.size_average = param['size_average'] == "true"
            self.length_average = param['length_average'] == "true"
        self.pad_val = int(param.get('pad_val', -1))
        self.blank = int(param.get('blank',0))

        #---post_init---
        if self.ctc_type == 'warpctc':
            self.loss_fn = CtcLossWarpctc(
                    self.blank, self.size_average,
                    self.length_average)
        elif self.ctc_type == 'pytorch':
            self.loss_fn =  CtcLossPytorch(
                    self.blank)
        self.unpacker = self.Unpacker(self.pad_val)

    def forward(self, pre, gt, path=None):
        """
        input :
            pre: torch.LongTensor in N x MaxLength_of_pre
            gt : torch.LongTensor in N x MaxLength_of_gt
            path: used for debug; dropped nowadays
        """
        gt = self.unpacker(gt)
        loss = self.loss_fn(pre, gt)
        return loss

    def forward_shape(self, *input_shape):
        return [1]

    class Unpacker(object):# unpack padded test tensor to test
        def __init__(self, pad_val=-1):
            self.pad_val = pad_val

        @staticmethod
        def reduce_split(t, splits,  dim=0):
            return list(map(lambda x:x.squeeze(dim) ,
                t.split(splits,dim)))

        def unpack_tensor(self, tensor):
            "LongTensor -> List[LongTensor]"
            tensor = self.reduce_split(tensor, 1, dim=0 )
            tensor = [self.short_tensor(t) for t in tensor]
            return tensor

        def short_tensor(self, tensor):
            for i in range(tensor.size(0)):
                if tensor[i] == self.pad_val:
                    return tensor[:i]
            return tensor

        def __call__(self, tensor):
            """
            input : torch.LongTensor in N x MaxLength
            return: List[ torch.LongTensor ]
            """
            tensor = self.unpack_tensor(tensor)
            return tensor


class MimicLoss(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(MimicLoss, self).__init__()
        self.loss_weight = float(layer.get('loss_weight', 1.0))
        mimic_param = layer.get('mimic_param', OrderedDict())
        self.T = float(mimic_param.get('temperature', 1))
        self.axis = int(mimic_param.get('axis', -1))

    def __repr__(self):
        return 'MimicLoss(T=%f)' % self.T

    def forward_shape(self, *input_shapes):
        return [1, ]

    def forward(self, input, probs):
        assert(input.numel() == probs.numel())
        target = probs.detach()
        return F.kl_div(F.log_softmax(input / self.T, dim=self.axis), F.softmax(target / self.T, dim=self.axis)).view(1) * self.T * self.T

class EuclideanLoss(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(EuclideanLoss, self).__init__()
        loss_param = layer.get('loss_param', OrderedDict())
        self.normalization = loss_param.get('normalization', 'BATCH_SIZE')

    def forward(self, input, targets):
        if self.normalization == 'FULL':
            return F.mse_loss(input, targets, size_average = True).view(1) * .5
        elif self.normalization == 'BATCH_SIZE':
            batch_size = input.shape[0]
            return F.mse_loss(input, targets, size_average = False).view(1)/batch_size * .5
        elif self.normalization == 'NONE':
            return F.mse_loss(input, targets, size_average = False).view(1) * .5

    def forward_shape(self, *input_shapes):
        return [1,]
