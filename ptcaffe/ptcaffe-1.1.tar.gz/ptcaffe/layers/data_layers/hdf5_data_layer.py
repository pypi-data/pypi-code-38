import os
import torch
import torch.nn as nn
from collections import OrderedDict
from torch.utils.data import Dataset
import cv2
from PIL import Image
import random
import numpy as np
import copy
from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
import threading
import abc

class DataTransformer:
    def __init__(self, transform_param, phase):
        self.transform_param = transform_param
        self.scale = float(transform_param.get('scale', 1.0))
        self.mirror = (transform_param.get('mirror', 'false') == 'true')
        self.crop_size = int(transform_param.get('crop_size', -1))
        mean_value = transform_param.get('mean_value', None)
        if mean_value is not None:
            mean_value = mean_value.lstrip('[').rstrip(']')
            mean_value = [float(m.strip()) for m in mean_value.split(',')]
        self.mean_value = mean_value
        self.phase = phase

    def __call__(self, img, target):
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
        if self.mean_value:
            for i in range(img.shape[2]):
                img[:, :, i] -= self.mean_value[i]
        img *= self.scale
        return img, target

def is_h5_file(filename):
    H5_EXTENSIONS = ['.h5']
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in H5_EXTENSIONS)

def make_dataset(dir):
    images = []
    dir = os.path.expanduser(dir)
    for root, _, fnames in sorted(os.walk(dir)):
        for fname in sorted(fnames):
            if is_h5_file(fname):
                path = os.path.join(root, fname)
                images.append(path)
    return images

class Hdf5Dataset(Dataset):
    def __init__(self, root, pkgSize, new_width, new_height, is_color = True, transform=None, target_transform=None):
        self.root = root
        self.pkgList = make_dataset(root)
        self.pkgList = sorted(self.pkgList, key=lambda x:int(x.split('-')[-1].split('.')[0]))
        self.transform = transform
        self.target_transform = target_transform
        self.currentPkgIndex = -1
        self.pkgSize = pkgSize
        self.length = len(self.pkgList) * pkgSize
        self.pkgHandle = None
        self.new_width = new_width
        self.new_height = new_height
        self.is_color = is_color

    def openPkg(self, pkgIndex):
        import h5py
        pkgPath = self.pkgList[pkgIndex]
        self.pkgHandle = h5py.File(pkgPath, 'r')

    def __len__(self):
        return self.length
        
    def __getitem__(self, index):
        pkgIndex = int(index / self.pkgSize)
        imageIndex = int(index % self.pkgSize)
        
        if pkgIndex != self.currentPkgIndex:
            self.openPkg(pkgIndex)
            self.currentPkgIndex = pkgIndex
        
        assert (self.pkgHandle != None)
        featureKey = "img/" + str(imageIndex)
        labelKey = "label/" + str(imageIndex)
        img = self.pkgHandle[featureKey].value
        img = np.fromstring(img, np.uint8)
        img = cv2.imdecode(img, -1)
        target = self.pkgHandle[labelKey].value

        img = cv2.resize(img, (self.new_width, self.new_height))
       
        if self.target_transform is not None:
            target = self.target_transform(target)
        
        if self.transform is not None:
            img, target = self.transform(img, target)
        
        if self.is_color:
            img = torch.from_numpy(img.transpose(2,0,1)).float()
        else:
            img = torch.from_numpy(img).unsqueeze(0).float()
        
        return (img, target)

# -------------------------------------------------------
# Define similar to ImageData
# -------------------------------------------------------
class Hdf5BaseData(nn.Module):
    def __init__(self, layer):
        super(Hdf5BaseData, self).__init__()
        self.device = -1
        hdf5_data_param = layer.get('hdf5_data_param', OrderedDict())
        self.batch_size = int(hdf5_data_param.get('batch_size', 64))
        include_param = layer.get('include', OrderedDict())
        self.phase = include_param.get('phase', 'TRAIN')

        self.data_loader = self.create_data_loader(layer)
        self.batch_iter = iter(self.data_loader)
        self.batch_idx = 0
        self.batch_num = self.get_batch_num()
        logger.info('batch_num = %d' % self.batch_num)

        self.saved_inputs = None

    def __repr__(self):
        return 'Hdf5BaseData(batch_size=%d)' % self.batch_size

    def get_batch_num(self):
        return len(self.data_loader)

    def set_device(self, device):
        self.device = device
 
    @abc.abstractmethod
    def create_data_loader(self, layer):
        hdf5_data_param = layer.get('hdf5_data_param', OrderedDict())
        source = hdf5_data_param.get('source', 'data/')
        pkg_size = int(hdf5_data_param.get('pkg_size', 1280))
        new_height = int(hdf5_data_param.get('new_height', 256))
        new_width = int(hdf5_data_param.get('new_width', 256))
        is_color = (hdf5_data_param.get('is_color', 'true') == 'true')

        num_workers = int(hdf5_data_param.get('num_workers', 4))
        assert('rand_skip' not in hdf5_data_param)
        assert('mean_file' not in hdf5_data_param)

        include_param = layer.get('include', OrderedDict())
        phase = include_param.get('phase', 'TRAIN')
        transform_param = layer.get('transform_param', OrderedDict())
        data_transformer = DataTransformer(transform_param, phase)

        kwargs = {'num_workers': num_workers, 'pin_memory': True}
        data_loader = torch.utils.data.DataLoader(
            Hdf5Dataset(source, pkg_size, new_width, new_height, is_color=is_color, transform=data_transformer, target_transform=self.target_transformer),
            batch_size=self.batch_size, shuffle=(phase == 'TRAIN'), **kwargs)
        return data_loader
   
    def target_transformer(self, label):
        return label

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

