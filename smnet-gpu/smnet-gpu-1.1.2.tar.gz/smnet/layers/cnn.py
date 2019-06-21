# ----------------------------
# SMNet Convolutional Networks
# Written by smarsu
# ----------------------------

"""Convolutional nerual network layer"""

import math
import numpy as np
from numba import jit

from ..blob import Tensor
from .. import layer as nn
from .. import net


@jit(nopython=True, parallel=True, fastmath=True)
def extract_image_patchs(input, ho, wo, hs, ws, hf, wf, ni, cf):
    input_patches = []
    for _h in range(ho):
        for _w in range(wo):
            _h_start = _h * hs
            _w_start = _w * ws
            input_patches.append(np.reshape(np.ascontiguousarray(input[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :]), (ni, 1, cf)))
    return input_patches


@jit(nopython=True, parallel=True, fastmath=True)
def extract_image_patchs_max_pool(value, ho, wo, hs, ws, hf, wf):
    input_patches = []
    for _h in range(ho):
        for _w in range(wo):
            _h_start = _h * hs
            _w_start = _w * ws
            input_patches.append(value[:, _h_start:_h_start+hf, _w_start:_w_start+wf])
    return input_patches


@jit(nopython=True, parallel=True, fastmath=True)
def max_pool_backpropagation(collect_grad, grad, ni, ci, _h_start, h_index, _w_start, w_index, _h, _w):
    for _b in range(ni):
        for _c in range(ci):
            collect_grad[_b, _h_start+h_index[_b, _c], _w_start+w_index[_b, _c], _c] += grad[_b, _h, _w, _c]


@jit(nopython=True, parallel=True, fastmath=True)
def extract_image_patchs_avg_pool(value, ho, wo, hs, ws, hf, wf):
    input_patches = []
    for _h in range(ho):
        for _w in range(wo):
            _h_start = _h * hs
            _w_start = _w * ws
            input_patches.append(value[:, _h_start:_h_start+hf, _w_start:_w_start+wf])
    return input_patches


@jit(nopython=True, parallel=True, fastmath=True)
def avg_pool_backpropagation(collect_grad, grad, ho, wo, hs, ws, hf, wf, cell_area):
    for _h in range(ho):
        for _w in range(wo):
            _h_start = _h * hs
            _w_start = _w * ws
            collect_grad[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :] += np.tile(grad[:, _h, _w, :], (1, hf, wf, 1)) / cell_area  # cell_area: hf * wf

   
@jit(nopython=True, parallel=True, fastmath=True)
def global_max_pool_backpropagation(_inter_grad, grad, n, c, max_ids_h, max_ids_w):
    for _n in range(n):
        for _c in range(c):
            _inter_grad[_n, max_ids_h[_n, _c], max_ids_w[_n, _c], _c] += grad[_n, _c]


