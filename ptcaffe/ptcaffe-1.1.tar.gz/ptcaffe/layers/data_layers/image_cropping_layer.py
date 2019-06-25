from __future__ import division, print_function

from collections import OrderedDict

import cv2
import numpy as np
import torch
import torch.nn as nn

__all__ = ['ImageCroppingData']

# -------
# layer {
#  top: "img_bbox"
#  name: "img_bbox"
#  bottom: "data"
#  bottom: "bbox"
#  type: "ImageCroppingData"
#  source_transform_param {
#    scale: 0.00390625
#    channel_type: false
#    # other: mean, std
#  }
#  target_transform_param {
#    mean: "[103.94, 116.78, 123.68]"
#    scale: 0.017
#    channel_type: false
#    new_width: 224
#    new_height: 224
#    # other: std
#  }
#  crop_param {
#    crop_factor: '[0.0, 0.0, 0.1, 0.1]' # x1,x2,y1,y2
#  }
# }


class ImageCroppingData(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(ImageCroppingData, self).__init__()
        self.source_transform_param = layer.get('source_transform_param', OrderedDict())
        self.target_transform_param = layer.get('target_transform_param', OrderedDict())
        self.new_width = int(self.target_transform_param.get('new_width', 224))
        self.new_height = int(self.target_transform_param.get('new_height', 224))
        crop_param = layer.get('crop_param', OrderedDict())
        crop_factor = crop_param.get('crop_factor', '')
        if crop_factor == '':
            self.crop_factor = [0.0, 0.0, 0.0, 0.0]
        else:
            crop_factor = crop_factor.lstrip('[').rstrip(']')
            self.crop_factor = [float(c.strip()) for c in crop_factor.split(',')]

    def bgr2rgb(self, im):
        b, g, r = im.split(1, dim=1)
        return torch.cat((r, g, b), dim=1)

    def source_transform(self, image, source_transform_param):
        # params for source transform params
        mean_value = source_transform_param.get('mean', '')
        if mean_value == '':
            mean_value = [0.0] * image.size(1)
        else:
            mean_value = mean_value.lstrip('[').rstrip(']')
            mean_value = [float(m.strip()) for m in mean_value.split(',')]

        std_value = source_transform_param.get('std', '')
        if std_value == '':
            std_value = [1.0] * image.size(1)
        else:
            std_value = std_value.lstrip('[').rstrip(']')
            std_value = [float(s.strip()) for s in std_value.split(',')]

        channel_type = (source_transform_param.get('channel_type', 'false') == 'true')
        scale = float(source_transform_param.get('scale', 1.0))

        image = image / scale
        for c in range(image.size(1)):
            image[:, c, :, :] = image[:, c, :, :] * std_value[c] + mean_value[c]
        # image = image * scale
        if channel_type:
            image = self.bgr2rgb(image)
        return image

    def target_transform(self, image, target_transform_param):
        mean_value = target_transform_param.get('mean', '')
        if mean_value == '':
            mean_value = [0.0] * image.shape[2]
        else:
            mean_value = mean_value.lstrip('[').rstrip(']')
            mean_value = [float(m.strip()) for m in mean_value.split(',')]

        std_value = target_transform_param.get('std', '')
        if std_value == '':
            std_value = [1.0] * image.shape[2]
        else:
            std_value = std_value.lstrip('[').rstrip(']')
            std_value = [float(s.strip()) for s in std_value.split(',')]

        channel_type = (target_transform_param.get('channel_type', 'false') == 'true')
        scale = float(target_transform_param.get('scale', 1.0))

        image = image.astype(np.float32)
        for c in range(image.shape[2]):
            image[:, :, c] = (image[:, :, c] - mean_value[c]) / std_value[c]
        image *= scale
        return image

    def cut_boxes_cv2(self, img, boxes):
        # image type: numpy h w c
        width = img.shape[1]
        height = img.shape[0]
        imgs = []
        for i in range(len(boxes)):
            box = boxes[i]
            x1 = int(round((box[0] - box[2] * (1 + self.crop_factor[0]) / 2.0) * width))
            y1 = int(round((box[1] - box[3] * (1 + self.crop_factor[2]) / 2.0) * height))
            x2 = int(round((box[0] + box[2] * (1 + self.crop_factor[1]) / 2.0) * width))
            y2 = int(round((box[1] + box[3] * (1 + self.crop_factor[3]) / 2.0) * height))

            x1 = min(max(x1, 0), width)
            x2 = min(max(x2, 0), width)
            y1 = min(max(y1, 0), height)
            y2 = min(max(y2, 0), height)
            imgs.append(img[y1:y2, x1:x2])

        if len(imgs) == 0:
            imgs.append(np.zeros((100, 100, 3), dtype=np.uint8))
        return imgs

    def forward(self, img, boxes):
        if img.size(0) == 1:
            img = self.source_transform(img.data.cpu(), self.source_transform_param)
            img = img.squeeze(0).permute(1, 2, 0).numpy().astype('uint8')
            imgs = self.cut_boxes_cv2(img, boxes.data)
            test_im = []
            for img in imgs:
                img = cv2.resize(img, (self.new_width, self.new_height))
                img = self.target_transform(img, self.target_transform_param)
                # test_im.append(torch.from_numpy(self.target_transform(img).transpose(2,0,1)).float().unsqueeze(0))
                test_im.append(torch.from_numpy(img.transpose(2, 0, 1)).float().unsqueeze(0))
            test_im = torch.cat(test_im[:])
            test_im = test_im.cuda()
        return test_im

    def forward_shape(self, img_shape, box_shape):
        return [1, 3, self.new_width, self.new_height]
