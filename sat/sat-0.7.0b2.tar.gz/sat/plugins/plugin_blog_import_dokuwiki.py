#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin to import dokuwiki blogs
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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
from sat.tools import xml_tools
from twisted.internet import threads
from collections import OrderedDict
import calendar
import urllib
import urlparse
import tempfile
import re
import time
import os.path

try:
    from dokuwiki import DokuWiki, DokuWikiError  # this is a new dependency
except ImportError:
    raise exceptions.MissingModule(
        u'Missing module dokuwiki, please install it with "pip install dokuwiki"'
    )
try:
    from PIL import Image  # this is already needed by plugin XEP-0054
except:
    raise exceptions.MissingModule(
        u"Missing module pillow, please download/install it from https://python-pillow.github.io"
    )

PLUGIN_INFO = {
    C.PI_NAME: "Dokuwiki import",
    C.PI_IMPORT_NAME: "IMPORT_DOKUWIKI",
    C.PI_TYPE: C.PLUG_TYPE_BLOG,
    C.PI_DEPENDENCIES: ["BLOG_IMPORT"],
    C.PI_MAIN: "DokuwikiImport",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Blog importer for Dokuwiki blog engine."""),
}

SHORT_DESC = D_(u"import posts from Dokuwiki blog engine")

LONG_DESC = D_(
    u"""This importer handle Dokuwiki blog engine.

To use it, you need an admin access to a running Dokuwiki website
(local or on the Internet). The importer retrieves the data using
the XMLRPC Dokuwiki API.

You can specify a namespace (that could be a namespace directory
or a single post) or leave it empty to use the root namespace "/"
and import all the posts.

You can specify a new media repository to modify the internal
media links and make them point to the URL of your choice, but
note that the upload is not done automatically: a temporary
directory will be created on your local drive and you will
need to upload it yourself to your repository via SSH or FTP.

Following options are recognized:

location: DokuWiki site URL
user: DokuWiki admin user
passwd: DokuWiki admin password
namespace: DokuWiki namespace to import (default: root namespace "/")
media_repo: URL to the new remote media repository (default: none)
limit: maximal number of posts to import (default: 100)

Example of usage (with jp frontend):

jp import dokuwiki -p dave --pwd xxxxxx --connect
    http://127.0.1.1 -o user souliane -o passwd qwertz
    -o namespace public:2015:10
    -o media_repo http://media.diekulturvermittlung.at

This retrieves the 100 last blog posts from http://127.0.1.1 that
are inside the namespace "public:2015:10" using the Dokuwiki user
"souliane", and it imports them to sat profile dave's microblog node.
Internal Dokuwiki media that were hosted on http://127.0.1.1 are now
pointing to http://media.diekulturvermittlung.at.
"""
)
DEFAULT_MEDIA_REPO = ""
DEFAULT_NAMESPACE = "/"
DEFAULT_LIMIT = 100  # you might get a DBUS timeout (no reply) if it lasts too long


class Importer(DokuWiki):
    def __init__(
        self, url, user, passwd, media_repo=DEFAULT_MEDIA_REPO, limit=DEFAULT_LIMIT
    ):
        """

        @param url (unicode): DokuWiki site URL
        @param user (unicode): DokuWiki admin user
        @param passwd (unicode): DokuWiki admin password
        @param media_repo (unicode): New remote media repository
        """
        DokuWiki.__init__(self, url, user, passwd)
        self.url = url
        self.media_repo = media_repo
        self.temp_dir = tempfile.mkdtemp() if self.media_repo else None
        self.limit = limit
        self.posts_data = OrderedDict()

    def getPostId(self, post):
        """Return a unique and constant post id

        @param post(dict): parsed post data
        @return (unicode): post unique item id
        """
        return unicode(post["id"])

    def getPostUpdated(self, post):
        """Return the update date.

        @param post(dict): parsed post data
        @return (unicode): update date
        """
        return unicode(post["mtime"])

    def getPostPublished(self, post):
        """Try to parse the date from the message ID, else use "mtime".

        The date can be extracted if the message ID looks like one of:
            - namespace:YYMMDD_short_title
            - namespace:YYYYMMDD_short_title
        @param post (dict):  parsed post data
        @return (unicode): publication date
        """
        id_, default = unicode(post["id"]), unicode(post["mtime"])
        try:
            date = id_.split(":")[-1].split("_")[0]
        except KeyError:
            return default
        try:
            time_struct = time.strptime(date, "%y%m%d")
        except ValueError:
            try:
                time_struct = time.strptime(date, "%Y%m%d")
            except ValueError:
                return default
        return unicode(calendar.timegm(time_struct))

    def processPost(self, post, profile_jid):
        """Process a single page.

        @param post (dict): parsed post data
        @param profile_jid
        """
        # get main information
        id_ = self.getPostId(post)
        updated = self.getPostUpdated(post)
        published = self.getPostPublished(post)

        # manage links
        backlinks = self.pages.backlinks(id_)
        for link in self.pages.links(id_):
            if link["type"] != "extern":
                assert link["type"] == "local"
                page = link["page"]
                backlinks.append(page[1:] if page.startswith(":") else page)

        self.pages.get(id_)
        content_xhtml = self.processContent(self.pages.html(id_), backlinks, profile_jid)

        # XXX: title is already in content_xhtml and difficult to remove, so leave it
        # title = content.split("\n")[0].strip(u"\ufeff= ")

        # build the extra data dictionary
        mb_data = {
            "id": id_,
            "published": published,
            "updated": updated,
            "author": profile_jid.user,
            # "content": content,  # when passed, it is displayed in Libervia instead of content_xhtml
            "content_xhtml": content_xhtml,
            # "title": title,
            "allow_comments": "true",
        }

        # find out if the message access is public or restricted
        namespace = id_.split(":")[0]
        if namespace and namespace.lower() not in ("public", "/"):
            mb_data["group"] = namespace  # roster group must exist

        self.posts_data[id_] = {"blog": mb_data, "comments": [[]]}

    def process(self, client, namespace=DEFAULT_NAMESPACE):
        """Process a namespace or a single page.

        @param namespace (unicode): DokuWiki namespace (or page) to import
        """
        profile_jid = client.jid
        log.info("Importing data from DokuWiki %s" % self.version)
        try:
            pages_list = self.pages.list(namespace)
        except DokuWikiError:
            log.warning(
                'Could not list Dokuwiki pages: please turn the "display_errors" setting to "Off" in the php.ini of the webserver hosting DokuWiki.'
            )
            return

        if not pages_list:  # namespace is actually a page?
            names = namespace.split(":")
            real_namespace = ":".join(names[0:-1])
            pages_list = self.pages.list(real_namespace)
            pages_list = [page for page in pages_list if page["id"] == namespace]
            namespace = real_namespace

        count = 0
        for page in pages_list:
            self.processPost(page, profile_jid)
            count += 1
            if count >= self.limit:
                break

        return (self.posts_data.itervalues(), len(self.posts_data))

    def processContent(self, text, backlinks, profile_jid):
        """Do text substitutions and file copy.

        @param text (unicode): message content
        @param backlinks (list[unicode]): list of backlinks
        """
        text = text.strip(u"\ufeff")  # this is at the beginning of the file (BOM)

        for backlink in backlinks:
            src = '/doku.php?id=%s"' % backlink
            tgt = '/blog/%s/%s" target="#"' % (profile_jid.user, backlink)
            text = text.replace(src, tgt)

        subs = {}

        link_pattern = r"""<(img|a)[^>]* (src|href)="([^"]+)"[^>]*>"""
        for tag in re.finditer(link_pattern, text):
            type_, attr, link = tag.group(1), tag.group(2), tag.group(3)
            assert (type_ == "img" and attr == "src") or (type_ == "a" and attr == "href")
            if re.match(r"^\w*://", link):  # absolute URL to link directly
                continue
            if self.media_repo:
                self.moveMedia(link, subs)
            elif link not in subs:
                subs[link] = urlparse.urljoin(self.url, link)

        for url, new_url in subs.iteritems():
            text = text.replace(url, new_url)
        return text

    def moveMedia(self, link, subs):
        """Move a media from the DokuWiki host to the new repository.

        This also updates the hyperlinks to internal media files.
        @param link (unicode): media link
        @param subs (dict): substitutions data
        """
        url = urlparse.urljoin(self.url, link)
        user_media = re.match(r"(/lib/exe/\w+.php\?)(.*)", link)
        thumb_width = None

        if user_media:  # media that has been added by the user
            params = urlparse.parse_qs(urlparse.urlparse(url).query)
            try:
                media = params["media"][0]
            except KeyError:
                log.warning("No media found in fetch URL: %s" % user_media.group(2))
                return
            if re.match(r"^\w*://", media):  # external URL to link directly
                subs[link] = media
                return
            try:  # create thumbnail
                thumb_width = params["w"][0]
            except KeyError:
                pass

            filename = media.replace(":", "/")
            # XXX: avoid "precondition failed" error (only keep the media parameter)
            url = urlparse.urljoin(self.url, "/lib/exe/fetch.php?media=%s" % media)

        elif link.startswith("/lib/plugins/"):
            # other link added by a plugin or something else
            filename = link[13:]
        else:  # fake alert... there's no media (or we don't handle it yet)
            return

        filepath = os.path.join(self.temp_dir, filename)
        self.downloadMedia(url, filepath)

        if thumb_width:
            filename = os.path.join("thumbs", thumb_width, filename)
            thumbnail = os.path.join(self.temp_dir, filename)
            self.createThumbnail(filepath, thumbnail, thumb_width)

        new_url = os.path.join(self.media_repo, filename)
        subs[link] = new_url

    def downloadMedia(self, source, dest):
        """Copy media to localhost.

        @param source (unicode): source url
        @param dest (unicode): target path
        """
        dirname = os.path.dirname(dest)
        if not os.path.exists(dest):
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            urllib.urlretrieve(source, dest)
            log.debug("DokuWiki media file copied to %s" % dest)

    def createThumbnail(self, source, dest, width):
        """Create a thumbnail.

        @param source (unicode): source file path
        @param dest (unicode): destination file path
        @param width (unicode): thumbnail's width
        """
        thumb_dir = os.path.dirname(dest)
        if not os.path.exists(thumb_dir):
            os.makedirs(thumb_dir)
        try:
            im = Image.open(source)
            im.thumbnail((width, int(width) * im.size[0] / im.size[1]))
            im.save(dest)
            log.debug("DokuWiki media thumbnail created: %s" % dest)
        except IOError:
            log.error("Cannot create DokuWiki media thumbnail %s" % dest)


