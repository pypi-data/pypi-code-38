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

import glob
#import re
import os.path

from .chemistry import molar_masses

all_components = list(molar_masses.keys())
all_components.append("BSE")

"""Util functions for managing paths"""

def pattern_from_component(path, component):
    """Returns the path pattern from the file of a component.

    :param path: filepath to the map of the given component
    :param component: a component
    :returns: a filepath pattern to the maps
    """
    return path.replace(component, "{component}")

def pattern_from_BSE(bse_path):
    """Returns the path pattern from the file of the BSE map.

    :param bse_path: filepath to the BSE map
    :returns: a filepath pattern to the maps
    """
    return pattern_from_component(bse_path, "BSE")

def find_component_path(pattern, component):
    """Returns the filepath for a component

    :param pattern: a filepath pattern
    :param component: a component
    :returns: a valid filepath
    :raises: RuntimeError if no filepath exist for that component
    """
    glob_pattern = pattern.format(component=component)
    path = glob.glob(glob_pattern)
    if len(path) == 0:
        raise RuntimeError("No file found for component : {component}".format(component=component))
    elif len(path) > 1:
        raise RuntimeError("Ambiguous pattern: '{pattern}'".format(pattern=glob_pattern))
    return path[0]

def find_components(pattern):
    """Returns the list of components for a given pattern

    :param pattern: a filepath pattern to the list of components
    :returns: a list of components

    """
    out = pattern.rsplit("{component}", maxsplit=1)

    if len(out) == 1:
        prefix=""
        suffix=out[0]
    else:
        prefix=out[0]
        suffix=out[1]

    components = []
    for component in all_components:
        filepath = prefix+component+suffix
        if os.path.exists(filepath):
            components.append(component)
    return components

#    all_pattern = prefix+"*"+suffix
#    all_paths = glob.glob(all_pattern)
#
#    re_pattern = "(?<={prefix})([\w]*)(?={suffix})".format(prefix=prefix,suffix=suffix)
#
#    components = []
#    for file in all_paths:
#        omatch = re.search(re_pattern, file)
#        if omatch is not None:
#            components.append(omatch.group(0))
#    return components


