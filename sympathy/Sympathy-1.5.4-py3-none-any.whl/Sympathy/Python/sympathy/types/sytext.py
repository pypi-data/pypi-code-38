# Copyright (c) 2013, Combine Control Systems AB
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
"""Sympathy text."""
import six
from . import sybase
from . sytable import sytable
from . types import TypeTable
from . import exception as exc


class sytext(sybase.sygroup):
    """A type representing a text."""
    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        """
        Init. container_type parameter is not used, needed to
        conform factory interface.
        """
        self.__table = sytable(TypeTable())
        super(sytext, self).__init__(container_type,
                                     datasource or sybase.NULL_SOURCE)
        self._cache = (None, False)

    def get(self):
        """Get contained text."""
        value = self._cache[0]
        if value is None:
            value = self._datasource.read()
            self._cache = (value, False)
        return value

    def set(self, text):
        """Set contained text."""
        assert(isinstance(text, six.text_type) or
               isinstance(text, six.binary_type))
        self._cache = (text or "", True)

    def update(self, other):
        """Updates the text with other text if it exists."""
        self.set(other.get())

    def __copy__(self):
        obj = super(sytext, self).__copy__()
        obj.__table = self.__table.__copy__()
        obj._cache = tuple(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        return self.__copy__()

    def source(self, other, shallow=False):
        self.update(other)

    def visit(self, group_visitor):
        """Accept group visitor."""
        group_visitor.visit_text(self)

    def writeback(self):
        super(sytext, self).writeback()

    def _writeback(self, datasource, link=None):
        # Transfer relies on direct compatiblity, for example, in the hdf5
        # datasource case both sources need to be hdf5 and the source needs to
        # be read only.
        origin = self._datasource
        target = datasource
        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)

        if link:
            return self._link(datasource, link)

        shares_origin = target.shares_origin(origin)
        value, dirty = self._cache

        if shares_origin and not dirty:
            # At this point there is no support for writing texts more than
            # once.
            return

        if target.transferable(origin) and not dirty:
            target.transfer(
                None, origin, None)
        else:
            # No transfer possible, writing using numpy texts.
            if value is None:
                value = self.get()

            if value is not None:
                target.write(value)

    def __repr__(self):
        return "sytext()"
