from __future__ import division, print_function

import copy
import math
from collections import OrderedDict

import torch
import torch.nn as nn

from ptcaffe.utils.utils import make_list

__all__ = ['Crop', 'Slice', 'Permute', 'Flatten', 'PriorBox']


class Crop(nn.Module):
    def __init__(self, layer, *input_shapes):
        super(Crop, self).__init__()
        crop_param = layer.get('crop_param', OrderedDict())
        axis = int(crop_param.get('axis', 2))
        offsets = make_list(crop_param.get('offset', '0'))
        offsets = [int(offset) for offset in offsets]
        self.axis = axis
        input_dims = len(input_shapes[0])
        if len(offsets) == 1:
            offsets = offsets * (input_dims - axis)
        assert(len(offsets) == (input_dims - axis))
        self.offsets = offsets

    def __repr__(self):
        return 'Crop(axis=%d, offsets=%s)' % (self.axis, self.offsets)

    def forward_shape(self, input_shape, ref_shape):
        output_shape = copy.copy(input_shape)
        for i in range(self.axis, len(input_shape)):
            output_shape[i] = ref_shape[i]
        return output_shape

    def forward(self, x, ref):
        slices = [slice(None, None, None)] * self.axis
        for axis in range(self.axis, x.dim()):
            ref_size = ref.size(axis)
            offset = self.offsets[axis - self.axis]
            slices.append(slice(offset, offset + ref_size, None))
        out = x[slices].contiguous()
        return out


class Slice(nn.Module):
    def __init__(self, layer, input_shape):
        super(Slice, self).__init__()
        tname = layer['top']
        axis = int(layer['slice_param']['axis'])
        if not (isinstance(tname, list) and len(tname) >= 2):
            raise ValueError('Slice layers requires multiple top')
        slice_points = layer['slice_param']['slice_point']
        if not isinstance(slice_points, list):
            slice_points = [slice_points]
        if len(slice_points) != len(tname) - 1:
            raise ValueError('Slice layers requires |top| - 1 slice_points')
        self.slice_points = [int(s) for s in slice_points]
        self.axis = axis

    def __repr__(self):
        return 'Slice(axis={}, slice_points={!r})'.format(self.axis, self.slice_points)

    def forward_shape(self, input_shape):
        output_shapes = []
        for s in self.build_slices(input_shape[self.axis]):
            o = copy.copy(input_shape)
            o[self.axis] = s[-1].stop - s[-1].start
            output_shapes.append(o)
        return tuple(output_shapes)

    def forward_legacy(self, x):
        prev = 0
        outputs = []
        is_cuda = x.is_cuda
        if is_cuda:
            device_id = x.data.get_device()
        last = x.size(self.axis)
        for idx, slice_point in enumerate(self.slice_points + [last]):
            rng = range(prev, slice_point)
            rng = torch.LongTensor(rng)
            if is_cuda:
                rng = rng.cuda(device_id)
            y = x.index_select(self.axis, rng)
            prev = slice_point
            outputs.append(y)
        return tuple(outputs)

    def forward(self, x):
        N = x.size(self.axis)
        return tuple(x[s] for s in self.build_slices(N))

    def build_slices(self, stop):
        # say slicing x on axis=3, following is exactly `x[:, :, :, ?]`
        slices = [slice(None, None, None)] * (self.axis + 1)
        xs = [0] + self.slice_points + [stop]
        for left, right in zip(xs, xs[1:]):
            slices[-1] = slice(left, right)
            yield slices


class Permute(nn.Module):
    def __init__(self, layer, input_shape):
        super(Permute, self).__init__()
        orders = layer['permute_param']['order']
        self.orders = [int(order) for order in orders]

    def __repr__(self):
        return 'Permute(%s)' % self.orders

    def forward_shape(self, input_shape):
        output_shape = [input_shape[order] for order in self.orders]
        return output_shape

    def forward(self, x):
        x = x.permute(*self.orders).contiguous()
        return x


class Flatten(nn.Module):
    def __init__(self, layer, input_shape):
        super(Flatten, self).__init__()
        flatten_param = layer.get('flatten_param', OrderedDict())
        axis = int(flatten_param.get('axis', '1'))
        self.axis = axis

    def __repr__(self):
        return 'Flatten(axis=%d)' % self.axis

    def forward_shape(self, input_shape):
        left_size = 1
        right_size = 1
        for i in range(self.axis):
            left_size = input_shape[i] * left_size
        for i in range(self.axis, len(input_shape)):
            right_size = input_shape[i] * right_size
        return [left_size, right_size]

    def forward(self, x):
        left_size = 1
        for i in range(self.axis):
            left_size = x.size(i) * left_size
        return x.view(left_size, -1)


