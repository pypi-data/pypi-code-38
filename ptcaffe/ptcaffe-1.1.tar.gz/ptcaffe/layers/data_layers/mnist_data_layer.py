from __future__ import division, print_function

from collections import OrderedDict

import numpy as np
import torch
import torch.nn as nn

__all__ = ['MnistData']

# ----------- MnistData -----------
# layer {
#  name: "mnist"
#  type: "MnistData"
#  top: "data"
#  top: "label"
#  include {
#    phase: TRAIN
#    selector: MNIST
#  }
#  data_param {
#    prefix: "./data/mnist/train" #including ./data/mnist/train-images-idx3-ubyte.gz and
#                                 # ./data/mnist/train-labels-idx1-ubyte.gz
#    batch_size: 64
#  }
# }

# Load data from original mnist(or fashion mnist) .gz file


class MnistData(nn.Module):
    def __init__(self, layer):
        super(MnistData, self).__init__()
        self.phase = layer['include']['phase']
        data_param = layer.get('data_param', OrderedDict())
        self.prefix = data_param['prefix']  # such as 'data/mnist/t10k'
        self.batch_size = int(data_param['batch_size'])
        self.orig_images, self.orig_labels = self.load_mnist(self.prefix)
        self.num_imgs = self.orig_images.shape[0]
        if self.phase == 'TRAIN':
            rand_ids = np.random.permutation(self.num_imgs)
            self.images = self.orig_images[rand_ids, :]
            self.labels = self.orig_labels[rand_ids]
        else:
            self.images = self.orig_images
            self.labels = self.orig_labels
        self.batch_num = int(self.num_imgs / self.batch_size)
        self.cur_batch = 0
        self.device = -1

    def __repr__(self):
        return 'MnistData(prefix=%s)' % self.prefix

    def set_device(self, device):
        self.device = device

    def load_mnist(self, prefix):
        """Load MNIST data from `path`"""
        labels_path = '%s-labels-idx1-ubyte.gz' % prefix
        images_path = '%s-images-idx3-ubyte.gz' % prefix

        import gzip
        with gzip.open(labels_path, 'rb') as lbpath:
            labels = np.frombuffer(lbpath.read(), dtype=np.uint8,
                                   offset=8)

        with gzip.open(images_path, 'rb') as imgpath:
            images = np.frombuffer(imgpath.read(), dtype=np.uint8,
                                   offset=16).reshape(len(labels), 784)

        return images, labels

    def forward(self):
        if self.cur_batch == self.batch_num:
            if self.phase == 'TRAIN':
                rand_ids = np.random.permutation(self.num_imgs)
                self.images = self.orig_images[rand_ids, :]
                self.labels = self.orig_labels[rand_ids]
            self.cur_batch = 0
        start_idx = self.cur_batch * self.batch_size
        end_idx = start_idx + self.batch_size
        batch_images = self.images[start_idx:end_idx, :]
        batch_labels = self.labels[start_idx:end_idx]
        if self.device == -1:
            batch_images = torch.from_numpy(batch_images).view(-1, 1, 28, 28).float() / 255.0
            batch_labels = torch.from_numpy(batch_labels).view(-1)
        else:
            batch_images = torch.from_numpy(batch_images).view(-1, 1, 28, 28).float().cuda(self.device) / 255.0
            batch_labels = torch.from_numpy(batch_labels).view(-1).cuda(self.device)
        self.cur_batch += 1

        return batch_images, batch_labels

    def forward_shape(self):
        return [self.batch_num, 1, 28, 28], [self.batch_num]
