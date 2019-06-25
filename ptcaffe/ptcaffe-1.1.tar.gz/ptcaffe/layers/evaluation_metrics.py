# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

from __future__ import division, print_function


class BaseMetric(object):
    def __init__(self):
        pass

    def reset(self):
        pass

    def get(self):
        pass

    def update(self):
        pass


class AccuracyMetric(object):
    def __init__(self, top_k=1, ignore_label=None):
        self.top_k = top_k
        self.ignore_label = ignore_label
        self.sum_accuracy = 0.0
        self.count = 0

    def reset(self):
        self.sum_accuracy = 0.0
        self.count = 0

    def get(self):
        if self.count == 0:
            return None
        else:
            return self.sum_accuracy / self.count

    def update(self, output, label):
        if self.top_k == 1:
            if self.ignore_label is None:
                max_vals, max_ids = output.data.max(1)
                if label.dim() > 1 and label.numel() == output.size(0):
                    label = label.view(-1)
                n_correct = (max_ids.view(-1).long() == label.data.long()).sum()
                batchsize = output.data.size(0)
                accuracy = float(n_correct) / batchsize
            else:
                max_vals, max_ids = output.data.max(1)
                non_ignore_mask = (label.data.long() != self.ignore_label)
                n_correct = ((max_ids.view(-1).long() == label.data.long()) & non_ignore_mask).sum()
                non_ignore_num = float(non_ignore_mask.sum())
                accuracy = float(n_correct) / (non_ignore_num + 1e-6)
        else:
            assert(self.top_k == 5)
            max_vals, max_ids = output.data.topk(self.top_k, 1)
            label_size = label.numel()
            label_ext = label.data.long().view(label_size, 1).expand(label_size, self.top_k)
            compare = (max_ids.view(-1, self.top_k) == label_ext)
            n_correct = compare.sum()
            batchsize = output.data.size(0)
            accuracy = float(n_correct) / batchsize
        self.sum_accuracy += accuracy
        self.count += 1
