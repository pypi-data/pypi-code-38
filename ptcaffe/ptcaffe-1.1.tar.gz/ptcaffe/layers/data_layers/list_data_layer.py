from __future__ import division, print_function

import random
import torch
from torch.utils.data import Dataset
from collections import OrderedDict
from ptcaffe.transforms import create_transform
from ptcaffe.utils.utils import parse_types

from .base_data_layer import BaseData

__all__ = ['ListData']

class ListData(BaseData):
    def __init__(self, layer):
        super(ListData, self).__init__(layer)

    def create_data_loader(self, layer):
        phase = layer['include']['phase']

        transform_param = layer.get('transform_param', OrderedDict())
        data_param = layer.get('data_param', OrderedDict())

        source = data_param.pop('source')
        dataset = create_dataset(source, phase, transform_param)

        kwargs = parse_types(data_param) 

        data_loader = create_dataloader(dataset, phase, **kwargs)
        return data_loader


def create_dataset(source, phase, transform_param):
    transform = create_transform(transform_param)
    list_dataset = ListDataset(source, phase, transform=transform)
    return list_dataset

def create_dataloader(dataset, phase, batch_size, num_workers=0, pin_memory=True):
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=(phase == 'TRAIN'), num_workers=num_workers, pin_memory=pin_memory)
    return data_loader

class ListDataset(Dataset):
    def __init__(self, source, phase, transform=None):
        with open(source, 'r') as file:
            self.lines = file.readlines()

        if phase=='TRAIN':
            random.shuffle(self.lines)

        self.nSamples = len(self.lines)
        self.transform = transform

    def __len__(self):
        return self.nSamples

    def __getitem__(self, index):
        assert index <= len(self), 'index range error'
        line = self.lines[index]
        return self.transform(line)
