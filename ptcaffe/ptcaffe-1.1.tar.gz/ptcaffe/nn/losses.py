from __future__ import division, print_function

import six
import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.nn.functional import log_softmax

__all__ = ["FocalLoss" , "CtcLossPytorch", "CtcLossWarpctc"]
# size_average_type
#     0 : no average
#     1 : full average
#     2 : weighted average
class FocalLoss(nn.Module):
    """
    size_average_type
      0 : no average
      1 : full average
      2 : weighted average
    """
    def __init__(self, gamma=0, alpha=None, size_average_type=0):
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.alpha = alpha
        if isinstance(alpha, (float,) + six.integer_types):
            self.alpha = torch.Tensor([alpha, 1 - alpha])
        if isinstance(alpha, list):
            self.alpha = torch.Tensor(alpha)
        if size_average_type not in {0, 1, 2}:
            raise ValueError('Unknown size_average_type {}'.format(size_average_type))
        self.size_average_type = size_average_type
        self.eps = 1e-6

    def forward_shape(self, input_shape1, input_shape2):
        return [1]

    def forward(self, input, target):
        if input.dim() > 2:
            input = input.view(input.size(0), input.size(1), -1)  # N,C,H,W => N,C,H*W
            input = input.transpose(1, 2)    # N,C,H*W => N,H*W,C
            input = input.contiguous().view(-1, input.size(2))   # N,H*W,C => N*H*W,C
        target = target.view(-1, 1)

        logpt = log_softmax(input, dim=1)
        logpt = logpt.gather(1, target)
        logpt = logpt.view(-1)
        pt = logpt.data.exp()

        if self.alpha is not None:
            if self.alpha.type() != input.data.type():
                self.alpha = self.alpha.type_as(input.data)
            at = self.alpha.gather(0, target.data.view(-1))
            logpt = logpt * at

        focus = (1 - pt)**self.gamma
        loss = -1 * focus * logpt
        if self.size_average_type == 0:
            return loss.sum()
        if self.size_average_type == 1:
            return loss.mean()
        elif self.size_average_type == 2:
            return loss.sum() / (focus.sum() + self.eps)

class CtcLossPytorch():
    " pytorch 1.0 is needed"
    def __init__(self, blank=9054):
        self.blank = blank

    def encode(self, gts, device):
        "List[LongTensor], torch.device -> LongTensor, List[int]"
        lengths = [gt.size(0) for gt in gts]
        gts = torch.cat(gts).to(device)
        return gts, lengths

    def __call__(self, pre, gt):
        pre = F.log_softmax(pre, dim=-1)
        gt, ta_length = self.encode(gt, pre.device)
        in_length = [pre.size(0)]*pre.size(1)
        return F.ctc_loss(pre, gt, in_length, ta_length, blank=self.blank)

class CtcLossWarpctc():
    " warp_ctc is needed"
    def __init__(self, blank=9054, size_average=True, length_average=True):
        self.blank = blank
        self.size_average = size_average
        self.length_average = length_average

        #---post_init---
        from warpctc_pytorch import CTCLoss
        self.loss_fn = CTCLoss(blank=self.blank, size_average=self.size_average,
                length_average=self.length_average)

    def encode(self, gts, device):
        "List[LongTensor], torch.device -> LongTensor, List[int]"
        lengths = [gt.size(0) for gt in gts]
        gts = torch.cat(gts).to(device)
        return gts, lengths

    def __call__(self, pre, gt):
        """
        input:
            pre: LongTensor in shape N x MaxLength_of_pre
            gt : List[ LongTensor ] in 1 dim
        return: FloatTensor
        """
        gt, ta_length = self.encode(gt, pre.device)
        in_length = [pre.size(0)]*pre.size(1)
        #convert to type fit into warpctc
        gt = gt.int().cpu()
        ta_length = torch.IntTensor(ta_length).cpu()
        in_length = torch.IntTensor(in_length).cpu()
        loss = self.loss_fn(pre, gt, in_length, ta_length)
        loss = loss.to(pre.device)
        return loss


