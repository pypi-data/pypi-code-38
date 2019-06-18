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

""" Module providing tools to parse and create valid urls and paths.

usage example:

When in fastr.config under the mounts section the data mount is set to /media/data, you will get the following.
.. code-block:: python

  >>> from fastr.data.url import get_path_from_url
  >>> get_path_from_url('vfs://data/temp/blaat1.png')
  '/media/data/temp/blaat1.png'
"""

import re
import os.path
import urllib.parse as up
import posixpath

from .. import resources
from fastr.exceptions import FastrUnknownURLSchemeError


def register_url_scheme(scheme):
    """ Register a custom scheme to behave http like. This is needed to parse
    all things properly.
    """
    for method in [s for s in dir(up) if s.startswith('uses_')]:
        getattr(up, method).append(scheme)


def get_url_scheme(url):
    """
    Get the schem of the url

    :param str url: url to extract scheme from
    :return: the url scheme
    :rtype: str
    """
    parsed_url = up.urlparse(str(url))
    return parsed_url.scheme


def get_path_from_url(url):
    """ Get the path to a file from a url.
    Currently supports the file:// and vfs:// scheme's

    Examples:

    .. code-block:: python

      >>> url.get_path_from_url('vfs://neurodata/user/project/file.ext')
      'Y:\\neuro3\\user\\project\\file.ext'


      >>> 'file:///d:/data/project/file.ext'
      'd:\\data\\project\\file.ext'

    .. warning::

      file:// will not function cross platform and is mainly for testing

    """
    # Translate properly depending on the scheme being used
    scheme = get_url_scheme(url)

    # Make the paths and vfs not go via ioplugins, but shortcut it
    if scheme == '':
        # This is not a URL, but a path, throw error
        raise FastrUnknownURLSchemeError('URL using no url scheme in {}, so it must be a path! '.format(url))
    elif scheme == 'vfs':
        # Directly call vfs
        return resources.ioplugins['vfs'].url_to_path(url)
    else:
        # Dispatch to ioplugin via the ioplugin manager
        try:
            ioplugin = resources.ioplugins[scheme]
        except KeyError:
            raise FastrUnknownURLSchemeError('URL using an unknown scheme in {}'
                                             ' ({} not in {})'.format(url,
                                                                      scheme,
                                                                      list(resources.ioplugins.keys())))

        return ioplugin.url_to_path(url)


def isurl(string):
    """
    Check if string is a valid url

    :param str string: potential url
    :return: flag indicating if string is a valid url
    """
    if not isinstance(string, str):
        return False

    parsed_url = up.urlparse(str(string))
    return len(parsed_url.scheme) > 1


def basename(url):
    """
    Get basename of url

    :param str url: the url
    :return: the basename of the path in the url
    """
    parsed_url = up.urlparse(str(url))
    return posixpath.basename(parsed_url.path)


def dirname(url):
    """
    Get the dirname of the url

    :param str url: the url
    :return: the dirname of the path in the url
    """
    parsed_url = up.urlparse(str(url))
    return posixpath.dirname(parsed_url.path)


def dirurl(url):
    """
    Get the a new url only having the dirname as the path

    :param str url: the url
    :return: the modified url with only dirname as path
    """
    return split(url)[0]


def split(url):
    """
    Split a url in a url with the dirname and the basename part of the path of
    the url

    :param str url: the url
    :return: a tuple with (dirname_url, basename)
    """
    # pylint: disable=protected-access
    parsed_url = up.urlparse(str(url))._asdict()
    parsed_url['path'], part = posixpath.split(parsed_url['path'])
    return up.urlunparse(list(parsed_url.values())), part


def join(url, *p):
    """
    Join the path in the url with p

    :param str url: the base url to join with
    :param p: additional parts of the path
    :return: the url with the parts added to the path
    """
    # pylint: disable=protected-access
    parsed_url = up.urlparse(str(url))._asdict()
    parsed_url['path'] = posixpath.join(parsed_url['path'], *p)
    return up.urlunparse(list(parsed_url.values()))


def normurl(url):
    """
    Normalized the path of the url

    :param str url: the url
    :return: the normalized url
    """
    # pylint: disable=protected-access
    parsed_url = up.urlparse(str(url))._asdict()
    parsed_url['path'] = posixpath.normpath(parsed_url['path'])
    return up.urlunparse(list(parsed_url.values()))


def create_vfs_url(mountpoint, path):
    """
    Construct an url from a given mount point and a relative path to the mount point.

    :param str mountpoint: the name of the mountpoint
    :param str path: relative path from the mountpoint
    :return: the created vfs url
    """
    return "vfs://%s/%s" % (mountpoint, path.strip('/'))


def full_split(urlpath):
    """
    Split the path in the url in a list of parts

    :param urlpath: the url path
    :return: a list of parts
    """
    parts = []
    while True:
        newpath, tail = posixpath.split(urlpath)
        if newpath == urlpath:
            assert not tail
            if urlpath:
                parts.append(urlpath)
            break
        parts.append(tail)
        urlpath = newpath
    parts.reverse()
    return parts


def _correct_separators(path):
    """
    Translates the URL seperator '/' into the apropriate seperator for the OS

    :param str path: the path to correct
    :return: path with consistent separators
    """
    return re.sub('/', ('%r' % os.path.sep).strip("'"), path.strip('/'))
