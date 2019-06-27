#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools.common import regex
from sat.core import exceptions
from sat.core.constants import Const as C
import cPickle as pickle
import mimetypes
import os.path
import time

DEFAULT_EXT = ".raw"


class Cache(object):
    """generic file caching"""

    def __init__(self, host, profile):
        """
        @param profile(unicode, None): ame of the profile to set the cache for
            if None, the cache will be common for all profiles
        """
        self.profile = profile
        path_elts = [host.memory.getConfig("", "local_dir"), C.CACHE_DIR]
        if profile:
            path_elts.extend([u"profiles", regex.pathEscape(profile)])
        else:
            path_elts.append(u"common")
        self.cache_dir = os.path.join(*path_elts)

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def getPath(self, filename):
        """return cached file URL

        @param filename(unicode): cached file name (cache data or actual file)
        """
        if not filename or u"/" in filename:
            log.error(
                u"invalid char found in file name, hack attempt? name:{}".format(filename)
            )
            raise exceptions.DataError(u"Invalid char found")
        return os.path.join(self.cache_dir, filename)

    def getMetadata(self, uid):
        """retrieve metadata for cached data

        @param uid(unicode): unique identifier of file
        @return (dict, None): metadata with following keys:
            see [cacheData] for data details, an additional "path" key is the full path to cached file.
            None if file is not in cache (or cache is invalid)
        """

        uid = uid.strip()
        if not uid:
            raise exceptions.InternalError(u"uid must not be empty")
        cache_url = self.getPath(uid)
        if not os.path.exists(cache_url):
            return None

        try:
            with open(cache_url, "rb") as f:
                cache_data = pickle.load(f)
        except IOError:
            log.warning(u"can't read cache at {}".format(cache_url))
            return None
        except pickle.UnpicklingError:
            log.warning(u"invalid cache found at {}".format(cache_url))
            return None

        try:
            eol = cache_data["eol"]
        except KeyError:
            log.warning(u"no End Of Life found for cached file {}".format(uid))
            eol = 0
        if eol < time.time():
            log.debug(
                u"removing expired cache (expired for {}s)".format(time.time() - eol)
            )
            return None

        cache_data["path"] = self.getPath(cache_data["filename"])
        return cache_data

    def getFilePath(self, uid):
        """retrieve absolute path to file

        @param uid(unicode): unique identifier of file
        @return (unicode, None): absolute path to cached file
            None if file is not in cache (or cache is invalid)
        """
        metadata = self.getMetadata(uid)
        if metadata is not None:
            return metadata["path"]

    def cacheData(self, source, uid, mime_type=None, max_age=None, filename=None):
        """create cache metadata and file object to use for actual data

        @param source(unicode): source of the cache (should be plugin's import_name)
        @param uid(unicode): an identifier of the file which must be unique
        @param mime_type(unicode): MIME type of the file to cache
            it will be used notably to guess file extension
        @param max_age(int, None): maximum age in seconds
            the cache metadata will have an "eol" (end of life)
            None to use default value
            0 to ignore cache (file will be re-downloaded on each access)
        @param filename: if not None, will be used as filename
            else one will be generated from uid and guessed extension
        @return(file): file object opened in write mode
            you have to close it yourself (hint: use with statement)
        """
        cache_url = self.getPath(uid)
        if filename is None:
            if mime_type:
                ext = mimetypes.guess_extension(mime_type, strict=False)
                if ext is None:
                    log.warning(
                        u"can't find extension for MIME type {}".format(mime_type)
                    )
                    ext = DEFAULT_EXT
                elif ext == u".jpe":
                    ext = u".jpg"
            else:
                ext = DEFAULT_EXT
                mime_type = None
            filename = uid + ext
        if max_age is None:
            max_age = C.DEFAULT_MAX_AGE
        cache_data = {
            u"source": source,
            u"filename": filename,
            u"eol": int(time.time()) + max_age,
            u"mime_type": mime_type,
        }
        file_path = self.getPath(filename)

        with open(cache_url, "wb") as f:
            pickle.dump(cache_data, f, protocol=2)

        return open(file_path, "wb")
