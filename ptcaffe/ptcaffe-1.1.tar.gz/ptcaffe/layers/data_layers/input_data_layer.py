from __future__ import division, print_function

from collections import OrderedDict

import cv2
import torch
import torch.nn as nn
from PIL import Image

from ptcaffe.utils.logger import logger

__all__ = ['InputData']


class InputData(nn.Module):
    def __init__(self, layer):
        super(InputData, self).__init__()
        data_param = layer.get('data_param', OrderedDict())
        transform_param = layer.get('transform', OrderedDict())

        self.source = data_param.get('source', '0')
        self.capture = ImageSource(self.source)
        self.means = transform_param.get('mean', [])
        self.means = self.means if isinstance(self.means, list) else [self.means]
        if len(self.means) > 0:
            self.means = [float(m) for m in self.means]
        self.scale = float(transform_param.get('scale', 1.0))
        self.channel_type = transform_param.get('channel_type', 'RGB')
        self.resize_width = int(transform_param.get('resize_width', -1))
        self.resize_height = int(transform_param.get('resize_height', -1))

        self.device = -1

        self.saved_input = None

    def set_device(self, device):
        if device is None:
            self.device = 0
        else:
            self.device = device

    def __repr__(self):
        return 'InputData(source = %s)' % self.source

    def rgb2bgr(self, im):
        r, g, b = im.split(1, dim=1)
        return torch.cat((b, g, r), dim=1)

    def forward(self):
        if self.saved_input is not None:
            saved_input = self.saved_input
            if self.device != -1:
                saved_input = saved_input.cuda(self.device)
            self.saved_input = None
            return saved_input

        img = self.capture.next()
        if img is None:
            self.capture = ImageSource(self.source)
            img = self.capture.next()
        if self.capture.image_type == 'CV2':
            height, width, channels = img.shape
            if self.resize_width > 0 and self.resize_height > 0:
                img = cv2.resize(img, (self.resize_width, self.resize_height))
            elif self.resize_width > 0:
                self.resize_height = int((height * self.resize_width + 0.5 * width) / width)
                img = cv2.resize(img, (self.resize_width, self.resize_height))
            elif self.resize_height > 0:
                self.resize_width = int((width * self.resize_height + 0.5 * height) / height)
                img = cv2.resize(img, (self.resize_width, self.resize_height))

            if self.channel_type == 'RGB':
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = torch.from_numpy(img.transpose(2, 0, 1)).float().unsqueeze(0)
        elif self.capture.image_type == 'PIL':
            height, width = img.size()
            if self.resize_width > 0 and self.resize_height > 0:
                img = img.resize((self.resize_width, self.resize_height))
            elif self.resize_width > 0:
                self.resize_height = int((height * self.resize_width + 0.5 * width) / width)
                img = img.resize((self.resize_width, self.resize_height))
            elif self.resize_height > 0:
                self.resize_width = int((width * self.resize_height + 0.5 * height) / height)
                img = img.resize((self.resize_width, self.resize_height))

            height, width = img.size()
            img = torch.ByteTensor(torch.ByteStorage.from_buffer(img.tobytes()))
            img = img.view(height, width, 3).transpose(0, 1).transpose(0, 2).contiguous()
            img = img.view(1, 3, height, width)
            img = img.float()  # .div(255.0)
            if self.channel_type == 'BGR':  # default RGB
                img = self.rgb2bgr(img)

        for i in range(len(self.means)):
            img[0][i] = img[0][i] - self.means[i]
        img = img * self.scale
        if self.device == -1:
            return img
        else:
            return img.cuda(self.device)

    def forward_shape(self):
        if self.saved_input is None:
            self.saved_input = self.forward()

        return self.saved_input.shape


class ImageSource:
    def __init__(self, source):
        if source.find('.txt') >= 0 or source.find('.lst') >= 0 or source.find('.list') >= 0:
            self.source_type = 'filelist'
            with open(source) as fp:
                self.lines = fp.readlines()
            self.next_line_id = 0
        elif source.find('.mov') >= 0 or source.find('.avi') >= 0 or source.find('.mp4'):
            self.source_type = 'video'
            self.capture = cv2.VideoCapture(source)
        elif source.isdigit():
            self.source_type = 'camera'
            self.capture = cv2.VideoCapture(int(source))
        else:
            logger.error('Unknown source type')
            exit()

        self.image_type = 'CV2'  # 'PIL' # or CV2

    def next(self):
        if self.source_type == 'camera':
            res, img = self.capture.read()
            return img
        elif self.source_type == 'video':
            res, img = self.capture.read()
            return img
        elif self.source_type == 'filelist':
            line = self.lines[self.next_line_id].strip()
            self.next_line_id = (self.next_line_id + 1) % len(self.lines)
            if self.image_type == 'CV2':
                img = cv2.imread(line)
            elif self.image_type == 'PIL':
                img = Image.open(line).convert('RGB')
            return img
