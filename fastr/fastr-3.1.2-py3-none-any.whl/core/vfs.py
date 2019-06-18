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

import os
import urllib.parse
import shutil
import fastr
import fastr.data.url
import errno

from .. import exceptions
from ..abc.baseplugin import PluginState


class VirtualFileSystem:
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

    _status = (PluginState.loaded, '')
    abstract = False

    def __init__(self):
        """
        Instantiate the VFS plugin

        :return: the VirtualFileSysten plugin
        """
        self.filename = __file__
        super(VirtualFileSystem, self).__init__()

    @property
    def scheme(self):
        return 'vfs'

    def setup(self):
        """
        The plugin setup, does nothing but needs to be implemented
        """
        pass

    def fetch_url(self, inurl, outpath):
        """
        Fetch the files from the vfs.

        :param inurl: url to the item in the data store, starts with ``vfs://``
        :param outpath: path where to store the fetch data locally

        """
        inpath = self.url_to_path(inurl)

        # Clear away present data
        if os.path.exists(outpath):
            fastr.log.info('Removing currently exists data at {}'.format(outpath))
            if os.path.isdir(outpath) and not os.path.islink(outpath):
                shutil.rmtree(outpath)
            else:
                os.remove(outpath)

        if not os.path.exists(inpath):
            raise exceptions.FastrValueError(
                'Path of the url to fetch ({}) does not point to a file or directory! ({} does not exist)'.format(
                    inurl,
                    inpath
                )
            )

        try:
            os.symlink(inpath, outpath)
            fastr.log.debug('Symlink successful')
        except (OSError, AttributeError):
            fastr.log.debug('Cannot symlink, fallback to copy')
            self.copy_file_dir(inpath, outpath)

        return outpath

    def fetch_value(self, inurl):
        """
        Fetch a value from an external vfs file.

        :param inurl: url of the value to read
        :return: the fetched value
        """
        path = self.url_to_path(inurl)
        with open(path, 'r') as file_handle:
            data = file_handle.read().strip()

        return data

    def put_url(self, inpath, outurl):
        """
        Put the files to the external data store.

        :param inpath: path of the local data
        :param outurl: url to where to store the data, starts with ``vfs://``
        """
        outpath = self.url_to_path(outurl)
        outdir = os.path.dirname(outpath)

        # Make sure the directory in which the out has to be placed exists or is created
        os.makedirs(outdir, exist_ok=True)

        self.copy_file_dir(inpath, outpath)
        return os.path.exists(outpath)

    def put_value(self, value, outurl):
        """
        Put the value in the external data store.

        :param value: value to store
        :param outurl: url to where to store the data, starts with ``vfs://``
        """
        outpath = self.url_to_path(outurl)
        outdir = os.path.dirname(outpath)

        # Make sure the out directory exists or is created
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        with open(outpath, 'w') as file_handle:
            file_handle.write(str(value))

        return os.path.exists(outpath)

    def expand_url(self, url):
        """
        Try to expand the url. For vfs with will return the original url.

        :param url: url to expand
        :return: the expanded url (same as url)
        """
        if fastr.data.url.get_url_scheme(url) != 'vfs':
            raise exceptions.FastrValueError('URL not of vfs type! (Found {})'.format(url))

        return url

    def url_to_path(self, url, scheme=None):
        """
        Get the path to a file from a vfs url

        :param str url: url to get the path for
        :return: the matching path
        :rtype: str
        :raises FastrMountUnknownError: if the mount in url is unknown
        :raises FastrUnknownURLSchemeError: if the url scheme is not correct

        Example (the mountpoint tmp points to /tmp):

        .. code-block:: python

          >>> fastr.vfs.url_to_path('vfs://tmp/file.ext')
          '/tmp/file.ext'

        """
        parsed_url = urllib.parse.urlparse(str(url))

        if scheme is None:
            scheme = self.scheme

        # Translate properly depending on the scheme being used
        if parsed_url.scheme == scheme:
            try:
                return os.path.join(fastr.config.mounts[parsed_url.netloc.lower()],
                                    self._correct_separators(parsed_url.path.lstrip('/')))
            except KeyError:
                raise exceptions.FastrMountUnknownError(
                    "The mount '{}' does not exists in url: {}. Available mounts: {}".format(
                        parsed_url.netloc,
                        url,
                        ", ".join(fastr.config.mounts.keys())
                    )
                )
        else:
            raise exceptions.FastrUnknownURLSchemeError(
                'URL using an unknown scheme ({}) found in {}!'.format(parsed_url.scheme, url)
            )

    def path_to_url(self, path, mountpoint=None, scheme=None):
        """
        Construct an url from a given mount point and a relative path to the mount point.

        :param str path: the path to find the url for
        :mountpoint str: mountpoint the url should be under
        :return: url of the
        """
        if scheme is None:
            scheme = self.scheme

        abspath = os.path.abspath(os.path.expanduser(path))

        # This will allow a path to match a mount even if there is no further
        # sub-path involved
        if os.path.isdir(abspath):
            abspath += os.path.sep

        if mountpoint is None:
            # We get the mount that matches most of the path
            options = {k: v for k, v in list(fastr.config.mounts.items())
                       if abspath.startswith(v.rstrip(os.path.sep) + os.path.sep)}
            if len(options) == 0:
                raise exceptions.FastrMountUnknownError(
                    "Mountpath for {} cannot be found in config.mounts".format(abspath)
                )

            # Sort by length of path matched
            options = sorted(options.items(), key=lambda x: len(x[1]))
            # Pick the longest option
            mountpoint = options[-1][0]

        mount_path = fastr.config.mounts[mountpoint]
        if not abspath.startswith(mount_path):
            raise exceptions.FastrValueError('Path is not contained in the mount {} ({})'.format(mountpoint,
                                                                                                 mount_path))

        # Strip both start / from abspath as possible ending / of a directory
        path = abspath.replace(mount_path, "", 1).strip(os.path.sep)

        return "{scheme}://{mnt}/{path}".format(scheme=scheme, mnt=mountpoint, path=path)

    @staticmethod
    def copy_file_dir(inpath, outpath):
        """
        Helper function, copies a file or directory not caring what the inpath
        actually is

        :param inpath: path of the things to be copied
        :param outpath: path of the destination
        :return: the result of shutil.copy2 or shutil.copytree (depending on
                 inpath pointing to a file or directory)
        """
        if os.path.isfile(inpath):
            return shutil.copy2(inpath, outpath)
        elif os.path.isdir(inpath):
            return shutil.copytree(inpath, outpath, symlinks=True)
        else:
            raise exceptions.FastrValueError('Cannot copy {}, not a valid file or directory!'.format(inpath))

    @staticmethod
    def _correct_separators(path):
        """
        Translates the URL seperator '/' into the apropriate seperator for the OS

        :param str path: the path to correct
        :return: path with corrected separators
        :rtype: str
        """
        return path.replace('/', os.path.sep)
