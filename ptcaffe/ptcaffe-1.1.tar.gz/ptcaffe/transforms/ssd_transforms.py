from __future__ import division, print_function

import torch
import cv2
import numpy as np
import types
from numpy import random

import sys
if sys.version_info[0] == 2:
    import xml.etree.cElementTree as ET
else:
    import xml.etree.ElementTree as ET

def parse_yolo2_annotation(annopath, class_to_ind, width, height):
    lines = open(annopath).readlines()
    if len(lines) == 0:
        return []
    res = []
    for idx, line in enumerate(lines):
        items = line.split()
        cx = float(items[1])
        cy = float(items[2])
        w = float(items[3])
        h = float(items[4])
        x1 = cx - w / 2.0
        y1 = cy - h / 2.0
        x2 = cx + w / 2.0
        y2 = cy + h / 2.0
        label = int(items[0]) + 1
        bndbox = [x1, y1, x2, y2, label]
        bndbox.append(0) # difficult
        res.append(bndbox)
    return res

def parse_xml_annotation(annopath, class_to_ind, width, height, keep_difficult):
    target = ET.parse(annopath).getroot()
    res = []
    for obj in target.iter('object'):
        difficult = int(obj.find('difficult').text) == 1
        if not keep_difficult and difficult:
            continue
        name = obj.find('name').text.lower().strip()
        bbox = obj.find('bndbox')

        pts = ['xmin', 'ymin', 'xmax', 'ymax']
        bndbox = []
        for i, pt in enumerate(pts):
            cur_pt = float(bbox.find(pt).text) - 1
            # scale height or width
            cur_pt = cur_pt / width if i % 2 == 0 else cur_pt / height
            bndbox.append(cur_pt)
        label_idx = class_to_ind[name] + 1 # 0 for background
        bndbox.append(label_idx)
        bndbox.append(difficult)
        res += [bndbox]  # [xmin, ymin, xmax, ymax, label_ind]

    return res


def intersect(box_a, box_b):
    max_xy = np.minimum(box_a[:, 2:], box_b[2:])
    min_xy = np.maximum(box_a[:, :2], box_b[:2])
    inter = np.clip((max_xy - min_xy), a_min=0, a_max=np.inf)
    return inter[:, 0] * inter[:, 1]


def jaccard_numpy(box_a, box_b):
    inter = intersect(box_a, box_b)
    area_a = ((box_a[:, 2]-box_a[:, 0]) *
              (box_a[:, 3]-box_a[:, 1]))  # [A,B]
    area_b = ((box_b[2]-box_b[0]) *
              (box_b[3]-box_b[1]))  # [A,B]
    union = area_a + area_b - inter
    return inter / union  # [A,B]


class SSD_LineLoader(object):
    def __init__(self, num_classes=None, classes=None, keep_difficult=True):
        if classes is not None:
            self.class_to_ind = dict(zip(classes, range(len(classes))))
        elif num_classes is not None:
            classes = ["class%d" % i for i in range(num_classes)]
            self.class_to_ind = dict(zip(classes, range(len(classes))))
        else:
            classes = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
            self.class_to_ind = dict(zip(classes, range(len(classes))))

        self.keep_difficult = keep_difficult

    def __call__(self, line):
        imgpath, annopath = line.strip().split()

        img = cv2.imread(imgpath)
        height, width, channels = img.shape
        if annopath.find(".xml") >= 0:
            target = parse_xml_annotation(annopath, self.class_to_ind, width, height, self.keep_difficult)
        elif annopath.find(".txt") >= 0:
            target = parse_yolo2_annotation(annopath, self.class_to_ind, width, height)

        if len(target) == 0:
            raise ValueError("target is empty")

        target = np.array(target)
        boxes = target[:, :4]
        labels = target[:, 4]
        difficults = target[:, 5]

        return img, boxes, labels, difficults

class CV2_Int2Float(object):
    def __call__(self, image):
        return image.astype(np.float32)

class CV2_SubtractMeans(object):
    def __init__(self, mean):
        self.mean = np.array(mean, dtype=np.float32)

    def __call__(self, image):
        image = image.astype(np.float32)
        image -= self.mean
        return image.astype(np.float32)

class BBox_Percent2Absolute(object):
    def __call__(self, image, boxes):
        height, width, channels = image.shape
        boxes[:, 0] *= width 
        boxes[:, 2] *= width
        boxes[:, 1] *= height
        boxes[:, 3] *= height
        return image, boxes

class BBox_Absolute2Percent(object):
    def __call__(self, image, boxes):
        height, width, channels = image.shape
        boxes[:, 0] /= float(width)
        boxes[:, 2] /= float(width)
        boxes[:, 1] /= float(height)
        boxes[:, 3] /= float(height)

        return image, boxes

