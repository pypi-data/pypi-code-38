from __future__ import division, print_function

import os
import torch
import torchvision
from collections import OrderedDict
from ptcaffe.transforms import create_transform
from ptcaffe.utils.utils import parse_types
from ptcaffe.utils.logger import logger
from ptcaffe.utils.config import cfg

from .base_data_layer import BaseData

__all__ = ['FolderData']

class FolderData(BaseData):
    def __init__(self, layer):
        super(FolderData, self).__init__(layer)

    def create_data_loader(self, layer):
        phase = layer['include']['phase']

        transform_param = layer.get('transform_param', OrderedDict())
        data_param = layer.get('data_param', OrderedDict())

        data_dir = data_param.pop('data_dir')
        logger.info('data_dir: %s' % data_dir)
        dataset = create_dataset(data_dir, transform_param)

        kwargs = parse_types(data_param) 
        if 'base_batch_size' in kwargs:
            base_batch_size = kwargs.pop('base_batch_size')
            
            if cfg.NUM_GPUS is not None:
                kwargs['batch_size'] = base_batch_size * cfg.NUM_GPUS
            else:
                kwargs['batch_size'] = base_batch_size
        data_loader = create_dataloader(dataset, phase, **kwargs)
        return data_loader


def create_dataset(data_dir, transform_param):
    transform = create_transform(transform_param)
    dataset = torchvision.datasets.ImageFolder(data_dir, transform=transform)
    return dataset

def create_dataloader(dataset, phase, batch_size, num_workers=0, pin_memory=True):
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=(phase == 'TRAIN'), num_workers=num_workers, pin_memory=pin_memory)
    return data_loader
