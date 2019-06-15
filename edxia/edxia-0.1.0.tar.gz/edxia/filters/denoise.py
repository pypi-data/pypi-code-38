# Copyright (c) 2019 Fabien Georget <fabien.georget@epfl.ch>, EPFL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.



from .base_filter import AbstractFilter

from skimage.restoration import denoise_tv_chambolle
from scipy.ndimage import gaussian_filter, uniform_filter


class DenoiseFilter(AbstractFilter):
    """Denoising filter"""
    def __init__(self, weight=0.1, **kwargs):
        self.weight = 0.1
        self.params = kwargs

    def apply_impl(self, eds_map):
        return denoise_tv_chambolle(eds_map.map, weight=self.weight, **(self.params))

class UniformFilter(AbstractFilter):
    """Uniform filter"""
    def __init__(self, size, **kwargs):
        self.radius = size
        self.params = kwargs

    def apply_impl(self, eds_map):
        return uniform_filter(eds_map.map, size=self.radius, **(self.params))

class GaussianFilter(AbstractFilter):
    """GaussianFilter"""
    def __init__(self, sigma, **kwargs):
        self.sigma = sigma
        self.params = kwargs

    def apply_impl(self, eds_map):
        return gaussian_filter(eds_map.map, sigma=self.sigma, **(self.params))