class DokuwikiImport(object):
    def __init__(self, host):
        log.info(_("plugin Dokuwiki Import initialization"))
        self.host = host
        self._blog_import = host.plugins["BLOG_IMPORT"]
        self._blog_import.register("dokuwiki", self.DkImport, SHORT_DESC, LONG_DESC)

    def DkImport(self, client, location, options=None):
        """Import from DokuWiki to PubSub

        @param location (unicode): DokuWiki site URL
        @param options (dict, None): DokuWiki import parameters
            - user (unicode): DokuWiki admin user
            - passwd (unicode): DokuWiki admin password
            - namespace (unicode): DokuWiki namespace to import
            - media_repo (unicode): New remote media repository
        """
        options[self._blog_import.OPT_HOST] = location
        try:
            user = options["user"]
        except KeyError:
            raise exceptions.DataError('parameter "user" is required')
        try:
            passwd = options["passwd"]
        except KeyError:
            raise exceptions.DataError('parameter "passwd" is required')

        opt_upload_images = options.get(self._blog_import.OPT_UPLOAD_IMAGES, None)
        try:
            media_repo = options["media_repo"]
            if opt_upload_images:
                options[
                    self._blog_import.OPT_UPLOAD_IMAGES
                ] = False  # force using --no-images-upload
            info_msg = _(
                "DokuWiki media files will be *downloaded* to {temp_dir} - to finish the import you have to upload them *manually* to {media_repo}"
            )
        except KeyError:
            media_repo = DEFAULT_MEDIA_REPO
            if opt_upload_images:
                info_msg = _(
                    "DokuWiki media files will be *uploaded* to the XMPP server. Hyperlinks to these media may not been updated though."
                )
            else:
                info_msg = _(
                    "DokuWiki media files will *stay* on {location} - some of them may be protected by DokuWiki ACL and will not be accessible."
                )

        try:
            namespace = options["namespace"]
        except KeyError:
            namespace = DEFAULT_NAMESPACE
        try:
            limit = options["limit"]
        except KeyError:
            limit = DEFAULT_LIMIT

        dk_importer = Importer(location, user, passwd, media_repo, limit)
        info_msg = info_msg.format(
            temp_dir=dk_importer.temp_dir, media_repo=media_repo, location=location
        )
        self.host.actionNew(
            {"xmlui": xml_tools.note(info_msg).toXml()}, profile=client.profile
        )
        d = threads.deferToThread(dk_importer.process, client, namespace)
        return d
