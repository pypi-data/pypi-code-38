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

# When adding a new editor, also add it to gui/create_editor.
# Also add to dict in layers.py


class Base(object):
    """Base object for other editors to inherit."""

    def __init__(self, *args, **kwargs):
        self.options = lambda: None
        self.property_object = None
        self.value_range = None
        self.tags = set()
        self.get = lambda: self.property_object.get()
        self.set = lambda x: self.property_object.set(x)

    def init(self):
        pass


class String(Base):
    """String editor."""

    pass


class MultiLineString(Base):
    """Multi line string editor."""

    pass


class DataSource(Base):
    """Editor for choosing data source."""

    pass


class Integer(Base):
    """Integer editor."""

    pass


class Float(Base):
    """Float editor."""

    pass


class Color(Base):
    """Color editor."""

    pass


class Boolean(Base):
    """Boolean editor."""

    pass


class ImmutableList(Base):
    """Immutable list editor using ComboBox."""

    current_index = 0

    def __init__(self, options_function):
        super(ImmutableList, self).__init__(options_function)
        # The options are always fetched using a function.
        assert hasattr(options_function, '__call__')
        self.options = options_function

        # We need to update current_index as well when setting the value
        def new_setter(x):
            self._old_setter(x)
            self.init()
        self._old_setter = self.set
        self.set = new_setter

    def init(self):
        # Initialize index for combo box. Fallback on zero.
        try:
            self.current_index = self.options().index(self.get())
        except (AttributeError, ValueError):
            self.current_index = -1


class ColorScale(Base):
    """Select a color scale using ComboBox."""

    pass


class Image(Base):
    """Select an image using a file selector."""

    pass


class EditorTags(object):
    """Tags for giving editors different properties."""

    force_update_after_edit = 0,
    force_rebuild_after_edit = 1
