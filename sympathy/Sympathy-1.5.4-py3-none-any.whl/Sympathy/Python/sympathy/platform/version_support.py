# Copyright (c) 2016-2017, Combine Control Systems AB
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
import os
import six
import sys
import json
import collections
import codecs
_fs_encoding = sys.getfilesystemencoding()
fs_encoding = _fs_encoding


def _fs_decode_list(list_):
    return [x.decode(_fs_encoding) for x in list_]


def _fs_encode_list(list_):
    return [x.encode(_fs_encoding) for x in list_]


class EncodedDictWrapper(object):
    def __init__(self, dict_):
        self._dict = dict_

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key):
        return self._dict[encode(key, _fs_encoding)].decode(_fs_encoding)

    def __setitem__(self, key, value):
        self._dict[encode(key, _fs_encoding)] = encode(value, _fs_encoding)

    def __delitem__(self, key):
        del self._dict[encode(key, _fs_encoding)]

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def keys(self):
        return _fs_decode_list(self._dict.keys())

    def values(self):
        return _fs_decode_list(self._dict.values())

    def items(self):
        return zip(self.keys(), self.values())

    def update(self, other):
        try:
            items = other.items()
        except AttributeError:
            items = other

        for key, value in items:
            self[key] = value


class EncodedListWrapper(object):
    def __init__(self, list_):
        self._list = list_

    def __getitem__(self, index):
        res = self._list[index]
        try:
            return res.decode(_fs_encoding)
        except AttributeError:
            # Assuming slice.
            return _fs_decode_list(res)

    def __setitem__(self, index, value):
        try:
            self._list[index] = value.encode(_fs_encoding)
        except AttributeError:
            # Assuming slice.
            self._list[index] = _fs_encode_list(value)

    def __iter__(self):
        for i in range(len(self._list)):
            yield self[i]

    def __len__(self):
        return len(self._list)

    def __delitem__(self, key):
        return self._list.__delitem__(key.decode(_fs_encoding))


if six.PY2:
    def environ_wrapper(environ=os.environ):
        return EncodedDictWrapper(environ)

    _environ = environ_wrapper()
    _argv = EncodedListWrapper(sys.argv)
    _path = EncodedListWrapper(sys.path)

    class OSWrapper(object):
        @property
        def environ(self):
            return _environ

    class SYSWrapper(object):
        @property
        def argv(self):
            return _argv

        @property
        def path(self):
            return _path

    OS = OSWrapper()
    SYS = SYSWrapper()
else:
    def environ_wrapper(environ=os.environ):
        return environ
    OS = os
    SYS = sys


def py_file(file_):
    if isinstance(file_, six.binary_type):
        file_ = file_.decode(_fs_encoding)
    return os.path.abspath(file_)


def py_file_dir(file_):
    return os.path.dirname(py_file(file_))


def encode(string, encoding):
    if isinstance(string, six.binary_type):
        return string
    return string.encode(encoding)


def decode(string, encoding):
    if isinstance(string, six.text_type):
        return string
    return string.decode(encoding)


def fs_encode(string):
    return encode(string, _fs_encoding)


def fs_decode(string):
    return decode(string, _fs_encoding)


def str_(string, encoding='ascii', errors='strict'):
    if isinstance(string, str):
        return string
    if six.PY2:
        return string.encode(encoding, errors)
    else:
        return string.decode(encoding, errors)


if six.PY3:
    _dict = {}
    _odict = collections.OrderedDict()
    _dict_iters = set(type(x) for x in [
        _dict.keys(), _dict.values(), _dict.items(),
        _odict.keys(), _odict.values(), _odict.items()])

    def dict_encoder(obj):
        if type(obj) in _dict_iters:
            return list(obj)
        return obj

    def json_dumps(*args, **kwargs):
        return json.dumps(*args, default=dict_encoder, **kwargs)
else:
    dict_encoder = None
    json_dumps = json.dumps


def samefile(filename1, filename2):
    if six.PY2 and sys.platform == 'win32':
        return (os.path.normcase(os.path.abspath(filename1)) ==
                os.path.normcase(os.path.abspath(filename2)))
    return os.path.samefile(filename1, filename2)


def deepcopy(obj):
    return json.loads(json_dumps(obj), object_hook=collections.OrderedDict)


def wrap_encode_std():
    """
    When running Python2, wrap stdout and stderr in codecs writers which
    encodes text before writing.
    """
    if six.PY2:
        writer = codecs.getwriter(fs_encoding)
        if sys.stdout and getattr(sys.stdout, 'encoding', None) is None:
            sys.stdout = writer(sys.stdout)
        if sys.stderr and getattr(sys.stderr, 'encoding', None) is None:
            sys.stderr = writer(sys.stderr)


if six.PY2 or sys.version_info.minor < 6:
    OrderedDict = collections.OrderedDict
else:
    # Python3.6 and forward should have ordered dict.
    OrderedDict = dict
