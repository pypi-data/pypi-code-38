from __future__ import division, print_function

import abc

import torch.nn as nn

__all__ = ['BaseData']


class BaseData(nn.Module):
    def __init__(self, layer):
        super(BaseData, self).__init__()
        self.layer = layer
        self.device = -1
        self.phase = 'TEST'
        if 'include' in layer and 'phase' in layer['include']:
            self.phase = layer['include']['phase']
        self.data_loader = self.create_data_loader(layer)
        self.batch_iter = iter(self.data_loader)
        self.batch_idx = 0
        self.batch_num = self.get_batch_num()
        self.batch_size = self.get_batch_size()

        self.saved_inputs = None

    @abc.abstractmethod
    def create_data_loader(self, layer):
        pass

    def get_batch_num(self):
        return len(self.data_loader)

    def get_batch_size(self):
        return self.data_loader.batch_size

    def __repr__(self):
        return 'BaseData()'

    def set_device(self, device):
        if device is None:
            self.device = 0
        else:
            self.device = device

    def forward(self):
        if self.saved_inputs is not None:
            saved_inputs = self.saved_inputs
            if self.device != -1:
                saved_inputs = tuple([input.cuda(self.device) for input in saved_inputs])
            self.saved_inputs = None
            return saved_inputs

        if self.batch_idx % self.batch_num == 0 and self.batch_idx != 0:
            self.batch_iter = iter(self.data_loader)
        self.batch_idx += 1

        fetch_datas = next(self.batch_iter)

        if self.device != -1:
            outputs = [data.cuda(self.device) for data in fetch_datas]
        else:
            outputs = [data for data in fetch_datas]
        return tuple(outputs)

    def forward_shape(self):
        if self.saved_inputs is None:
            self.saved_inputs = self.forward()

        output_shapes = [list(data.size()) for data in self.saved_inputs]

        if len(output_shapes) == 1:
            return output_shapes[0]
        else:
            return output_shapes
