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
This module contains the FileSystem plugin for fastr
"""

import os
import shutil
import urllib.parse
import fastr
from fastr import exceptions
from fastr.core.ioplugin import IOPlugin


class FileSystem(IOPlugin):
    """
    The FileSystem plugin is create to handle ``file://`` type or URLs. This is
    generally not a good practice, as this is not portable over between
    machines. However, for test purposes it might be useful.

    The URL scheme is rather simple: ``file://host/path``
    (see `wikipedia <http://en.wikipedia.org/wiki/File_URI_scheme>`_ for details)

    We do not make use of the ``host`` part and at the moment only support
    localhost (just leave the host empty) leading to ``file:///`` URLs.

    .. warning:: This plugin ignores the hostname in the URL and does only
                 accept driver letters on Windows in the form ``c:/``
    """
    scheme = 'file'

    def __init__(self):
        # initialize the instance and register the scheme
        super(FileSystem, self).__init__()

    def url_to_path(self, url):
        """ Get the path to a file from a url.
        Currently supports the file:// scheme

        Examples:

        .. code-block:: python

          >>> 'file:///d:/data/project/file.ext'
          'd:\\data\\project\\file.ext'

        .. warning::

          file:// will not function cross platform and is mainly for testing

        """
        parsed_url = up.urlparse(str(url))

        # Translate properly depending on the scheme being used
        if parsed_url.scheme == self.scheme:
            if os.name == 'nt':
                path = parsed_url.path.lstrip('/')
            else:
                path = parsed_url.path

            return self._correct_separators(path)
            # return o.path
        else:
            raise exceptions.FastrValueError('This parses the {} scheme and not the {} scheme!'.format(self.scheme,
                                                                                                       parsed_url.scheme))

    def path_to_url(self, path, mountpoint=None):
        """ Construct an url from a given mount point and a relative path to the mount point. """
        return "{scheme}:///{path}".format(scheme=self.scheme, path=path)

    def fetch_url(self, inurl, outpath):
        """
        Fetch the files from the file.

        :param inurl: url to the item in the data store, starts with ``file://``
        :param outpath: path where to store the fetch data locally
        """
        inpath = self.url_to_path(inurl)

        # Clear away present data
        if os.path.exists(outpath):
            fastr.log.info('Removing currently exists data at {}'.format(outpath))
            if os.path.islink(outpath):
                os.remove(outpath)
            elif os.path.isdir(outpath):
                shutil.rmtree(outpath)
            else:
                os.remove(outpath)

        try:
            os.symlink(inpath, outpath)
            fastr.log.debug('Symlink successful')
        except OSError:
            fastr.log.debug('Cannot symlink, fallback to copy')
            if os.path.isdir(inpath):
                shutil.copytree(inpath, outpath)
            else:
                shutil.copy2(inpath, outpath)

        return outpath

    def fetch_value(self, inurl):
        """
        Fetch a value from an external file file.

        :param inurl: url of the value to read
        :return: the fetched value
        """
        path = self.url_to_path(inurl)
        with open(path, 'r') as file_handle:
            data = file_handle.read()

        return data

    def put_url(self, inpath, outurl):
        """
        Put the files to the external data store.

        :param inpath: path of the local data
        :param outurl: url to where to store the data, starts with ``file://``
        """
        outpath = self.url_to_path(outurl)
        fastr.vfs.copy_file_dir(inpath, outpath)
        return os.path.exists(outpath)

    def put_value(self, value, outurl):
        """
        Put the value in the external data store.

        :param value: value to store
        :param outurl: url to where to store the data, starts with ``file://``
        """
        outpath = self.url_to_path(outurl)

        with open(outpath, 'w') as file_handle:
            file_handle.write(str(value))

        return os.path.exists(outpath)
