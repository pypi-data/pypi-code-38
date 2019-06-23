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


from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.internet import defer
from twisted.web import client as web_client
from twisted.words.xish import domish
from sat.core import exceptions
from sat.tools import xml_tools
import os
import os.path
import tempfile
import urlparse
import shortuuid


PLUGIN_INFO = {
    C.PI_NAME: "blog import",
    C.PI_IMPORT_NAME: "BLOG_IMPORT",
    C.PI_TYPE: (C.PLUG_TYPE_BLOG, C.PLUG_TYPE_IMPORT),
    C.PI_DEPENDENCIES: ["IMPORT", "XEP-0060", "XEP-0277", "TEXT_SYNTAXES", "UPLOAD"],
    C.PI_MAIN: "BlogImportPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        u"""Blog import management:
This plugin manage the different blog importers which can register to it, and handle generic importing tasks."""
    ),
}

OPT_HOST = "host"
OPT_UPLOAD_IMAGES = "upload_images"
OPT_UPLOAD_IGNORE_HOST = "upload_ignore_host"
OPT_IGNORE_TLS = "ignore_tls_errors"
URL_REDIRECT_PREFIX = "url_redirect_"


class BlogImportPlugin(object):
    BOOL_OPTIONS = (OPT_UPLOAD_IMAGES, OPT_IGNORE_TLS)
    JSON_OPTIONS = ()
    OPT_DEFAULTS = {OPT_UPLOAD_IMAGES: True, OPT_IGNORE_TLS: False}

    def __init__(self, host):
        log.info(_("plugin Blog Import initialization"))
        self.host = host
        self._u = host.plugins["UPLOAD"]
        self._p = host.plugins["XEP-0060"]
        self._m = host.plugins["XEP-0277"]
        self._s = self.host.plugins["TEXT_SYNTAXES"]
        host.plugins["IMPORT"].initialize(self, u"blog")

    def importItem(
        self, client, item_import_data, session, options, return_data, service, node
    ):
        """importItem specialized for blog import

        @param item_import_data(dict):
            * mandatory keys:
                'blog' (dict): microblog data of the blog post (cf. http://wiki.goffi.org/wiki/Bridge_API_-_Microblogging/en)
                    the importer MUST NOT create node or call XEP-0277 plugin itself
                    'comments*' key MUST NOT be used in this microblog_data, see bellow for comments
                    It is recommanded to use a unique id in the "id" key which is constant per blog item,
                    so if the import fail, a new import will overwrite the failed items and avoid duplicates.

                'comments' (list[list[dict]],None): Dictionaries must have the same keys as main item (i.e. 'blog' and 'comments')
                    a list of list is used because XEP-0277 can handler several comments nodes,
                    but in most cases, there will we only one item it the first list (something like [[{comment1_data},{comment2_data}, ...]])
                    blog['allow_comments'] must be True if there is any comment, and False (or not present) if comments are not allowed.
                    If allow_comments is False and some comments are present, an exceptions.DataError will be raised
            * optional keys:
                'url' (unicode): former url of the post (only the path, without host part)
                    if present the association to the new path will be displayed to user, so it can make redirections if necessary
        @param options(dict, None): Below are the generic options,
            blog importer can have specific ones. All options have unicode values
            generic options:
                - OPT_HOST (unicode): original host
                - OPT_UPLOAD_IMAGES (bool): upload images to XMPP server if True
                    see OPT_UPLOAD_IGNORE_HOST.
                    Default: True
                - OPT_UPLOAD_IGNORE_HOST (unicode): don't upload images from this host
                - OPT_IGNORE_TLS (bool): ignore TLS error for image upload.
                    Default: False
        @param return_data(dict): will contain link between former posts and new items

        """
        mb_data = item_import_data["blog"]
        try:
            item_id = mb_data["id"]
        except KeyError:
            item_id = mb_data["id"] = unicode(shortuuid.uuid())

        try:
            # we keep the link between old url and new blog item
            # so the user can redirect its former blog urls
            old_uri = item_import_data["url"]
        except KeyError:
            pass
        else:
            new_uri = return_data[URL_REDIRECT_PREFIX + old_uri] = self._p.getNodeURI(
                service if service is not None else client.jid.userhostJID(),
                node or self._m.namespace,
                item_id,
            )
            log.info(u"url link from {old} to {new}".format(old=old_uri, new=new_uri))

        return mb_data

    @defer.inlineCallbacks
    def importSubItems(self, client, item_import_data, mb_data, session, options):
        # comments data
        if len(item_import_data["comments"]) != 1:
            raise NotImplementedError(u"can't manage multiple comment links")
        allow_comments = C.bool(mb_data.get("allow_comments", C.BOOL_FALSE))
        if allow_comments:
            comments_service = yield self._m.getCommentsService(client)
            comments_node = self._m.getCommentsNode(mb_data["id"])
            mb_data["comments_service"] = comments_service.full()
            mb_data["comments_node"] = comments_node
            recurse_kwargs = {
                "items_import_data": item_import_data["comments"][0],
                "service": comments_service,
                "node": comments_node,
            }
            defer.returnValue(recurse_kwargs)
        else:
            if item_import_data["comments"][0]:
                raise exceptions.DataError(
                    u"allow_comments set to False, but comments are there"
                )
            defer.returnValue(None)

    def publishItem(self, client, mb_data, service, node, session):
        log.debug(
            u"uploading item [{id}]: {title}".format(
                id=mb_data["id"], title=mb_data.get("title", "")
            )
        )
        return self._m.send(client, mb_data, service, node)

    @defer.inlineCallbacks
    def itemFilters(self, client, mb_data, session, options):
        """Apply filters according to options

        modify mb_data in place
        @param posts_data(list[dict]): data as returned by importer callback
        @param options(dict): dict as given in [blogImport]
        """
        # FIXME: blog filters don't work on text content
        # TODO: text => XHTML conversion should handler links with <a/>
        #       filters can then be used by converting text to XHTML
        if not options:
            return

        # we want only XHTML content
        for prefix in (
            "content",
        ):  # a tuple is use, if title need to be added in the future
            try:
                rich = mb_data["{}_rich".format(prefix)]
            except KeyError:
                pass
            else:
                if "{}_xhtml".format(prefix) in mb_data:
                    raise exceptions.DataError(
                        u"importer gave {prefix}_rich and {prefix}_xhtml at the same time, this is not allowed".format(
                            prefix=prefix
                        )
                    )
                # we convert rich syntax to XHTML here, so we can handle filters easily
                converted = yield self._s.convert(
                    rich, self._s.getCurrentSyntax(client.profile), safe=False
                )
                mb_data["{}_xhtml".format(prefix)] = converted
                del mb_data["{}_rich".format(prefix)]

            try:
                mb_data["txt"]
            except KeyError:
                pass
            else:
                if "{}_xhtml".format(prefix) in mb_data:
                    log.warning(
                        u"{prefix}_text will be replaced by converted {prefix}_xhtml, so filters can be handled".format(
                            prefix=prefix
                        )
                    )
                    del mb_data["{}_text".format(prefix)]
                else:
                    log.warning(
                        u"importer gave a text {prefix}, blog filters don't work on text {prefix}".format(
                            prefix=prefix
                        )
                    )
                    return

        # at this point, we have only XHTML version of content
        try:
            top_elt = xml_tools.ElementParser()(
                mb_data["content_xhtml"], namespace=C.NS_XHTML
            )
        except domish.ParserError:
            # we clean the xml and try again our luck
            cleaned = yield self._s.cleanXHTML(mb_data["content_xhtml"])
            top_elt = xml_tools.ElementParser()(cleaned, namespace=C.NS_XHTML)
        opt_host = options.get(OPT_HOST)
        if opt_host:
            # we normalise the domain
            parsed_host = urlparse.urlsplit(opt_host)
            opt_host = urlparse.urlunsplit(
                (
                    parsed_host.scheme or "http",
                    parsed_host.netloc or parsed_host.path,
                    "",
                    "",
                    "",
                )
            )

        tmp_dir = tempfile.mkdtemp()
        try:
            # TODO: would be nice to also update the hyperlinks to these images, e.g. when you have <a href="{url}"><img src="{url}"></a>
            for img_elt in xml_tools.findAll(top_elt, names=[u"img"]):
                yield self.imgFilters(client, img_elt, options, opt_host, tmp_dir)
        finally:
            os.rmdir(tmp_dir)  # XXX: tmp_dir should be empty, or something went wrong

        # we now replace the content with filtered one
        mb_data["content_xhtml"] = top_elt.toXml()

    @defer.inlineCallbacks
    def imgFilters(self, client, img_elt, options, opt_host, tmp_dir):
        """Filters handling images

        url without host are fixed (if possible)
        according to options, images are uploaded to XMPP server
        @param img_elt(domish.Element): <img/> element to handle
        @param options(dict): filters options
        @param opt_host(unicode): normalised host given in options
        @param tmp_dir(str): path to temp directory
        """
        try:
            url = img_elt["src"]
            if url[0] == u"/":
                if not opt_host:
                    log.warning(
                        u"host was not specified, we can't deal with src without host ({url}) and have to ignore the following <img/>:\n{xml}".format(
                            url=url, xml=img_elt.toXml()
                        )
                    )
                    return
                else:
                    url = urlparse.urljoin(opt_host, url)
            filename = url.rsplit("/", 1)[-1].strip()
            if not filename:
                raise KeyError
        except (KeyError, IndexError):
            log.warning(u"ignoring invalid img element: {}".format(img_elt.toXml()))
            return

        # we change the url for the normalized one
        img_elt["src"] = url

        if options.get(OPT_UPLOAD_IMAGES, False):
            # upload is requested
            try:
                ignore_host = options[OPT_UPLOAD_IGNORE_HOST]
            except KeyError:
                pass
            else:
                # host is the ignored one, we skip
                parsed_url = urlparse.urlsplit(url)
                if ignore_host in parsed_url.hostname:
                    log.info(
                        u"Don't upload image at {url} because of {opt} option".format(
                            url=url, opt=OPT_UPLOAD_IGNORE_HOST
                        )
                    )
                    return

            # we download images and re-upload them via XMPP
            tmp_file = os.path.join(tmp_dir, filename).encode("utf-8")
            upload_options = {"ignore_tls_errors": options.get(OPT_IGNORE_TLS, False)}

            try:
                yield web_client.downloadPage(url.encode("utf-8"), tmp_file)
                filename = filename.replace(
                    u"%", u"_"
                )  # FIXME: tmp workaround for a bug in prosody http upload
                __, download_d = yield self._u.upload(
                    client, tmp_file, filename, options=upload_options
                )
                download_url = yield download_d
            except Exception as e:
                log.warning(
                    u"can't download image at {url}: {reason}".format(url=url, reason=e)
                )
            else:
                img_elt["src"] = download_url

            try:
                os.unlink(tmp_file)
            except OSError:
                pass
