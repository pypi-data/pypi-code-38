from __future__ import division, print_function

import torch
import torch.nn as nn
from torch.utils.data import Dataset
import random
from collections import OrderedDict
from ptcaffe.utils.logger import logger
from ptcaffe.utils.utils import make_list

__all__ = ['CaffeLmdbData']

class CaffeLmdbData(nn.Module):
    def __init__(self, layer):
        super(CaffeLmdbData, self).__init__()
        data_param = layer.get('data_param', OrderedDict())
        source = data_param['source']
        self.batch_size = int(data_param['batch_size'])
        num_workers = int(data_param.get('num_workers', 0))
        assert num_workers <= 1, "lmdb works with only one worker"
        include_param = layer.get('include', OrderedDict())
        phase = include_param.get('phase', 'TRAIN')
        transform_param = layer.get('transform_param', OrderedDict())
        data_transformer = DataTransformer(transform_param, phase)
        kwargs = {'num_workers': num_workers, 'pin_memory': True}
        self.data_loader = torch.utils.data.DataLoader(
            CaffeLmdbDataset(source=source, transform=data_transformer),
            batch_size=self.batch_size, shuffle=(phase == 'TRAIN'), **kwargs)

        self.batch_iter = iter(self.data_loader)
        self.batch_idx = 0
        self.batch_num = len(self.data_loader)
        logger.info('batch_num = %d' % self.batch_num)

        self.phase = phase

    def __repr__(self):
        return 'ImageData(batch_size=%d)' % self.batch_size

    def forward(self):
        if self.batch_idx % self.batch_num == 0 and self.batch_idx != 0:
            self.batch_iter = iter(self.data_loader)
        self.batch_idx += 1

        data, target = next(self.batch_iter)
        data, target = data.cuda(), target.cuda()
        return data, target

    def forward_shape(self):
        data, target = self.forward()
        if self.phase == 'TEST':
            self.batch_idx = 0
            self.batch_iter = iter(self.data_loader)
        return list(data.size()), list(target.size())

class DataTransformer:
    def __init__(self, transform_param, phase):
        self.transform_param = transform_param
        self.scale = float(transform_param.get('scale', 1.0))
        self.mirror = (transform_param.get('mirror', 'false') == 'true')
        self.crop_size = int(transform_param.get('crop_size', -1))
        mean_value = transform_param.get('mean_value', None)
        if mean_value is None:
            mean_value = [0.0, 0.0, 0.0]
        else:
            mean_value = make_list(mean_value)
            mean_value = [float(value) for value in mean_value]
        self.mean_value = mean_value
        self.phase = phase

    def __call__(self, img):
        import cv2
        import numpy as np

        if self.phase == 'TRAIN' and self.mirror and random.random() > 0.5:
            img = cv2.flip(img, 1)
        if self.crop_size != -1:
            assert(self.crop_size <= img.shape[0] and self.crop_size <= img.shape[1])
            if self.phase == 'TRAIN':
                offx = random.randint(0, img.shape[1] - self.crop_size)
                offy = random.randint(0, img.shape[0] - self.crop_size)
            else:
                offx = int((img.shape[1] - self.crop_size) / 2.0)
                offy = int((img.shape[0] - self.crop_size) / 2.0)
            img = img[offy:offy + self.crop_size, offx:offx + self.crop_size]
        img = img.astype(np.float32)
        for i in range(img.shape[2]):
            img[:, :, i] -= self.mean_value[i]
        img *= self.scale
        return img

class CaffeLmdbDataset(Dataset):
    def __init__(self, source, transform=None, target_transform=None):
        import lmdb

        self.env = lmdb.open(source, readonly=True)
        self.txn = self.env.begin()
        self.cursor = self.txn.cursor()
        self.nSamples = self.txn.stat()['entries']
        self.transform = transform
        self.target_transform = target_transform
        assert(self.cursor.next())
        
    def __len__(self):
        return self.nSamples

    def __getitem__(self, index):
        import numpy as np
        import cv2
        from ptcaffe.proto import caffe_pb2
        assert index <= len(self), 'index range error'

        if False:
            raw_datum = self.txn.get(b'%08d' % index)
        else: #if raw_datum is None:
            raw_datum = self.cursor.value()
            if not self.cursor.next():
                self.cursor = self.txn.cursor()
                assert(self.cursor.next())

        datum = caffe_pb2.Datum()
        datum.ParseFromString(raw_datum)

        img = np.fromstring(datum.data, dtype=np.uint8)
        img = img.reshape(datum.height, datum.width, datum.channels)
        label = datum.label

        if self.transform is not None:
            img = self.transform(img)
        img = torch.from_numpy(img.transpose(2, 0, 1)).float()

        label = int(label)
        if self.target_transform is not None:
            label = self.target_transform(label)
        
        return img, label
