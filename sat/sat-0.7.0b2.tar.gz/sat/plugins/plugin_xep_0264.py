#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0264
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2014 Emmanuel Gil Peyrot (linkmauve@linkmauve.fr)

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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.internet import threads
from twisted.python.failure import Failure

from zope.interface import implements

from wokkel import disco, iwokkel

from sat.core import exceptions
import hashlib

try:
    from PIL import Image
except:
    raise exceptions.MissingModule(
        u"Missing module pillow, please download/install it from https://python-pillow.github.io"
    )

#  cf. https://stackoverflow.com/a/23575424
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler


MIME_TYPE = u"image/jpeg"
SAVE_FORMAT = u"JPEG"  # (cf. Pillow documentation)

NS_THUMBS = "urn:xmpp:thumbs:1"

PLUGIN_INFO = {
    C.PI_NAME: "XEP-0264",
    C.PI_IMPORT_NAME: "XEP-0264",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0264"],
    C.PI_DEPENDENCIES: ["XEP-0234"],
    C.PI_MAIN: "XEP_0264",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Thumbnails handling"""),
}


class XEP_0264(object):
    SIZE_SMALL = (250, 250)
    SIZE_MEDIUM = (1024, 1024)

    def __init__(self, host):
        log.info(_(u"Plugin XEP_0264 initialization"))
        self.host = host
        host.trigger.add("XEP-0234_buildFileElement", self._addFileThumbnails)
        host.trigger.add("XEP-0234_parseFileElement", self._getFileThumbnails)

    def getHandler(self, client):
        return XEP_0264_handler()

    ## triggers ##

    def _addFileThumbnails(self, file_elt, extra_args):
        try:
            thumbnails = extra_args[u"extra"][C.KEY_THUMBNAILS]
        except KeyError:
            return
        for thumbnail in thumbnails:
            thumbnail_elt = file_elt.addElement((NS_THUMBS, u"thumbnail"))
            thumbnail_elt["uri"] = u"cid:" + thumbnail["id"]
            thumbnail_elt["media-type"] = MIME_TYPE
            width, height = thumbnail["size"]
            thumbnail_elt["width"] = unicode(width)
            thumbnail_elt["height"] = unicode(height)
        return True

    def _getFileThumbnails(self, file_elt, file_data):
        thumbnails = []
        for thumbnail_elt in file_elt.elements(NS_THUMBS, u"thumbnail"):
            uri = thumbnail_elt["uri"]
            if uri.startswith("cid:"):
                thumbnail = {"id": uri[4:]}
            width = thumbnail_elt.getAttribute("width")
            height = thumbnail_elt.getAttribute("height")
            if width and height:
                try:
                    thumbnail["size"] = int(width), int(height)
                except ValueError:
                    pass
            try:
                thumbnail["mime_type"] = thumbnail_elt["media-type"]
            except KeyError:
                pass
            thumbnails.append(thumbnail)

        if thumbnails:
            file_data.setdefault("extra", {})[C.KEY_THUMBNAILS] = thumbnails
        return True

    ## thumbnails generation ##

    def getThumbId(self, image_uid, size):
        """return an ID unique for image/size combination

        @param image_uid(unicode): unique id of the image
            can be a hash
        @param size(tuple(int)): requested size of thumbnail
        @return (unicode): unique id for this image/size
        """
        return hashlib.sha256(repr((image_uid, size))).hexdigest()

    def _blockingGenThumb(self, source_path, size=None, max_age=None, image_uid=None):
        """Generate a thumbnail for image

        This is a blocking method and must be executed in a thread
        params are the same as for [generateThumbnail]
        """
        if size is None:
            size = self.SIZE_SMALL
        try:
            img = Image.open(source_path)
        except IOError:
            return Failure(exceptions.DataError(u"Can't open image"))

        img.thumbnail(size)
        uid = self.getThumbId(image_uid or source_path, size)

        with self.host.common_cache.cacheData(
            PLUGIN_INFO[C.PI_IMPORT_NAME], uid, MIME_TYPE, max_age
        ) as f:
            img.save(f, SAVE_FORMAT)

        return img.size, uid

    def generateThumbnail(self, source_path, size=None, max_age=None, image_uid=None):
        """Generate a thumbnail of image

        @param source_path(unicode): absolute path to source image
        @param size(int, None): max size of the thumbnail
            can be one of self.SIZE_*
            None to use default value (i.e. self.SIZE_SMALL)
        @param max_age(int, None): same as for [memory.cache.Cache.cacheData])
        @param image_uid(unicode, None): unique ID to identify the image
            use hash whenever possible
            if None, source_path will be used
        @return D(tuple[tuple[int,int], unicode]): tuple with:
            - size of the thumbnail
            - unique Id of the thumbnail
        """

        d = threads.deferToThread(
            self._blockingGenThumb, source_path, size, max_age, image_uid=image_uid
        )
        d.addErrback(
            lambda failure_: log.error(u"thumbnail generation error: {}".format(failure_))
        )
        return d


class XEP_0264_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_THUMBS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
