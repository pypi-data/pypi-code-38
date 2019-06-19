# Copyright (c) 2016, Combine Control Systems AB
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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import six
import distutils.version
import matplotlib
from matplotlib import markers as mpl_markers
from . import colors


def _mpl_version():
    return distutils.version.LooseVersion(matplotlib.__version__).version[:3]


def list_from_cycle(cycle):
    first = next(cycle)
    result = [first]
    for current in cycle:
        if current == first:
            break
        else:
            result.append(current)

    # Reset iterator state:
    for current in cycle:
        if current == result[-1]:
            break
    return result


def set_color_cycle(axes, color_cycle):
    if _mpl_version() < [1, 5, 0]:
        axes.set(color_cycle=color_cycle)
    else:
        from matplotlib import cycler
        axes.set(prop_cycle=cycler(color=color_cycle))


def color_cycle(axes=None):
    if axes is None:
        return ['#' + c for c in colors.COLOR_CYCLES['default']]

    if _mpl_version() < [1, 5, 0]:
        return list_from_cycle(axes._get_lines.color_cycle)
    else:
        return [prop['color']
                for prop in list_from_cycle(axes._get_lines.prop_cycler)]


MARKERS = mpl_markers.MarkerStyle.markers

LINESTYLES = ['solid', 'dashed', 'dashdot', 'dotted']

DRAWSTYLES = ['default', 'steps', 'steps-pre', 'steps-mid', 'steps-post']

HISTTYPES = ['bar', 'step']

GROUPTYPES = ['grouped', 'stacked']

VALIGNMENTS = ['over', 'top', 'center', 'bottom', 'under']

LEGEND_LOC = {
    'best': 0,  # (only implemented for axes legends)
    'upper right': 1,
    'upper left': 2,
    'lower left': 3,
    'lower right': 4,
    'right': 5,
    'center left': 6,
    'center right': 7,
    'lower center': 8,
    'upper center': 9,
    'center': 10
}
FONTSIZE = ['xx-small',
            'x-small',
            'small',
            'medium',
            'large',
            'x-large',
            'xx-large']

def lookup_marker(marker):
    for key, value in six.iteritems(MARKERS):
        if marker == key:
            return marker
        elif marker == value:
            return key
    return None
