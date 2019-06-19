# Copyright (c) 2015, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import re
import six
import collections
import numpy as np


SCALE_TYPES = (
    'linear',
    'log'
)


re_color = re.compile('#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})',
                      flags=re.IGNORECASE)


color_string_to_tuple = lambda color_string: tuple(
    [int(x, 16) for x in re_color.match(color_string).groups()])


interpolate_color_tuples = lambda color1_tuple, color2_tuple, weight: tuple(
    [int((c2 - c1) * weight + c1)
     for c1, c2 in zip(color1_tuple, color2_tuple)])


tuple_to_color_string = lambda color_tuple: '#{:02x}{:02x}{:02x}'.format(
    *color_tuple)


class IdentityScale(object):
    """Scale doing nothing but returning the same value it receives."""

    def f(self, x):
        return x

    def __call__(self, domain_value):
        if (isinstance(domain_value, (collections.Sequence, np.ndarray)) and
                not isinstance(domain_value, six.string_types)):
            # This way we can return the same type of sequence as we get in.
            if domain_value.__class__ == np.ndarray:
                range_value = np.array([self.f(x) for x in domain_value])
            else:
                range_value = domain_value.__class__(
                    [self.f(x) for x in domain_value])
        else:
            range_value = self.f(domain_value)
        return range_value


class LinearScale(IdentityScale):
    """Linear interpolation scale."""

    def __init__(self, domain, range_, invalid_value=None):
        """Create a linear scale"""
        self._domain = domain
        self._range = range_
        self._invalid_value = invalid_value
        if isinstance(self._range[0], six.string_types):
            self.f = self.color_f
        else:
            self.f = self.numeric_f

    def color_f(self, x):
        # If set, return invalid color for NaN values.
        if self._invalid_value is not None and np.isnan(x):
            return self._invalid_value

        # Hold end values if outside domain.
        if x <= self._domain[0]:
            return self._range[0]
        elif x >= self._domain[-1]:
            return self._range[-1]

        # Find surrounding items.
        for i, (x1, x2) in enumerate(six.moves.zip(self._domain[0:-1],
                                                   self._domain[1:])):
            if x1 <= x <= x2:
                color1 = color_string_to_tuple(self._range[i])
                color2 = color_string_to_tuple(self._range[i + 1])
                weight = float(x - x1) / float(x2 - x1)
                break

        mid_color = interpolate_color_tuples(color1, color2, weight)

        return tuple_to_color_string(mid_color)

    def numeric_f(self, x):
        # If set, return invalid color for NaN values.
        if self._invalid_value is not None and np.isnan(x):
            return self._invalid_value

        return np.interp(x, self._domain, self._range)

    def __call__(self, domain_value):
        if self.f == self.color_f:
            result = super(LinearScale, self).__call__(domain_value)
            return result
        # Optimization since np.interp handles everything.
        return self.f(domain_value)


class OrdinalScale(IdentityScale):
    """
    Ordinal scale with discrete items. No interpolation. Just lookup.
    If the domain value does not exist a ValueError is thrown.
    """

    def __init__(self, domain, range_):
        self._domain_to_range = dict(list(zip(domain, range_)))

    def f(self, x):
        # Just return the range value corresponding to the index
        # of the domain value.
        return self._domain_to_range[x]


def create_scale(scale_type, domain, range_):
    if scale_type == 'identity':
        return IdentityScale()
    elif scale_type == 'linear':
        return LinearScale(domain, range_)
    elif scale_type == 'ordinal':
        return OrdinalScale(domain, range_)
    return None


class ScaleBinding(object):
    data_id = None
    scale_id = None

    def __init__(self, data_id, scale_id):
        self.data_id = data_id
        self.scale_id = scale_id

    def as_dict(self):
        return {
            'data': self.data_id,
            'scale': self.scale_id
        }
