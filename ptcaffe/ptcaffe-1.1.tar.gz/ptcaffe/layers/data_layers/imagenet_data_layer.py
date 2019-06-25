from __future__ import division, print_function

import io
import os
from collections import OrderedDict

import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import Dataset

from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.transforms import TFResizer, Lighting

__all__ = ['ImageNetData']


class ImageNetData(nn.Module):
    def __init__(self, layer):
        import torchvision.transforms as transforms  # to avoid conflict with gluon
        import torchvision.datasets as datasets
        super(ImageNetData, self).__init__()
        include_param = layer.get('include', OrderedDict())
        phase = include_param.get('phase', 'TRAIN')

        data_param = layer.get('data_param', OrderedDict())
        data_type = data_param.get('data_type', 'folder')
        data_dir = data_param['data_dir']
        logger.info('data_dir: %s' % data_dir)
        if 'batch_size' in data_param:
            self.batch_size = int(data_param['batch_size'])
        elif 'base_batch_size' in data_param:
            if cfg.NUM_GPUS is not None:
                self.batch_size = int(data_param['base_batch_size']) * cfg.NUM_GPUS
            else:
                self.batch_size = int(data_param['base_batch_size'])
        num_workers = int(data_param['num_workers'])
        model_name = data_param.get('model_name', 'unknown')
        self.input_size = int(data_param.get('input_size', 224))

        transform_param = layer.get('transform_param', OrderedDict())
        mean_values = transform_param.get('mean_value', [0.485,0.456,0.406])
        mean_values = [float(v) for v in mean_values]
        std_values = transform_param.get('std_value', [0.229,0.224,0.225])
        std_values = [float(v) for v in std_values]
       
        if 'jitter' in transform_param:
            jitter_param = float(transform_param['jitter'])
        else:
            jitter_param = 0.0 if model_name.startswith('mobilenet') else 0.4

        if 'lighting' in transform_param:
            lighting_param = float(transform_param['lighting'])
        else:
            lighting_param = 0.0 if model_name.startswith('mobilenet') else 0.1

        if 'min_scale' in transform_param:
            min_scale = float(transform_param['min_scale'])
        elif model_name.startswith('mobilenet'):
            min_scale = 0.2
        else:
            # see https://discuss.pytorch.org/t/is-transforms-randomresizedcrop-used-for-data-augmentation/16716
            min_scale = 0.08

        normalize = transforms.Normalize(mean_values, std_values)

        self.device = -1
        sub_dir = 'train' if phase == 'TRAIN' else 'val'
        if 'sub_dir' in data_param:
            sub_dir = data_param['sub_dir']

        if phase == 'TRAIN':
            transform = transforms.Compose([
                transforms.RandomResizedCrop(self.input_size, scale=(min_scale, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=jitter_param, contrast=jitter_param, saturation=jitter_param),
                transforms.ToTensor(),
                Lighting(lighting_param),
                normalize,
            ])
        else:
            transform = transforms.Compose([
                #TFResizer(int(self.input_size / 0.875)),
                transforms.Resize(int(self.input_size / 0.875)),  # 256
                transforms.CenterCrop(self.input_size),        # 224
                transforms.ToTensor(),
                normalize,
            ])

        kwargs = {'num_workers': num_workers, 'pin_memory': True}

        filedir = os.path.join(data_dir, sub_dir)
        if data_type == 'folder':
            self.data_loader = torch.utils.data.DataLoader(
                datasets.ImageFolder(filedir, transform=transform),
                batch_size=self.batch_size, shuffle=True, **kwargs)
        elif data_type == 'hdf5':
            self.data_loader = torch.utils.data.DataLoader(
                Hdf5Dataset(filedir, pkgSize=1280, transform=transform),
                batch_size=self.batch_size, shuffle=True, **kwargs)
        else:
            assert(False)

        self.batch_iter = iter(self.data_loader)
        self.batch_idx = 0
        self.batch_num = len(self.data_loader)
        logger.info('batch_num = %d' % self.batch_num)
        self.phase = phase

    def set_device(self, device):
        if device is None:
            self.device = 0
        else:
            self.device = device

    def forward(self):
        if self.batch_idx % self.batch_num == 0 and self.batch_idx != 0:
            self.batch_iter = iter(self.data_loader)
        self.batch_idx += 1

        data, label = next(self.batch_iter)
        if self.device == -1:
            return data, label
        else:
            return data.cuda(self.device), label.cuda(self.device, non_blocking=True)

    def forward_shape(self):
        return [self.batch_size, 3, self.input_size, self.input_size], [self.batch_size, ]


class Hdf5Dataset(Dataset):
    def __init__(self, root, pkgSize, transform=None):
        self.root = root
        self.pkgList = self.make_dataset(root)
        self.transform = transform
        self.currentPkgIndex = -1
        self.pkgSize = pkgSize
        self.length = len(self.pkgList) * pkgSize
        self.pkgHandle = None

    def is_h5_file(self, filename):
        H5_EXTENSIONS = ['.h5']
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in H5_EXTENSIONS)

    def make_dataset(self, dir):
        images = []
        dir = os.path.expanduser(dir)
        for root, _, fnames in sorted(os.walk(dir)):
            for fname in sorted(fnames):
                if self.is_h5_file(fname):
                    path = os.path.join(root, fname)
                    images.append(path)
        return images

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

        assert (self.pkgHandle is not None)
        img = self.pkgHandle["x/" + str(imageIndex)].value
        img = Image.open(io.BytesIO(img.tobytes()))
        img = img.convert('RGB')
        target = self.pkgHandle["y/" + str(imageIndex)].value

        if self.transform is not None:
            img = self.transform(img)

        return img, target
