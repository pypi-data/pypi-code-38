#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for import external blogs
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from sat.tools.common import data_format
from twisted.internet import threads
from collections import OrderedDict
import itertools
import time
import cgi
import os.path


PLUGIN_INFO = {
    C.PI_NAME: "Dotclear import",
    C.PI_IMPORT_NAME: "IMPORT_DOTCLEAR",
    C.PI_TYPE: C.PLUG_TYPE_BLOG,
    C.PI_DEPENDENCIES: ["BLOG_IMPORT"],
    C.PI_MAIN: "DotclearImport",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Blog importer for Dotclear blog engine."""),
}

SHORT_DESC = D_(u"import posts from Dotclear blog engine")

LONG_DESC = D_(
    u"""This importer handle Dotclear blog engine.

To use it, you'll need to export your blog to a flat file.
You must go in your admin interface and select Plugins/Maintenance then Backup.
Export only one blog if you have many, i.e. select "Download database of current blog"
Depending on your configuration, your may need to use Import/Export plugin and export as a flat file.

location: you must use the absolute path to your backup for the location parameter
"""
)
POST_ID_PREFIX = u"sat_dc_"
KNOWN_DATA_TYPES = (
    "link",
    "setting",
    "post",
    "meta",
    "media",
    "post_media",
    "comment",
    "captcha",
)
ESCAPE_MAP = {"r": u"\r", "n": u"\n", '"': u'"', "\\": u"\\"}


class DotclearParser(object):
    # XXX: we have to parse all file to build data
    #      this can be ressource intensive on huge blogs

    def __init__(self):
        self.posts_data = OrderedDict()
        self.tags = {}

    def getPostId(self, post):
        """Return a unique and constant post id

        @param post(dict): parsed post data
        @return (unicode): post unique item id
        """
        return u"{}_{}_{}_{}:{}".format(
            POST_ID_PREFIX,
            post["blog_id"],
            post["user_id"],
            post["post_id"],
            post["post_url"],
        )

    def getCommentId(self, comment):
        """Return a unique and constant comment id

        @param comment(dict): parsed comment
        @return (unicode): comment unique comment id
        """
        post_id = comment["post_id"]
        parent_item_id = self.posts_data[post_id]["blog"]["id"]
        return u"{}_comment_{}".format(parent_item_id, comment["comment_id"])

    def getTime(self, data, key):
        """Parse time as given by dotclear, with timezone handling

        @param data(dict): dotclear data (post or comment)
        @param key(unicode): key to get (e.g. "post_creadt")
        @return (float): Unix time
        """
        return time.mktime(time.strptime(data[key], "%Y-%m-%d %H:%M:%S"))

    def readFields(self, fields_data):
        buf = []
        idx = 0
        while True:
            if fields_data[idx] != '"':
                raise exceptions.ParsingError
            while True:
                idx += 1
                try:
                    char = fields_data[idx]
                except IndexError:
                    raise exceptions.ParsingError("Data was expected")
                if char == '"':
                    # we have reached the end of this field,
                    # we try to parse a new one
                    yield u"".join(buf)
                    buf = []
                    idx += 1
                    try:
                        separator = fields_data[idx]
                    except IndexError:
                        return
                    if separator != u",":
                        raise exceptions.ParsingError("Field separator was expeceted")
                    idx += 1
                    break  # we have a new field
                elif char == u"\\":
                    idx += 1
                    try:
                        char = ESCAPE_MAP[fields_data[idx]]
                    except IndexError:
                        raise exceptions.ParsingError("Escaped char was expected")
                    except KeyError:
                        char = fields_data[idx]
                        log.warning(u"Unknown key to escape: {}".format(char))
                buf.append(char)

    def parseFields(self, headers, data):
        return dict(itertools.izip(headers, self.readFields(data)))

    def postHandler(self, headers, data, index):
        post = self.parseFields(headers, data)
        log.debug(u"({}) post found: {}".format(index, post["post_title"]))
        mb_data = {
            "id": self.getPostId(post),
            "published": self.getTime(post, "post_creadt"),
            "updated": self.getTime(post, "post_upddt"),
            "author": post["user_id"],  # there use info are not in the archive
            # TODO: option to specify user info
            "content_xhtml": u"{}{}".format(
                post["post_content_xhtml"], post["post_excerpt_xhtml"]
            ),
            "title": post["post_title"],
            "allow_comments": C.boolConst(bool(int(post["post_open_comment"]))),
        }
        self.posts_data[post["post_id"]] = {
            "blog": mb_data,
            "comments": [[]],
            "url": u"/post/{}".format(post["post_url"]),
        }

    def metaHandler(self, headers, data, index):
        meta = self.parseFields(headers, data)
        if meta["meta_type"] == "tag":
            tags = self.tags.setdefault(meta["post_id"], set())
            tags.add(meta["meta_id"])

    def metaFinishedHandler(self):
        for post_id, tags in self.tags.iteritems():
            data_format.iter2dict("tag", tags, self.posts_data[post_id]["blog"])
        del self.tags

    def commentHandler(self, headers, data, index):
        comment = self.parseFields(headers, data)
        if comment["comment_site"]:
            # we don't use atom:uri because it's used for jid in XMPP
            content = u'{}\n<hr>\n<a href="{}">author website</a>'.format(
                comment["comment_content"],
                cgi.escape(comment["comment_site"]).replace('"', u"%22"),
            )
        else:
            content = comment["comment_content"]
        mb_data = {
            "id": self.getCommentId(comment),
            "published": self.getTime(comment, "comment_dt"),
            "updated": self.getTime(comment, "comment_upddt"),
            "author": comment["comment_author"],
            # we don't keep email addresses to avoid the author to be spammed
            # (they would be available publicly else)
            # 'author_email': comment['comment_email'],
            "content_xhtml": content,
        }
        self.posts_data[comment["post_id"]]["comments"][0].append(
            {"blog": mb_data, "comments": [[]]}
        )

    def parse(self, db_path):
        with open(db_path) as f:
            signature = f.readline().decode("utf-8")
            try:
                version = signature.split("|")[1]
            except IndexError:
                version = None
            log.debug(u"Dotclear version: {}".format(version))
            data_type = None
            data_headers = None
            index = None
            while True:
                buf = f.readline().decode("utf-8")
                if not buf:
                    break
                if buf.startswith("["):
                    header = buf.split(" ", 1)
                    data_type = header[0][1:]
                    if data_type not in KNOWN_DATA_TYPES:
                        log.warning(u"unkown data type: {}".format(data_type))
                    index = 0
                    try:
                        data_headers = header[1].split(",")
                        # we need to remove the ']' from the last header
                        last_header = data_headers[-1]
                        data_headers[-1] = last_header[: last_header.rfind("]")]
                    except IndexError:
                        log.warning(u"Can't read data)")
                else:
                    if data_type is None:
                        continue
                    buf = buf.strip()
                    if not buf and data_type in KNOWN_DATA_TYPES:
                        try:
                            finished_handler = getattr(
                                self, "{}FinishedHandler".format(data_type)
                            )
                        except AttributeError:
                            pass
                        else:
                            finished_handler()
                        log.debug(u"{} data finished".format(data_type))
                        data_type = None
                        continue
                    assert data_type
                    try:
                        fields_handler = getattr(self, "{}Handler".format(data_type))
                    except AttributeError:
                        pass
                    else:
                        fields_handler(data_headers, buf, index)
                    index += 1
        return (self.posts_data.itervalues(), len(self.posts_data))


class DotclearImport(object):
    def __init__(self, host):
        log.info(_("plugin Dotclear Import initialization"))
        self.host = host
        host.plugins["BLOG_IMPORT"].register(
            "dotclear", self.DcImport, SHORT_DESC, LONG_DESC
        )

    def DcImport(self, client, location, options=None):
        if not os.path.isabs(location):
            raise exceptions.DataError(
                u"An absolute path to backup data need to be given as location"
            )
        dc_parser = DotclearParser()
        d = threads.deferToThread(dc_parser.parse, location)
        return d