class PriorBox(nn.Module):
    """Compute priorbox coordinates in center-offset form for each source
    feature map.
    Note:
    This 'layer' has changed between versions of the original SSD
    paper, so we include both versions, but note v2 is the most tested and most
    recent version of the paper.
    """

    def __init__(self, layer, *input_shapes):
        super(PriorBox, self).__init__()
        min_sizes = layer['prior_box_param']['min_size']
        min_sizes = min_sizes if isinstance(min_sizes, list) else [min_sizes]
        min_sizes = [float(min_size) for min_size in min_sizes]
        max_sizes = None
        if 'max_size' in layer['prior_box_param']:
            max_sizes = layer['prior_box_param']['max_size']
            max_sizes = max_sizes if isinstance(max_sizes, list) else [max_sizes]
            max_sizes = [float(max_size) for max_size in max_sizes]
            assert(len(min_sizes) == len(max_sizes))
            for i in range(len(min_sizes)):
                assert(max_sizes[i] > min_sizes[i])
        aspects = []
        if 'aspect_ratio' in layer['prior_box_param']:
            # print(layer['prior_box_param']['aspect_ratio'])
            aspects = layer['prior_box_param']['aspect_ratio']
            if isinstance(aspects, list):
                aspects = [float(aspect) for aspect in aspects]
            else:
                aspects = [float(aspects)]
        if len(aspects) == 0:
            aspects.append(1.0)
        clip = (layer['prior_box_param']['clip'] == 'true')
        flip = False
        if 'flip' in layer['prior_box_param']:
            flip = (layer['prior_box_param']['flip'] == 'true')
        if 'step' in layer['prior_box_param']:
            step = int(float(layer['prior_box_param']['step']))
        else:
            assert(len(input_shapes) >= 2)
            step_w = int(input_shapes[1][3] / input_shapes[0][3])
            step_h = int(input_shapes[1][2] / input_shapes[0][2])
            assert(step_w == step_h)
            step = step_w
        offset = float(layer['prior_box_param']['offset'])
        variances = layer['prior_box_param']['variance']
        variances = [float(v) for v in variances]
        self.min_sizes = min_sizes
        self.max_sizes = max_sizes
        self.aspects = aspects
        self.clip = clip
        self.flip = flip
        self.step = step
        self.offset = offset
        self.variances = variances

    def __repr__(self):
        return 'PriorBox()'
        #return 'PriorBox(min_size=%f, max_size=%f, clip=%d, flip=%d, step=%d, offset=%f, variances=%s)' % (self.min_size, self.max_size, self.clip, self.flip, self.step, self.offset, self.variances)
        
    def forward_shape(self, feature_shape, image_shape):
        feature_height = feature_shape[2]
        feature_width = feature_shape[3]
        image_height = image_shape[2]
        image_width = image_shape[3]
        if self.flip:
            anchors_per_loc = len(self.min_sizes) * len(self.aspects)
            for ar in self.aspects:
                if ar != 1.0:
                    anchors_per_loc += len(self.min_sizes)
        else:
            anchors_per_loc = len(self.min_sizes) * len(self.aspects)
        if self.max_sizes:
            anchors_per_loc += len(self.max_sizes)
        output_shape = [1, 2, anchors_per_loc * feature_height * feature_width * 4]
        return output_shape

    def forward(self, feature, image):
        mean = []
        #assert(feature.size(2) == feature.size(3))
        #assert(image.size(2) == image.size(3))
        feature_height = feature.size(2)
        feature_width = feature.size(3)
        image_height = image.size(2)
        image_width = image.size(3)
        # for i, j in product(range(feature_height), repeat=2):
        for j in range(feature_height):
            for i in range(feature_width):
                # unit center x,y
                for idx, min_size in enumerate(self.min_sizes):
                    cx = (i + self.offset) * self.step / image_width
                    cy = (j + self.offset) * self.step / image_height
                    mw = float(min_size) / image_width
                    mh = float(min_size) / image_height
                    mean += [cx - mw / 2.0, cy - mh / 2.0, cx + mw / 2.0, cy + mh / 2.0]

                    if self.max_sizes:
                        max_size = self.max_sizes[idx]
                        ww = math.sqrt(mw * float(max_size) / image_width)
                        hh = math.sqrt(mh * float(max_size) / image_height)
                        mean += [cx - ww / 2.0, cy - hh / 2.0, cx + ww / 2.0, cy + hh / 2.0]
                    for aspect in self.aspects:
                        ww = mw * math.sqrt(aspect)
                        hh = mh / math.sqrt(aspect)
                        if aspect != 1.0:
                            mean += [cx - ww / 2.0, cy - hh / 2.0, cx + ww / 2.0, cy + hh / 2.0]
                        if self.flip and aspect != 1.0:
                            ww = mw / math.sqrt(aspect)
                            hh = mh * math.sqrt(aspect)
                            mean += [cx - ww / 2.0, cy - hh / 2.0, cx + ww / 2.0, cy + hh / 2.0]

        # back to torch land
        output1 = torch.Tensor(mean).view(-1, 4)
        output2 = torch.FloatTensor(self.variances).view(1, 4).expand_as(output1)
        if self.clip:
            output1.clamp_(max=1, min=0)
        output1 = output1.view(1, 1, -1)
        output2 = output2.contiguous().view(1, 1, -1)
        output = torch.cat([output1, output2], 1)
        if feature.data.is_cuda:
            device_id = feature.data.get_device()
            return output.cuda(device_id)
        else:
            return output
