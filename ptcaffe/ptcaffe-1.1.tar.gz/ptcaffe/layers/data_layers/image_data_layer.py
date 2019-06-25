from __future__ import division, print_function

import random
from collections import OrderedDict

import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset

from ptcaffe.utils.logger import logger

__all__ = ['ImageData']


class ImageData(nn.Module):
    def __init__(self, layer):
        super(ImageData, self).__init__()
        image_data_param = layer.get('image_data_param', OrderedDict())
        source = image_data_param.get('source', 'train.txt')
        self.batch_size = int(image_data_param.get('batch_size', 64))
        scale = float(image_data_param.get('scale', 1.0))
        new_height = int(image_data_param.get('new_height', 256))
        new_width = int(image_data_param.get('new_width', 256))
        root_folder = image_data_param.get('root_folder', '')

        is_color = (image_data_param.get('is_color', 'true') == 'true')
        num_workers = int(image_data_param.get('num_workers', 4))
        assert('rand_skip' not in image_data_param)
        assert('mean_file' not in image_data_param)

        include_param = layer.get('include', OrderedDict())
        phase = include_param.get('phase', 'TRAIN')

        transform_param = layer.get('transform_param', OrderedDict())
        data_transformer = DataTransformer(transform_param, phase)

        kwargs = {'num_workers': num_workers, 'pin_memory': True}
        self.data_loader = torch.utils.data.DataLoader(
            ImageListDataset(source, root_folder, is_color, new_width, new_height, shuffle=(phase == 'TRAIN'), transform=data_transformer),
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
        mean_value = transform_param.get('mean_value', '')
        if mean_value == '':
            mean_value = [0.0, 0.0, 0.0]
        else:
            mean_value = mean_value.lstrip('[').rstrip(']')
            mean_value = [float(m.strip()) for m in mean_value.split(',')]
        self.mean_value = mean_value
        self.phase = phase

    def __call__(self, img):
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


class ImageListDataset(Dataset):
    def __init__(self, source, root_folder, is_color, new_width, new_height, shuffle=True,
                 transform=None, target_transform=None):
        with open(source, 'r') as file:
            self.lines = file.readlines()

        if shuffle:
            random.shuffle(self.lines)

        self.nSamples = len(self.lines)
        self.transform = transform
        self.target_transform = target_transform
        self.root_folder = root_folder
        self.is_color = is_color
        self.new_width = new_width
        self.new_height = new_height

    def __len__(self):
        return self.nSamples

    def __getitem__(self, index):
        assert index <= len(self), 'index range error'
        imgpath, label = self.lines[index].split()
        imgpath = self.root_folder + imgpath
        if self.is_color:
            img = cv2.imread(imgpath)
        else:
            img = cv2.imread(imgpath, 0)
        img = cv2.resize(img, (self.new_width, self.new_height))

        if self.transform is not None:
            img = self.transform(img)
        img = torch.from_numpy(img.transpose(2, 0, 1)).float()

        label = int(label)

        if self.target_transform is not None:
            label = self.target_transform(label)

        return img, label
