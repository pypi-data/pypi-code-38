from __future__ import division, print_function

import math

import torch
import torch.nn as nn
import torch.utils.data

from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.utils.utils import get_visdom

__all__ = ['TorchVisionData']


class TorchVisionData(nn.Module):
    def __init__(self, layer):
        from torchvision import datasets, transforms
        super(TorchVisionData, self).__init__()
        self.device = -1
        root = './data'
        if 'root' in layer['torchvision_data_param']:
            root = layer['torchvision_data_param']['root']
        phase = 'TRAIN'
        if 'include' in layer and 'phase' in layer['include']:
            phase = layer['include']['phase']
        data_name = layer['torchvision_data_param']['data_name']
        self.batch_size = int(layer['torchvision_data_param']['batch_size'])
        num_workders = int(layer['torchvision_data_param'].get('num_workers', 2))
        mean = float(layer['transform_param']['mean'])
        std = float(layer['transform_param']['std'])
        kwargs = {'num_workers': num_workders, 'pin_memory': True}
        if data_name == 'MNIST':
            self.data_loader = torch.utils.data.DataLoader(
                datasets.MNIST(root, train=(phase == 'TRAIN'),
                               download=(phase == 'TRAIN'),
                               transform=transforms.Compose([
                                   transforms.ToTensor(),
                                   transforms.Normalize((mean,), (std,))
                               ])),
                batch_size=self.batch_size, shuffle=(phase == 'TRAIN'), **kwargs)
        else:
            logger.error('Unknown data name')
            exit(0)
        self.batch_iter = iter(self.data_loader)
        self.batch_idx = 0
        self.batch_num = len(self.data_loader)
        logger.info('batch_num = %d' % self.batch_num)

        self.phase = phase

        # visdom params
        from easydict import EasyDict as edict
        self.visdom = edict()
        if 'visdom_param' in layer:
            visdom_param = layer['visdom_param']
            assert('server' in visdom_param)
            self.visdom.viz = get_visdom(visdom_param, cfg)
            self.visdom.interval = int(visdom_param.get('interval', 8))
            lname = layer['top'][0] + '@' + phase
            self.visdom.title = visdom_param.get('title', lname)
            self.visdom.mean_value = mean
            self.visdom.std_value = std
            self.visdom.win = None
        else:
            self.visdom = None

    def __repr__(self):
        return 'TorchVisionData()'

    def set_device(self, device):
        self.device = device

    def forward(self):
        if self.batch_idx % self.batch_num == 0 and self.batch_idx != 0:
            self.batch_iter = iter(self.data_loader)
        self.batch_idx += 1

        data, target = next(self.batch_iter)

        if self.visdom and self.batch_idx % self.visdom.interval == 0:
            image = data * self.visdom.std_value + self.visdom.mean_value
            image = image * 255.0
            nrow = int(math.ceil(math.sqrt(image.size(0))))
            caption = "batch%d" % self.batch_idx
            if self.batch_idx == self.visdom.interval:
                self.visdom.win = self.visdom.viz.images(image.numpy(), nrow=nrow, opts={'title': self.visdom.title, 'caption': self.visdom.title})
            else:
                assert(self.visdom.win is not None)
                self.visdom.viz.images(image.numpy(), nrow=nrow, opts={'title': self.visdom.title, 'caption': caption}, win=self.visdom.win)

        if self.device != -1:
            data, target = data.cuda(self.device), target.cuda(self.device)
        return data, target

    def forward_shape(self):
        # return [1, 1, 28, 28], [1]
        data, target = self.forward()
        if self.phase == 'TEST':
            self.batch_idx = 0
            self.batch_iter = iter(self.data_loader)
        return list(data.size()), list(target.size())
