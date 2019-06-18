# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the virtual file system code. This is internally
used object as used as base class for the IOPlugin.
"""

from fastr.core.vfs import VirtualFileSystem
from fastr.core.ioplugin import IOPlugin


class VirtualFileSystem(VirtualFileSystem, IOPlugin):
    """
    The virtual file system class. This is an IOPlugin, but also heavily used
    internally in fastr for working with directories. The VirtualFileSystem
    uses the ``vfs://`` url scheme.

    A typical virtual filesystem url is formatted as ``vfs://mountpoint/relative/dir/from/mount.ext``

    Where the ``mountpoint`` is defined in the :ref:`config-file`. A list of
    the currently known mountpoints can be found in the ``fastr.config`` object

    .. code-block:: python

        >>> fastr.config.mounts
        {'example_data': '/home/username/fastr-feature-documentation/fastr/fastr/examples/data',
         'home': '/home/username/',
         'tmp': '/home/username/FastrTemp'}

    This shows that a url with the mount ``home`` such as
    ``vfs://home/tempdir/testfile.txt`` would be translated into
    ``/home/username/tempdir/testfile.txt``.

    There are a few default mount points defined by Fastr (that can be changed
    via the config file).

    +--------------+-----------------------------------------------------------------------------+
    | mountpoint   | default location                                                            |
    +==============+=============================================================================+
    | home         | the users home directory (:py:func:`expanduser('~/') <os.path.expanduser>`) |
    +--------------+-----------------------------------------------------------------------------+
    | tmp          | the fastr temprorary dir, defaults to ``tempfile.gettempdir()``             |
    +--------------+-----------------------------------------------------------------------------+
    | example_data | the fastr example data directory, defaults ``$FASTRDIR/example/data``       |
    +--------------+-----------------------------------------------------------------------------+

    """
    scheme = 'vfs'
