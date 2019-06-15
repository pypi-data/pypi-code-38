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

"""Channels information for a composite map."""

class CompositeChannels:
    """Channels information for a composite map."""
    def __init__(self, components, factors):
        """
        :param components: list of components (2 to 4, Red, Green, Blue and Gray in order)
        :param factors: list of scaling factors (same length as components)
        """
        if len(components) > 4 or len(components) <2:
            raise ValueError("Components must be a list of size 3 or 4")
        if len(components) != len(factors):
            raise ValueError("Components and factors must have the same size")
        self.components = components
        self.factors = factors

    @property
    def nb_components(self):
        """The number of components."""
        return len(self.components)

    @property
    def red(self):
        """The component of the red channel."""
        return self.components[0]
    @property
    def green(self):
        """The component of the green channel."""
        return self.components[1]
    @property
    def blue(self):
        """The component of the blue channel."""
        return self.components[2]
    @property
    def gray(self):
        """The component of the gray channel."""
        if self.nb_components==4:
            return self.components[3]
        else:
            return None

    @property
    def red_factor(self):
        """The scaling factor for the red channel."""
        return self.factors[0]
    @property
    def green_factor(self):
        """The scaling factor for the green channel."""
        return self.factors[1]
    @property
    def blue_factor(self):
        """The scaling factor for the blue channel."""
        return self.factors[2]
    @property
    def gray_factor(self):
        """The scaling factor for the gray channel."""
        if self.nb_components==4:
            return self.factors[3]
        else:
            return None
