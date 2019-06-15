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

import numpy as np

from glue.core.component import Component
from glue.core import Data

from skimage.color import rgb2hsv

def gluedata_from_points(name, pts):
    """Create a glue Data container from a set of EDS points

    :param name: label of the Data container
    :param pts: an EDSPoints instance
    """
    pts_data = Data(label=name)
    for name, column in pts.df.iteritems():
        c = Component(column.values)
        pts_data.add_component(c, name)
    return pts_data

def gluedata_from_stack(name, stack, coords=None):
    """Create a glue Data container from a set of map stacks

    :param name: label of the Data container
    :param stack: a stack of EDS maps
    """
    stack_data = Data(label=name, coords=coords)
    for ind, component in enumerate(stack.components):
        c = Component(np.flipud(stack.map(component).map))
        stack_data.add_component(c, component)
    return stack_data

def gluedata_from_composite(name, composite, coords=None):
    """Create a glue Data container from a composite

    :param name: label of the Data container
    :param composite: a composite instance
    """
    cmp_data = Data(label=name, coords=coords)
    cmp_data.add_component(Component(np.flipud(composite.map[:,:,0])), "red")
    cmp_data.add_component(Component(np.flipud(composite.map[:,:,1])), "green")
    cmp_data.add_component(Component(np.flipud(composite.map[:,:,2])), "blue")

    hsv = rgb2hsv(composite.map)
    cmp_data.add_component(Component(np.flipud(hsv[:,:,0])), "hue")
    cmp_data.add_component(Component(np.flipud(hsv[:,:,1])), "saturation")
    cmp_data.add_component(Component(np.flipud(hsv[:,:,2])), "value")
    return cmp_data

def gluedata_from_stack_and_composite(name, stack, composite, coords=None):
    """Create a glue Data container from a set of map stacks

    :param name: label of the Data container
    :param stack: a stack of EDS maps
    """
    stack_data = Data(label=name, coords=coords)
    for ind, component in enumerate(stack.components):
        c = Component(np.flipud(stack.map(component).map))
        stack_data.add_component(c, component)

    stack_data.add_component(Component(np.flipud(composite.map[:,:,0])), "red")
    stack_data.add_component(Component(np.flipud(composite.map[:,:,1])), "green")
    stack_data.add_component(Component(np.flipud(composite.map[:,:,2])), "blue")

    hsv = rgb2hsv(composite.map)
    stack_data.add_component(Component(np.flipud(hsv[:,:,0])), "hue")
    stack_data.add_component(Component(np.flipud(hsv[:,:,1])), "saturation")
    stack_data.add_component(Component(np.flipud(hsv[:,:,2])), "value")
    return stack_data