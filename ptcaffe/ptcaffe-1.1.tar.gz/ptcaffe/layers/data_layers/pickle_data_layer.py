from __future__ import division, print_function

from collections import OrderedDict

import torch
import torch.nn as nn

from ptcaffe.utils.utils import make_list

__all__ = ['PickleData', 'SavePickleData']

# ---------- PickleData ----------


class PickleData(nn.Module):
    def __init__(self, layer):
        super(PickleData, self).__init__()
        pickle_param = layer['pickle_param']
        self.data_prefix = pickle_param['data_prefix']
        self.start_idx = int(pickle_param.get('start_idx', 0))
        if 'end_idx' in pickle_param:
            self.end_idx = int(pickle_param['end_idx'])
        data_shapes = make_list(pickle_param['data_shape'])
        self.data_shapes = []
        for data_shape in data_shapes:
            data_shape = [int(dim.strip()) for dim in data_shape.split(',')]
            self.data_shapes.append(data_shape)
        self.device = -1
        self.batch_idx = 0
        self.tnames = make_list(layer['top'])

    def __repr__(self):
        return 'PickleData()'

    def set_device(self, device):
        self.device = device

    def forward_shape(self):
        if len(self.data_shapes) == 1:
            return self.data_shapes[0]
        else:
            return self.data_shapes

    def forward(self):
        import pickle
        idx = self.start_idx + self.batch_idx
        self.batch_idx += 1
        if self.end_idx is not None:
            self.batch_idx = self.batch_idx % (self.end_idx - self.start_idx)

        loadname = '%s%d.pkl' % (self.data_prefix, idx)
        with open(loadname) as fp:
            datas = pickle.load(fp)

        outputs = []
        if self.device == -1:
            outputs = [torch.from_numpy(datas[name]) for name in self.tnames]
        else:
            outputs = [torch.from_numpy(datas[name]).cuda(self.device) for name in self.tnames]
        return tuple(outputs)


class SavePickleData(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(SavePickleData, self).__init__()
        save_pickle_param = layer['save_pickle_param']
        self.data_prefix = save_pickle_param['data_prefix']
        self.batch_idx = 0
        self.bnames = make_list(layer['bottom'])

    def __repr__(self):
        return "SavePickleData()"

    def forward_shape(self, *input_shapes):
        return

    def forward(self, *inputs):
        import pickle
        savename = "%s%d.pkl" % (self.data_prefix, self.batch_idx)
        self.batch_idx += 1
        datas = OrderedDict()
        for name, input in zip(self.bnames, inputs):
            datas[name] = input.detach().cpu().numpy()

        with open(savename, 'wb') as fp:
            pickle.dump(datas, fp)