class CV2_Resize(object):
    # size could be
    # size
    # (height, width) 
    # (-1, width) 
    # (height, -1) 
    def __init__(self, size):
        if isinstance(size ,(list, tuple)):
            self.size = size
        else:
            self.size = (size, size)

    def __call__(self, image):
        height = image.shape[0]
        width = image.shape[1]
        new_height, new_width = self.size
        if new_height == -1:
            new_height = int((new_width * height)//width)
        elif new_width == -1:
            new_width = int((new_height * width)//height)
        image = cv2.resize(image, (new_width, new_height))
        return image

class CV2_RandomSaturation(object):
    def __init__(self, lower=0.5, upper=1.5):
        self.lower = lower
        self.upper = upper
        assert self.upper >= self.lower, "contrast upper must be >= lower."
        assert self.lower >= 0, "contrast lower must be non-negative."

    def __call__(self, image):
        image[:, :, 1] *= random.uniform(self.lower, self.upper)
        return image

class CV2_RandomHue(object):
    def __init__(self, delta=18.0):
        assert delta >= 0.0 and delta <= 360.0
        self.delta = delta

    def __call__(self, image):
        image[:, :, 0] += random.uniform(-self.delta, self.delta)
        image[:, :, 0][image[:, :, 0] > 360.0] -= 360.0
        image[:, :, 0][image[:, :, 0] < 0.0] += 360.0
        return image

class CV2_RandomLightingNoise(object):
    def __init__(self):
        self.perms = ((0, 1, 2), (0, 2, 1),
                      (1, 0, 2), (1, 2, 0),
                      (2, 0, 1), (2, 1, 0))

    def __call__(self, image):
        swap = self.perms[random.randint(len(self.perms))]
        shuffle = CV2_SwapChannels(swap)  # shuffle channels
        image = shuffle(image)
        return image

class CV2_SwapChannels(object):
    def __init__(self, swaps):
        self.swaps = swaps

    def __call__(self, image):
        image = image[:, :, self.swaps]
        return image

class CV2_ConvertColor(object):
    def __init__(self, current='BGR', transform='HSV'):
        self.transform = transform.upper()
        self.current = current.upper()

    def __call__(self, image):
        if self.current == 'BGR' and self.transform == 'HSV':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        elif self.current == 'HSV' and self.transform == 'BGR':
            image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        else:
            raise NotImplementedError
        return image

class CV2_RandomContrast(object):
    def __init__(self, lower=0.5, upper=1.5):
        self.lower = lower
        self.upper = upper
        assert self.upper >= self.lower, "contrast upper must be >= lower."
        assert self.lower >= 0, "contrast lower must be non-negative."

    def __call__(self, image):
        alpha = random.uniform(self.lower, self.upper)
        image *= alpha
        image = np.clip(image, 0.0, 255.0)
        return image

class CV2_RandomBrightness(object):
    def __init__(self, delta=32):
        assert delta >= 0.0
        assert delta <= 255.0
        self.delta = delta

    def __call__(self, image):
        delta = random.uniform(-self.delta, self.delta)
        image += delta
        return image

class Tensor_ToCV2(object):
    def __call__(self, tensor):
        return tensor.cpu().numpy().astype(np.float32).transpose((1, 2, 0))

class CV2_ToTensor(object):
    def __call__(self, cvimage):
        return torch.from_numpy(cvimage.astype(np.float32)).permute(2, 0, 1)

class SSD_RandomSampleCrop(object):
    def __init__(self):
        self.sample_options = (
            # using entire original input image
            None,
            # sample a patch s.t. MIN jaccard w/ obj in .1,.3,.4,.7,.9
            (0.1, None),
            (0.3, None),
            (0.7, None),
            (0.9, None),
            # randomly sample a patch
            (None, None),
        )

    def __call__(self, image, boxes, labels, difficults):
        height, width, _ = image.shape
        while True:
            # randomly choose a mode
            mode = random.choice(self.sample_options)
            if mode is None:
                return image, boxes, labels, difficults

            min_iou, max_iou = mode
            if min_iou is None:
                min_iou = float('-inf')
            if max_iou is None:
                max_iou = float('inf')

            # max trails (50)
            for _ in range(50):
                current_image = image

                w = random.uniform(0.3 * width, width)
                h = random.uniform(0.3 * height, height)

                # aspect ratio constraint b/t .5 & 2
                if h / w < 0.5 or h / w > 2:
                    continue

                left = random.uniform(width - w)
                top = random.uniform(height - h)

                # convert to integer rect x1,y1,x2,y2
                rect = np.array([int(left), int(top), int(left+w), int(top+h)])

                # calculate IoU (jaccard overlap) b/t the cropped and gt boxes
                overlap = jaccard_numpy(boxes, rect)

                # is min and max overlap constraint satisfied? if not try again
                if overlap.min() < min_iou and max_iou < overlap.max():
                    continue

                # cut the crop from the image
                current_image = current_image[rect[1]:rect[3], rect[0]:rect[2],
                                              :]

                # keep overlap with gt box IF center in sampled patch
                centers = (boxes[:, :2] + boxes[:, 2:]) / 2.0

                # mask in all gt boxes that above and to the left of centers
                m1 = (rect[0] < centers[:, 0]) * (rect[1] < centers[:, 1])

                # mask in all gt boxes that under and to the right of centers
                m2 = (rect[2] > centers[:, 0]) * (rect[3] > centers[:, 1])

                # mask in that both m1 and m2 are true
                mask = m1 * m2

                # have any valid boxes? try again if not
                if not mask.any():
                    continue

                # take only matching gt boxes
                current_boxes = boxes[mask, :].copy()

                # take only matching gt labels
                current_labels = labels[mask]
                current_difficults = difficults[mask]

                # should we use the box left and top corner or the crop's
                current_boxes[:, :2] = np.maximum(current_boxes[:, :2],
                                                  rect[:2])
                # adjust to crop (by substracting crop's left,top)
                current_boxes[:, :2] -= rect[:2]

                current_boxes[:, 2:] = np.minimum(current_boxes[:, 2:],
                                                  rect[2:])
                # adjust to crop (by substracting crop's left,top)
                current_boxes[:, 2:] -= rect[:2]

                return current_image, current_boxes, current_labels, current_difficults

class SSD_Expand(object):
    def __init__(self, mean, expand_prob=0.5, expand_ratio=4):
        self.mean = mean
        self.expand_prob = expand_prob
        self.expand_ratio = expand_ratio
        assert(self.expand_ratio >= 1.0)

    def __call__(self, image, boxes):
        if random.random() > self.expand_prob:
            return image, boxes

        height, width, depth = image.shape
        ratio = random.uniform(1, self.expand_ratio)
        left = random.uniform(0, width*ratio - width)
        top = random.uniform(0, height*ratio - height)

        expand_image = np.zeros(
            (int(height*ratio), int(width*ratio), depth),
            dtype=image.dtype)
        expand_image[:, :, :] = self.mean
        expand_image[int(top):int(top + height),
                     int(left):int(left + width)] = image
        image = expand_image

        boxes = boxes.copy()
        boxes[:, :2] += (int(left), int(top))
        boxes[:, 2:] += (int(left), int(top))

        return image, boxes

class SSD_RandomMirror(object):
    def __call__(self, image, boxes):
        _, width, _ = image.shape
        if random.randint(2):
            image = image[:, ::-1]
            boxes = boxes.copy()
            boxes[:, 0::2] = width - boxes[:, 2::-2]
        return image, boxes

class SSD_TensorflowAdjust(object):
    def __init__(self, adjust=False):
        self.adjust = adjust 

    def __call__(self, image, boxes):
        height, width, _ = image.shape
        if self.adjust:
            image = image[:, ::-1, :]
            image = image[::-1, :, :]
            image = image[:, :, ::-1]
            image = image / 127.5
            boxes = boxes.copy()
            boxes[:, 0::2] = 1.0 - boxes[:, 2::-2]
            boxes[:, 1::2] = 1.0 - boxes[:, 3::-2]
        return image, boxes

#class CV2_PhotometricDistort(object):
#    def __init__(self):
#        self.pd = [
#            CV2_RandomContrast(),
#            CV2_ConvertColor(transform='HSV'),
#            CV2_RandomSaturation(),
#            CV2_RandomHue(),
#            CV2_ConvertColor(current='HSV', transform='BGR'),
#            CV2_RandomContrast()
#        ]
#        self.rand_brightness = CV2_RandomBrightness()
#        self.rand_light_noise = CV2_RandomLightingNoise()
#
#    def __call__(self, image):
#        im = image.copy()
#        im = self.rand_brightness(im)
#        if random.randint(2):
#            distort = Compose(self.pd[:-1])
#        else:
#            distort = Compose(self.pd[1:])
#        im = distort(im), boxes, labels)
#        return self.rand_light_noise(im)

class SSD_MergeTarget(object):
    def __call__(self, image, boxes, labels, difficults):
        target = np.hstack((boxes, np.expand_dims(labels, axis=1), np.expand_dims(difficults, axis=1)))
        return torch.from_numpy(image).permute(2, 0, 1), target
