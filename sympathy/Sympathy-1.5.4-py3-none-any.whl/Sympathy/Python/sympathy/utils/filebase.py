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
"""
Utility functions needed to read and write tables from/to different
formats.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import six

from .. datasources.info import (get_fileinfo_from_scheme,
                                 get_scheme_from_file)
from .. types.types import (from_string_alias, from_type_expand,
                            from_string_expand)
from .. types import sylist
from .. types.types import manager as type_manager
from .. types.factory import typefactory
from .. types import types
from . import port as port_util
from .. platform import exceptions


class PPrintUnicode(object):
    """
    Base class for pretty printing in IPython.

    Any subclass will be printed with unicode(obj) instead of the default
    repr(obj) when they are the result of an expression in IPython. This allows
    for higher interactivity when working in IPython.
    """
    def _repr_mimebundle_(self, include=None, exclude=None):
        """
        For ipython integration, determines how values of this type are written
        to the console.

        Can be customized in subclasses and can be used to add support for
        other kinds of output such as text/html.
        """
        return {'text/plain': six.text_type(self)}


def typeutil(typealias):
    def inner(cls):
        declaration = from_string_alias(typealias)
        cls.container_type = declaration
        type_manager.set_typealias_util(declaration.name(), cls)
        return cls
    return inner


def from_file(filename, scheme=None, sytype=None, external=True):
    link = not external

    if scheme is None:
        scheme = get_scheme_from_file(filename)

    if scheme is None:
        return None

    fileinfo_ = fileinfo(filename, scheme)

    if sytype is None:
        sytype = fileinfo_.type()

    return port_util.port_maker(
        {'file': filename, 'scheme': scheme,
         'type': sytype}, 'r', link, True)


def to_file(filename, scheme, sytype, external=True):
    link = not external

    return port_util.port_maker(
        {'file': filename, 'scheme': scheme,
         'type': sytype}, 'w', link, True)


def from_type(sytype):
    return typefactory.from_type(sytype)


def empty_from_type(sytype):
    return typefactory.from_type(sytype)


def fileinfo(filename, scheme=None):
    if scheme is None:
        scheme = get_scheme_from_file(filename)

    return get_fileinfo_from_scheme(scheme)(filename)


def filetype(filename):
    try:
        fileinfo_ = fileinfo(filename)
        return fileinfo_.type()
    except:
        pass


def is_type(sytype, filename, scheme='hdf5'):
    info = fileinfo(filename, scheme)
    try:
        return fileinfo.type() == str(sytype)
    except (KeyError, AttributeError, TypeError):
        pass
    try:
        return (str(from_string_expand(info.datatype())) ==
                str(from_type_expand(sytype)))
    except TypeError:
        return False


class FileManager(PPrintUnicode):
    """FileManager handles data contexts for File and FileList."""
    container_type = None
    ELEMENT = None

    def __init__(self, fileobj, data, filename, mode, scheme,
                 import_links=False):
        """
        Fileobj is a file owned. It should be closed by self.
        Data is a borrowed file. It shall not be closed by self.
        Filename is used to construct a new fileobj.
        Mode and scheme are used together with filename to construct
        the filename.
        Import_links is only usable together with filename and enables links
        to the file source to be written.

        Fileobj, data and filename are mutually exclusive.
        """
        if filename is not None:
            if mode not in ['r', 'w']:
                raise AssertionError(
                    "Supported values for mode are: 'r' and 'w', but '{}'"
                    " was given.".format(mode))
        self._data = data
        self.__fileobj = fileobj

        if fileobj is not None:
            self._data = fileobj
        elif data is not None:
            pass
        elif filename is not None:
            if mode == 'w' and import_links:
                exceptions.sywarn(
                    "Argument: 'import_links' must be False for mode 'w'.")
                import_links = False

            self.__fileobj = open_file(
                filename=filename, mode=mode, external=not import_links,
                sytype=self.container_type, scheme='hdf5')
            self._data = self.__fileobj
        else:
            self._data = typefactory.from_type(self.container_type)._data

        if isinstance(self._data, type(self)):
            # TODO(erik): Handle per case above, not for all cases at once.
            # Avoiding double wrapping with non-managed nodes.
            self._data = self._data._data

    def _copy_base(self):
        cls = type(self)
        obj = cls.__new__(cls)
        obj._data = self._data
        obj.__fileobj = self.__fileobj
        return obj

    def __copy__(self):
        return self._copy_base()

    def __deepcopy__(self, memo=None):
        obj = self._copy_base()
        obj._data = self._data.__deepcopy__()
        return obj

    def writeback(self):
        self._data.writeback()

    def sync(self):
        pass

    def _writeback(self, datasource, link=None):
        self.sync()
        return self._data._writeback(datasource, link)

    @classmethod
    def is_type(cls, filename, scheme='hdf5'):
        return is_type(cls.container_type, filename, scheme)

    @staticmethod
    def is_valid():
        return True

    def close(self):
        """Close the referenced data file."""
        # TODO(erik): Handle ownership on close.
        self.sync()
        if self.__fileobj is not None:
            self.__fileobj.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FileBase(FileManager):
    """File represents the top level of a table"""
    container_type = None

    def __init__(self, fileobj=None, data=None, filename=None, mode='r',
                 scheme='hdf5', source=None, managed=False,
                 import_links=False):
        if filename is not None and mode is None:
            mode = 'r'
        super(FileBase, self).__init__(fileobj, data, filename, mode, scheme,
                                       import_links=import_links)
        self._extra_init(fileobj, data, filename, mode, scheme, source)

    def _extra_init(self, fileobj, data, filename, mode, scheme, source):
        if source:
            self.source(source)
        else:
            self.init()

    def init(self):
        pass

    def source(self, other, shallow=False):
        """
        Update self with a deepcopy of the data from other, without keeping the
        old state.

        self and other must be of the exact same type.
        """
        self._data.source(other._data, shallow=shallow)


class TypeAlias(FileBase):
    container_type = None

    @classmethod
    def port(cls, description, name=None, **kwargs):
        """
        Return a new port for cls.
        """
        return port_util.CustomPort(
            cls.container_type.name(), description, name=name, **kwargs)

    @classmethod
    def viewer(cls):
        """
        Return viewer class, which must be a subclass of
        sympathy.api.typeutil.ViewerBase
        """
        return None

    @classmethod
    def icon(cls):
        """
        Return full path to svg icon.
        """
        return None

    def names(self, kind=None, **kwargs):
        """
        Return relevant names.
        Useful if this type has some kind of names that would be
        useful in adjust_parameters.
        """
        return []

    def types(self, kind=None, **kwargs):
        """
        Return types associated with names().
        """
        return []

    def init(self):
        """
        Perform any initialization, such as, defining local fields.
        """
        pass

    def source(self, other, shallow=False):
        """
        Update self with the data from other, without keeping the
        old state. When shallow is False (default), self should be
        updated with a deepcopy of other.

        self and other must be of the exact same type.
        """
        raise NotImplementedError

    def sync(self):
        """
        Synchronize data fields that are kept in memory against self._data.

        Called before data is written to disk and must be re-implemented by
        subclasses that define custom storage fields.
        """
        pass

    def __deepcopy__(self, memo=None):
        """
        Return new TypeAlias that does not share references with self.
        Must be re-implemented by subclasses that define their own storage
        fields.
        """
        return super(TypeAlias, self).__deepcopy__()


@six.python_2_unicode_compatible
class FileListBase(sylist, PPrintUnicode):
    """FileList represents a list of Files."""
    sytype = None  # str.
    scheme = None  # str.

    def __new__(cls, filename=None, mode='r', import_links=False):

        if mode == 'w' and import_links:
            exceptions.sywarn(
                "Argument: 'import_links' must be False for mode 'w'.")
            import_links = False

        fileobj = open_file(filename=filename, mode=mode,
                            external=not import_links,
                            sytype=types.from_string(cls.sytype),
                            scheme=cls.scheme)
        obj = fileobj
        obj.__class__ = cls
        obj._fileobj = fileobj
        return obj

    def __init__(self, filename=None, mode='r'):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        super(FileListBase, self).close()

    def is_type(self, filename, scheme=None):
        return is_type(types.from_string(self.sytype), filename, scheme)

    def set_read_through(self):
        exceptions.sywarn('set_read_through is not implemented.')

    def set_write_through(self):
        exceptions.sywarn('set_write_through is not implemented.')

    def is_read_through(self):
        return False

    def is_write_through(self):
        return False

    def __str__(self):
        repr_line = repr(self)
        elements_str = "  {} element{}".format(
            len(self), "s" if len(self) != 1 else u"")
        return repr_line + ":\n" + elements_str

    def __copy__(self):
        obj = super(FileListBase, self).__copy__()
        obj._fileobj = self._fileobj
        return obj

    def __deepcopy__(self, memo=None):
        obj = super(FileListBase, self).__deepcopy__()
        obj._fileobj = self._fileobj
        return obj

    def __repr__(self):
        mode = 'Buffered '
        id_ = hex(id(self))
        return "<{}FileList object at {}>".format(mode, id_)


def open_file(filename=None, mode='r', external=True, sytype=None,
              scheme='hdf5'):
    fileobj = None
    assert mode in 'rw', "Mode should be 'r' or 'w'"

    if filename is not None:
        if mode == 'r':
            fileobj = from_file(
                filename, external=external, sytype=sytype)
        elif mode == 'w':
            assert sytype is not None, "Mode 'w' requires sytype"
            assert scheme is not None, "Mode 'w' requires scheme"
            fileobj = to_file(filename, scheme, sytype, external=external)

    else:
        fileobj = from_type(sytype)
    return fileobj