class Conv2D(nn.Layer):
    """
    TODO(smarsu): Add dilations.
    """

    def __init__(self, input, filter, strides, padding, stop_grad=False, name='Conv2D'):
        super(Conv2D, self).__init__(stop_grad=stop_grad, name=name)
        self._prebuilt(input, filter, strides, padding)

    
    def _prebuilt(self, input, filter, strides, padding):
        self.input = self._to_tensor(input)
        self.filter = self._to_tensor(filter)
        self.strides = strides
        self.padding = padding
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        input = self.input.data
        filter = self.filter.data
        strides = self.strides
        padding = self.padding

        ni, hi, wi, ci = input.shape
        ns, hs, ws, cs = strides
        hf, wf, _, co = filter.shape

        # 2. Prepare output shape
        cf = hf * wf * ci

        if padding == 'SAME':
            ho, wo = math.ceil(hi / hs), math.ceil(wi / ws)
        if padding == 'VALID':
            ho, wo = (hi - hf) // hs + 1, (wi - wf) // ws + 1

        # 3. Pad input if `padding` is SAME
        if padding == 'SAME':
            hp = hs * (ho - 1) + (hf - 1) + 1 - hi
            wp = ws * (wo - 1) + (wf - 1) + 1 - wi
            pad_shape = ((0, 0), (hp // 2, hp - hp // 2), (wp // 2, wp - wp // 2), (0, 0))
            self.pad_shape = pad_shape
            input = np.pad(input, pad_shape, 'constant', constant_values=0)

        self.pad_input_shape = input.shape

        # 4. Extracts image patches from the input tensor to form a virtual tensor
        input_patches = extract_image_patchs(input, ho, wo, hs, ws, hf, wf, ni, cf)
        """input_patches = []
        for _h in range(ho):
            for _w in range(wo):
                _h_start = _h * hs
                _w_start = _w * ws
                input_patche = np.reshape(input[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :], [ni, 1, cf])
                input_patches.append(input_patche)"""
        input_patches = np.concatenate(input_patches, axis=1)
        input_patches = np.reshape(input_patches, [ni, ho, wo, cf])
        self.input_patches = input_patches

        # 5. Flattens the filter to a 2-D matrix
        flatten_fliter = np.reshape(filter, [cf, co])
        self.flatten_fliter = flatten_fliter

        # 6. Compute result
        feature_map = np.matmul(input_patches, flatten_fliter)

        # 7. Feed result
        self.res.feed(feature_map)


    def backward(self):
        grad = self.res.grad
        self._compute_grad_input(grad)
        self._compute_grad_filter(grad)
    

    def _compute_grad_input(self, grad):
        # 1. Prepare data
        flatten_fliter = self.flatten_fliter
        strides = self.strides
        padding = self.padding

        # 2. Compute grad
        grad = np.matmul(grad, flatten_fliter.T)

        n, ho, wo, cf = grad.shape
        ns, hs, ws, cs = strides
        hf, wf, ci, co = self.filter.shape

        collect_grad = np.zeros(self.pad_input_shape, dtype=self.flatten_fliter.dtype)
        for _h in range(ho):
            for _w in range(wo):
                _h_start = _h * hs
                _w_start = _w * ws
                collect_grad[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :] += np.reshape(grad[:, _h, _w, :], [n, hf, wf, ci])

        if padding == 'SAME':
            collect_grad_shape = collect_grad.shape
            collect_grad = eval(
                'collect_grad[{}]'.format(
                    ','.join(['{}:{}'.format(l, collect_grad_shape[idx]-r) for idx, (l, r) in enumerate(self.pad_shape)])
                )
            )

        # 3. Add grad
        self.input.add_grad(collect_grad)


    def _compute_grad_filter(self, grad):
        # 1. Prepare data
        input_patches = self.input_patches

        # 2. Compute grad
        n, ho, wo, cf = input_patches.shape
        n, ho, wo, co = grad.shape
        input_patches = np.reshape(input_patches, (-1, cf))
        grad = np.reshape(grad, (-1, co))

        grad = np.matmul(input_patches.T, grad)
        grad = np.reshape(grad, self.filter.shape)

        # 3. Add grad
        self.filter.add_grad(grad)


def conv2d(input, filter, strides, padding='SAME', stop_grad=False, name='Conv2D'):
    if net.use_cuda:
        from ..cuda import cuda_layer
        return cuda_layer.GpuConv2d(input, filter, strides, padding, stop_grad, name).res
    else:
        return Conv2D(input, filter, strides, padding, stop_grad=stop_grad, name=name).res


class Max_pool(nn.Layer):
    def __init__(self, value, ksize, strides, padding, stop_grad, name):
        super(Max_pool, self).__init__(stop_grad=stop_grad, name=name)
        self._prebuilt(value, ksize, strides, padding)

    
    def _prebuilt(self, value, ksize, strides, padding):
        self.value = self._to_tensor(value)
        self.ksize = ksize
        self.strides = strides
        self.padding = padding
        self.res = Tensor()


    def forward(self):
        # 1. Prepare data
        value = self.value.data
        ksize = self.ksize
        strides = self.strides
        padding = self.padding

        ni, hi, wi, ci = value.shape
        _, hf, wf, _ = ksize
        ns, hs, ws, cs = strides

        # 2. Prepare output shape
        if padding == 'SAME':
            ho, wo = math.ceil(hi / hs), math.ceil(wi / ws)
        if padding == 'VALID':
            ho, wo = (hi - hf) // hs + 1, (wi - wf) // ws + 1

        # 3. Pad input if `padding` is SAME
        if padding == 'SAME':
            hp = hs * (ho - 1) + (hf - 1) + 1 - hi
            wp = ws * (wo - 1) + (wf - 1) + 1 - wi
            pad_shape = ((0, 0), (hp // 2, hp - hp // 2), (wp // 2, wp - wp // 2), (0, 0))
            self.pad_shape = pad_shape
            value = np.pad(value, pad_shape, 'constant', constant_values=-np.inf)  # What value shell I pad 0/-np.inf?

        self.pad_value = value
        self.pad_value_shape = value.shape

        # 4. Extracts image patches
        input_patches = extract_image_patchs_max_pool(value, ho, wo, hs, ws, hf, wf)
        """input_patches = []
        for _h in range(ho):
            for _w in range(wo):
                _h_start = _h * hs
                _w_start = _w * ws
                input_patche = value[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :]
                input_patches.append(input_patche)"""
                
        #input_patches = np.concatenate(input_patches, axis=1)
        input_patches = np.stack(input_patches, axis=3)
        input_patches = np.max(input_patches, axis=(1, 2))
        input_patches = np.reshape(input_patches, (-1, ho, wo, ci))

        # 5. Feed result
        self.res.feed(input_patches)


    def backward(self):
        grad = self.res.grad
        self._compute_grad_value(grad)


    def _compute_grad_value(self, grad):
        # 1. Prepare data
        #value = self.value.data
        value = self.pad_value
        ksize = self.ksize
        strides = self.strides
        padding = self.padding

        ni, hi, wi, ci = self.value.shape
        _, hf, wf, _ = ksize
        ns, hs, ws, cs = strides

        # 2. Prepare output shape
        if padding == 'SAME':
            ho, wo = math.ceil(hi / hs), math.ceil(wi / ws)
        if padding == 'VALID':
            ho, wo = (hi - hf) // hs + 1, (wi - wf) // ws + 1

        # 3. Compute grad
        collect_grad = np.zeros(self.pad_value_shape, dtype=self.value.dtype)
        for _h in range(ho):
            for _w in range(wo):
                _h_start = _h * hs
                _w_start = _w * ws
                patch_value = value[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :]
                patch_value = np.reshape(patch_value, [-1, hf * wf, ci])
                max_index = np.argmax(patch_value, axis=1)  # shape: [batch, channel_in]
                h_index, w_index = max_index // wf, max_index % wf

                #batch, channel_in = max_index.shape
                max_pool_backpropagation(collect_grad, grad, ni, ci, _h_start, h_index, _w_start, w_index, _h, _w)
                """for _b in range(batch):
                    for _c in range(channel_in):
                        collect_grad[_b, _h_start+h_index[_b, _c], _w_start+w_index[_b, _c], _c] += grad[_b, _h, _w, _c]
                """

        # 4. Depad grad
        if padding == 'SAME':
            collect_grad_shape = collect_grad.shape
            collect_grad = eval(
                'collect_grad[{}]'.format(
                    ','.join(['{}:{}'.format(l, collect_grad_shape[idx]-r) for idx, (l, r) in enumerate(self.pad_shape)])
                )
            )

        # 5. Add grad
        self.value.add_grad(collect_grad)


def max_pool(value, ksize, strides, padding, stop_grad=False, name='Max_pool'):
    if net.use_cuda:
        from ..cuda import cuda_layer
        return cuda_layer.GpuMaxPool(value, ksize, strides, padding, stop_grad, name).res
    else:
        return Max_pool(value, ksize, strides, padding, stop_grad, name).res


class Avg_pool(nn.Layer):
    def __init__(self, value, ksize, strides, padding, stop_grad, name):
        super(Avg_pool, self).__init__(stop_grad=stop_grad, name=name)
        self._prebuilt(value, ksize, strides, padding)

    
    def _prebuilt(self, value, ksize, strides, padding):
        self.value = value
        self.ksize = ksize
        self.strides = strides
        self.padding = padding
        self.res = Tensor()


    def forward(self):
        # 1. Prepare data
        value = self.value.data
        ksize = self.ksize
        strides = self.strides
        padding = self.padding

        ni, hi, wi, ci = value.shape
        _, hf, wf, _ = ksize
        ns, hs, ws, cs = strides

        # 2. Prepare output shape
        if padding == 'SAME':
            ho, wo = math.ceil(hi / hs), math.ceil(wi / ws)
        if padding == 'VALID':
            ho, wo = (hi - hf) // hs + 1, (wi - wf) // ws + 1

        # 3. Pad input if `padding` is SAME
        if padding == 'SAME':
            hp = hs * (ho - 1) + (hf - 1) + 1 - hi
            wp = ws * (wo - 1) + (wf - 1) + 1 - wi
            pad_shape = ((0, 0), (hp // 2, hp - hp // 2), (wp // 2, wp - wp // 2), (0, 0))
            self.pad_shape = pad_shape
            value = np.pad(value, pad_shape, 'constant', constant_values=0)  # What value shell I pad 0/-np.inf?

        self.pad_value = value
        self.pad_value_shape = value.shape

        # 4. Extracts image patches
        input_patches = extract_image_patchs_avg_pool(value, ho, wo, hs, ws, hf, wf)
        """input_patches = []
        for _h in range(ho):
            for _w in range(wo):
                _h_start = _h * hs
                _w_start = _w * ws
                input_patche = value[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :]
                input_patches.append(input_patche)"""
                
        #input_patches = np.concatenate(input_patches, axis=1)
        input_patches = np.stack(input_patches, axis=3)
        #input_patches = np.mean(input_patches, axis=(1, 2))
        pad_num = np.sum(input_patches != 0, axis=(1, 2))
        input_patches = np.sum(input_patches, axis=(1, 2)) / pad_num
        input_patches = np.reshape(input_patches, (-1, ho, wo, ci))

        # 5. Feed result
        self.res.feed(input_patches)


    def backward(self):
        grad = self.res.grad
        self._compute_grad_value(grad)

    
    def _compute_grad_value(self, grad):
        # 1. Prepare data
        #value = self.value.data
        value = self.pad_value
        ksize = self.ksize
        strides = self.strides
        padding = self.padding

        ni, hi, wi, ci = self.value.shape
        _, hf, wf, _ = ksize
        ns, hs, ws, cs = strides

        # 2. Prepare output shape
        if padding == 'SAME':
            ho, wo = math.ceil(hi / hs), math.ceil(wi / ws)
        if padding == 'VALID':
            ho, wo = (hi - hf) // hs + 1, (wi - wf) // ws + 1

        # 3. Compute grad
        collect_grad = np.zeros(self.pad_value_shape, dtype=self.value.dtype)
        cell_area = hf * wf
        avg_pool_backpropagation(collect_grad, grad, ho, wo, hs, ws, hf, wf, cell_area)
        """for _h in range(ho):
            for _w in range(wo):
                _h_start = _h * hs
                _w_start = _w * ws
                collect_grad[:, _h_start:_h_start+hf, _w_start:_w_start+wf, :] += np.tile(grad[:, _h, _w, :], (1, hf, wf, 1)) / cell_area  # cell_area: hf * wf
        """

        # 4. Depad grad
        if padding == 'SAME':
            collect_grad_shape = collect_grad.shape
            collect_grad = eval(
                'collect_grad[{}]'.format(
                    ','.join(['{}:{}'.format(l, collect_grad_shape[idx]-r) for idx, (l, r) in enumerate(self.pad_shape)])
                )
            )

        # 5. Add grad
        self.value.add_grad(collect_grad)


def avg_pool(value, ksize, strides, padding, stop_grad=False, name='Avg_pool'):
    return Avg_pool(value, ksize, strides, padding, stop_grad, name).res


class Global_avg_pool(nn.Layer):
    def __init__(self, value, stop_grad, name):
        super(Global_avg_pool, self).__init__(stop_grad=stop_grad, name=name)
        self._prebuilt(value)

    
    def _prebuilt(self, value):
        self.value = value
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        value = self.value.data

        # 2. Compute and feed result
        self.res.feed(np.mean(value, axis=(1, 2)))

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_value(grad)


    def _compute_grad_value(self, grad):
        # 1. Prepare data
        _, h, w, _ = self.value.shape
        area = h * w

        # 2. Compute grad
        grad = grad / area

        # 3. Add grad
        self.value.add_grad(grad)


def global_avg_pool(value, stop_grad=False, name='Global_max_pool'):
    return Global_avg_pool(value, stop_grad, name).res


class Global_max_pool(nn.Layer):
    def __init__(self, value, stop_grad, name):
        super(Global_max_pool, self).__init__(stop_grad, name)
        self._prebuilt(value)

    
    def _prebuilt(self, value):
        self.value = value
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        value = self.value.data

        # 2. Compute and feed result
        self.res.feed(np.max(value, axis=(1, 2)))
    

    def backward(self):
        grad = self.res.grad
        self._compute_grad_value(grad)

    
    def _compute_grad_value(self, grad):
        # 1. Prepare data
        value = self.value.data
        n, h, w, c = value.shape

        # 2. Compute grad
        value = np.reshape(value, (n, h * w, c))
        max_ids = np.argmax(value, axis=1)
        max_ids_h, max_ids_w = max_ids // w, max_ids % w

        _inter_grad = np.zeros(self.value.shape, dtype=self.value.dtype)
        global_max_pool_backpropagation(_inter_grad, grad, n, c, max_ids_h, max_ids_w)
        """
        for _n in range(n):
            for _c in range(c):
                _inter_grad[_n, max_ids_h[_n, _c], max_ids_w[_n, _c], _c] += grad[_n, _c]
        """
            
        # 3. Add grad
        self.value.add_grad(_inter_grad)


def global_max_pool(value, stop_grad=False, name='Global_max_pool'):
    return Global_max_pool(value, stop_grad, name).res
