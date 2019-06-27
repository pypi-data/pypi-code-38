#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SàT command line tool
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


import base
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from sat.tools.common.ansi import ANSI as A
from sat.tools.common import data_objects
from sat.tools.common import uri
from sat.tools import config
from ConfigParser import NoSectionError, NoOptionError
from functools import partial
import json
import sys
import os.path
import os
import time
import tempfile
import subprocess
import codecs
from sat.tools.common import data_format

__commands__ = ["Blog"]

SYNTAX_XHTML = u"xhtml"
# extensions to use with known syntaxes
SYNTAX_EXT = {
    # FIXME: default syntax doesn't sounds needed, there should always be a syntax set
    #        by the plugin.
    "": "txt",  # used when the syntax is not found
    SYNTAX_XHTML: "xhtml",
    "markdown": "md",
}


CONF_SYNTAX_EXT = u"syntax_ext_dict"
BLOG_TMP_DIR = u"blog"
# key to remove from metadata tmp file if they exist
KEY_TO_REMOVE_METADATA = (
    "id",
    "content",
    "content_xhtml",
    "comments_node",
    "comments_service",
    "updated",
)

URL_REDIRECT_PREFIX = "url_redirect_"
INOTIFY_INSTALL = '"pip install inotify"'
MB_KEYS = (
    u"id",
    u"url",
    u"atom_id",
    u"updated",
    u"published",
    u"language",
    u"comments",  # this key is used for all comments* keys
    u"tags",  # this key is used for all tag* keys
    u"author",
    u"author_jid",
    u"author_email",
    u"author_jid_verified",
    u"content",
    u"content_xhtml",
    u"title",
    u"title_xhtml",
)
OUTPUT_OPT_NO_HEADER = u"no-header"


def guessSyntaxFromPath(host, sat_conf, path):
    """Return syntax guessed according to filename extension

    @param sat_conf(ConfigParser.ConfigParser): instance opened on sat configuration
    @param path(str): path to the content file
    @return(unicode): syntax to use
    """
    # we first try to guess syntax with extension
    ext = os.path.splitext(path)[1][1:]  # we get extension without the '.'
    if ext:
        for k, v in SYNTAX_EXT.iteritems():
            if k and ext == v:
                return k

    # if not found, we use current syntax
    return host.bridge.getParamA("Syntax", "Composition", "value", host.profile)


class BlogPublishCommon(object):
    """handle common option for publising commands (Set and Edit)"""

    @property
    def current_syntax(self):
        if self._current_syntax is None:
            self._current_syntax = self.host.bridge.getParamA(
                "Syntax", "Composition", "value", self.profile
            )
        return self._current_syntax

    def add_parser_options(self):
        self.parser.add_argument(
            "-T", "--title", type=base.unicode_decoder, help=_(u"title of the item")
        )
        self.parser.add_argument(
            "-t",
            "--tag",
            type=base.unicode_decoder,
            action="append",
            help=_(u"tag (category) of your item"),
        )

        comments_group = self.parser.add_mutually_exclusive_group()
        comments_group.add_argument(
            "-C", "--comments", action="store_const", const=True, dest="comments",
            help=_(u"enable comments (default: comments not enabled except if they "
                   u"already exist)")
        )
        comments_group.add_argument(
            "--no-comments", action="store_const", const=False, dest="comments",
            help=_(u"disable comments (will remove comments node if it exist)")
        )

        self.parser.add_argument(
            "-S",
            "--syntax",
            type=base.unicode_decoder,
            help=_(u"syntax to use (default: get profile's default syntax)"),
        )

    def setMbDataContent(self, content, mb_data):
        if self.args.syntax is None:
            # default syntax has been used
            mb_data["content_rich"] = content
        elif self.current_syntax == SYNTAX_XHTML:
            mb_data["content_xhtml"] = content
        else:
            mb_data["content_xhtml"] = self.host.bridge.syntaxConvert(
                content, self.current_syntax, SYNTAX_XHTML, False, self.profile
            )

    def setMbDataFromArgs(self, mb_data):
        """set microblog metadata according to command line options

        if metadata already exist, it will be overwritten
        """
        if self.args.comments is not None:
            mb_data["allow_comments"] = self.args.comments
        if self.args.tag:
            mb_data[u'tags'] = self.args.tag
        if self.args.title is not None:
            mb_data["title"] = self.args.title


class Set(base.CommandBase, BlogPublishCommon):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM},
            help=_(u"publish a new blog item or update an existing one"),
        )
        BlogPublishCommon.__init__(self)
        self.need_loop = True

    def add_parser_options(self):
        BlogPublishCommon.add_parser_options(self)

    def mbSendCb(self):
        self.disp(u"Item published")
        self.host.quit(C.EXIT_OK)

    def start(self):
        self._current_syntax = self.args.syntax
        self.pubsub_item = self.args.item
        mb_data = {}
        self.setMbDataFromArgs(mb_data)
        if self.pubsub_item:
            mb_data["id"] = self.pubsub_item
        content = codecs.getreader("utf-8")(sys.stdin).read()
        self.setMbDataContent(content, mb_data)

        self.host.bridge.mbSend(
            self.args.service,
            self.args.node,
            data_format.serialise(mb_data),
            self.profile,
            callback=self.exitCb,
            errback=partial(
                self.errback,
                msg=_(u"can't send item: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Get(base.CommandBase):
    TEMPLATE = u"blog/articles.html"

    def __init__(self, host):
        extra_outputs = {"default": self.default_output, "fancy": self.fancy_output}
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_verbose=True,
            use_pubsub=True,
            pubsub_flags={C.MULTI_ITEMS},
            use_output=C.OUTPUT_COMPLEX,
            extra_outputs=extra_outputs,
            help=_(u"get blog item(s)"),
        )
        self.need_loop = True

    def add_parser_options(self):
        #  TODO: a key(s) argument to select keys to display
        self.parser.add_argument(
            "-k",
            "--key",
            type=base.unicode_decoder,
            action="append",
            dest="keys",
            help=_(u"microblog data key(s) to display (default: depend of verbosity)"),
        )
        # TODO: add MAM filters

    def template_data_mapping(self, data):
        return {u"items": data_objects.BlogItems(data, deserialise=False)}

    def format_comments(self, item, keys):
        comments_data = data_format.dict2iterdict(
            u"comments", item, (u"node", u"service"), pop=True
        )
        lines = []
        for data in comments_data:
            lines.append(data[u"comments"])
            for k in (u"node", u"service"):
                if OUTPUT_OPT_NO_HEADER in self.args.output_opts:
                    header = u""
                else:
                    header = C.A_HEADER + k + u": " + A.RESET
                lines.append(header + data[k])
        return u"\n".join(lines)

    def format_tags(self, item, keys):
        tags = item.pop(u'tags', [])
        return u", ".join(tags)

    def format_updated(self, item, keys):
        return self.format_time(item["updated"])

    def format_published(self, item, keys):
        return self.format_time(item["published"])

    def format_url(self, item, keys):
        return uri.buildXMPPUri(
            u"pubsub",
            subtype=u"microblog",
            path=self.metadata[u"service"],
            node=self.metadata[u"node"],
            item=item[u"id"],
        )

    def get_keys(self):
        """return keys to display according to verbosity or explicit key request"""
        verbosity = self.args.verbose
        if self.args.keys:
            if not set(MB_KEYS).issuperset(self.args.keys):
                self.disp(
                    u"following keys are invalid: {invalid}.\n"
                    u"Valid keys are: {valid}.".format(
                        invalid=u", ".join(set(self.args.keys).difference(MB_KEYS)),
                        valid=u", ".join(sorted(MB_KEYS)),
                    ),
                    error=True,
                )
                self.host.quit(C.EXIT_BAD_ARG)
            return self.args.keys
        else:
            if verbosity == 0:
                return (u"title", u"content")
            elif verbosity == 1:
                return (
                    u"title",
                    u"tags",
                    u"author",
                    u"author_jid",
                    u"author_email",
                    u"author_jid_verified",
                    u"published",
                    u"updated",
                    u"content",
                )
            else:
                return MB_KEYS

    def default_output(self, data):
        """simple key/value output"""
        items, self.metadata = data
        keys = self.get_keys()

        #  k_cb use format_[key] methods for complex formattings
        k_cb = {}
        for k in keys:
            try:
                callback = getattr(self, "format_" + k)
            except AttributeError:
                pass
            else:
                k_cb[k] = callback
        for idx, item in enumerate(items):
            for k in keys:
                if k not in item and k not in k_cb:
                    continue
                if OUTPUT_OPT_NO_HEADER in self.args.output_opts:
                    header = ""
                else:
                    header = u"{k_fmt}{key}:{k_fmt_e} {sep}".format(
                        k_fmt=C.A_HEADER,
                        key=k,
                        k_fmt_e=A.RESET,
                        sep=u"\n" if "content" in k else u"",
                    )
                value = k_cb[k](item, keys) if k in k_cb else item[k]
                if isinstance(value, bool):
                    value = unicode(value).lower()
                self.disp(header + value)
            # we want a separation line after each item but the last one
            if idx < len(items) - 1:
                print(u"")

    def format_time(self, timestamp):
        """return formatted date for timestamp

        @param timestamp(str,int,float): unix timestamp
        @return (unicode): formatted date
        """
        fmt = u"%d/%m/%Y %H:%M:%S"
        return time.strftime(fmt, time.localtime(float(timestamp)))

    def fancy_output(self, data):
        """display blog is a nice to read way

        this output doesn't use keys filter
        """
        # thanks to http://stackoverflow.com/a/943921
        rows, columns = map(int, os.popen("stty size", "r").read().split())
        items, metadata = data
        verbosity = self.args.verbose
        sep = A.color(A.FG_BLUE, columns * u"▬")
        if items:
            print(u"\n" + sep + "\n")

        for idx, item in enumerate(items):
            title = item.get(u"title")
            if verbosity > 0:
                author = item[u"author"]
                published, updated = item[u"published"], item.get("updated")
            else:
                author = published = updated = None
            if verbosity > 1:
                tags = item.pop('tags', [])
            else:
                tags = None
            content = item.get(u"content")

            if title:
                print(A.color(A.BOLD, A.FG_CYAN, item[u"title"]))
            meta = []
            if author:
                meta.append(A.color(A.FG_YELLOW, author))
            if published:
                meta.append(A.color(A.FG_YELLOW, u"on ", self.format_time(published)))
            if updated != published:
                meta.append(
                    A.color(A.FG_YELLOW, u"(updated on ", self.format_time(updated), u")")
                )
            print(u" ".join(meta))
            if tags:
                print(A.color(A.FG_MAGENTA, u", ".join(tags)))
            if (title or tags) and content:
                print("")
            if content:
                self.disp(content)

            print(u"\n" + sep + "\n")

    def mbGetCb(self, mb_result):
        items, metadata = mb_result
        items = [data_format.deserialise(i) for i in items]
        mb_result = items, metadata
        self.output(mb_result)
        self.host.quit(C.EXIT_OK)

    def mbGetEb(self, failure_):
        self.disp(u"can't get blog items: {reason}".format(reason=failure_), error=True)
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.mbGet(
            self.args.service,
            self.args.node,
            self.args.max,
            self.args.items,
            self.getPubsubExtra(),
            self.profile,
            callback=self.mbGetCb,
            errback=self.mbGetEb,
        )


class Edit(base.CommandBase, BlogPublishCommon, common.BaseEdit):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM},
            use_draft=True,
            use_verbose=True,
            help=_(u"edit an existing or new blog post"),
        )
        BlogPublishCommon.__init__(self)
        common.BaseEdit.__init__(self, self.host, BLOG_TMP_DIR, use_metadata=True)

    def add_parser_options(self):
        BlogPublishCommon.add_parser_options(self)
        self.parser.add_argument(
            "-P",
            "--preview",
            action="store_true",
            help=_(u"launch a blog preview in parallel"),
        )

    def buildMetadataFile(self, content_file_path, mb_data=None):
        """Build a metadata file using json

        The file is named after content_file_path, with extension replaced by _metadata.json
        @param content_file_path(str): path to the temporary file which will contain the body
        @param mb_data(dict, None): microblog metadata (for existing items)
        @return (tuple[dict, str]): merged metadata put originaly in metadata file
            and path to temporary metadata file
        """
        # we first construct metadata from edited item ones and CLI argumments
        # or re-use the existing one if it exists
        meta_file_path = os.path.splitext(content_file_path)[0] + common.METADATA_SUFF
        if os.path.exists(meta_file_path):
            self.disp(u"Metadata file already exists, we re-use it")
            try:
                with open(meta_file_path, "rb") as f:
                    mb_data = json.load(f)
            except (OSError, IOError, ValueError) as e:
                self.disp(
                    u"Can't read existing metadata file at {path}, aborting: {reason}".format(
                        path=meta_file_path, reason=e
                    ),
                    error=True,
                )
                self.host.quit(1)
        else:
            mb_data = {} if mb_data is None else mb_data.copy()

        # in all cases, we want to remove unwanted keys
        for key in KEY_TO_REMOVE_METADATA:
            try:
                del mb_data[key]
            except KeyError:
                pass
        # and override metadata with command-line arguments
        self.setMbDataFromArgs(mb_data)

        # then we create the file and write metadata there, as JSON dict
        # XXX: if we port jp one day on Windows, O_BINARY may need to be added here
        with os.fdopen(
            os.open(meta_file_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600), "w+b"
        ) as f:
            # we need to use an intermediate unicode buffer to write to the file unicode without escaping characters
            unicode_dump = json.dumps(
                mb_data,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": "),
                sort_keys=True,
            )
            f.write(unicode_dump.encode("utf-8"))

        return mb_data, meta_file_path

    def edit(self, content_file_path, content_file_obj, mb_data=None):
        """Edit the file contening the content using editor, and publish it"""
        # we first create metadata file
        meta_ori, meta_file_path = self.buildMetadataFile(content_file_path, mb_data)

        # do we need a preview ?
        if self.args.preview:
            self.disp(u"Preview requested, launching it", 1)
            # we redirect outputs to /dev/null to avoid console pollution in editor
            # if user wants to see messages, (s)he can call "blog preview" directly
            DEVNULL = open(os.devnull, "wb")
            subprocess.Popen(
                [
                    sys.argv[0],
                    "blog",
                    "preview",
                    "--inotify",
                    "true",
                    "-p",
                    self.profile,
                    content_file_path,
                ],
                stdout=DEVNULL,
                stderr=subprocess.STDOUT,
            )

        # we launch editor
        self.runEditor(
            "blog_editor_args",
            content_file_path,
            content_file_obj,
            meta_file_path=meta_file_path,
            meta_ori=meta_ori,
        )

    def publish(self, content, mb_data):
        self.setMbDataContent(content, mb_data)

        if self.pubsub_item:
            mb_data["id"] = self.pubsub_item

        mb_data = data_format.serialise(mb_data)

        self.host.bridge.mbSend(
            self.pubsub_service, self.pubsub_node, mb_data, self.profile
        )
        self.disp(u"Blog item published")

    def getTmpSuff(self):
        # we get current syntax to determine file extension
        return SYNTAX_EXT.get(self.current_syntax, SYNTAX_EXT[""])

    def getItemData(self, service, node, item):
        items = [item] if item else []
        mb_data = self.host.bridge.mbGet(service, node, 1, items, {}, self.profile)[0][0]
        mb_data = data_format.deserialise(mb_data)
        try:
            content = mb_data["content_xhtml"]
        except KeyError:
            content = mb_data["content"]
            if content:
                content = self.host.bridge.syntaxConvert(
                    content, "text", SYNTAX_XHTML, False, self.profile
                )
        if content and self.current_syntax != SYNTAX_XHTML:
            content = self.host.bridge.syntaxConvert(
                content, SYNTAX_XHTML, self.current_syntax, False, self.profile
            )
        if content and self.current_syntax == SYNTAX_XHTML:
            content = content.strip()
            if not content.startswith('<div>'):
                content = u'<div>' + content + u'</div>'
            try:
                from lxml import etree
            except ImportError:
                self.disp(_(u"You need lxml to edit pretty XHTML"))
            else:
                parser = etree.XMLParser(remove_blank_text=True)
                root = etree.fromstring(content, parser)
                content = etree.tostring(root, encoding=unicode, pretty_print=True)

        return content, mb_data, mb_data["id"]

    def start(self):
        # if there are user defined extension, we use them
        SYNTAX_EXT.update(config.getConfig(self.sat_conf, "jp", CONF_SYNTAX_EXT, {}))
        self._current_syntax = self.args.syntax
        if self._current_syntax is not None:
            try:
                self._current_syntax = self.args.syntax = self.host.bridge.syntaxGet(
                    self.current_syntax
                )
            except Exception as e:
                if "NotFound" in unicode(
                    e
                ):  #  FIXME: there is not good way to check bridge errors
                    self.parser.error(
                        _(u"unknown syntax requested ({syntax})").format(
                            syntax=self.args.syntax
                        )
                    )
                else:
                    raise e

        (
            self.pubsub_service,
            self.pubsub_node,
            self.pubsub_item,
            content_file_path,
            content_file_obj,
            mb_data,
        ) = self.getItemPath()

        self.edit(content_file_path, content_file_obj, mb_data=mb_data)


class Preview(base.CommandBase, common.BaseEdit):
    # TODO: need to be rewritten with template output

    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "preview", use_verbose=True, help=_(u"preview a blog content")
        )
        common.BaseEdit.__init__(self, self.host, BLOG_TMP_DIR, use_metadata=True)

    def add_parser_options(self):
        self.parser.add_argument(
            "--inotify",
            type=str,
            choices=("auto", "true", "false"),
            default=u"auto",
            help=_(u"use inotify to handle preview"),
        )
        self.parser.add_argument(
            "file",
            type=base.unicode_decoder,
            nargs="?",
            default=u"current",
            help=_(u"path to the content file"),
        )

    def showPreview(self):
        # we implement showPreview here so we don't have to import webbrowser and urllib
        # when preview is not used
        url = "file:{}".format(self.urllib.quote(self.preview_file_path))
        self.webbrowser.open_new_tab(url)

    def _launchPreviewExt(self, cmd_line, opt_name):
        url = "file:{}".format(self.urllib.quote(self.preview_file_path))
        args = common.parse_args(
            self.host, cmd_line, url=url, preview_file=self.preview_file_path
        )
        if not args:
            self.disp(
                u'Couln\'t find command in "{name}", abording'.format(name=opt_name),
                error=True,
            )
            self.host.quit(1)
        subprocess.Popen(args)

    def openPreviewExt(self):
        self._launchPreviewExt(self.open_cb_cmd, "blog_preview_open_cmd")

    def updatePreviewExt(self):
        self._launchPreviewExt(self.update_cb_cmd, "blog_preview_update_cmd")

    def updateContent(self):
        with open(self.content_file_path, "rb") as f:
            content = f.read().decode("utf-8-sig")
            if content and self.syntax != SYNTAX_XHTML:
                # we use safe=True because we want to have a preview as close as possible
                # to what the people will see
                content = self.host.bridge.syntaxConvert(
                    content, self.syntax, SYNTAX_XHTML, True, self.profile
                )

        xhtml = (
            u'<html xmlns="http://www.w3.org/1999/xhtml">'
            u'<head><meta http-equiv="Content-Type" content="text/html;charset=utf-8" />'
            u"</head>"
            u"<body>{}</body>"
            u"</html>"
        ).format(content)

        with open(self.preview_file_path, "wb") as f:
            f.write(xhtml.encode("utf-8"))

    def start(self):
        import webbrowser
        import urllib

        self.webbrowser, self.urllib = webbrowser, urllib

        if self.args.inotify != "false":
            try:
                import inotify.adapters
                import inotify.constants
                from inotify.calls import InotifyError
            except ImportError:
                if self.args.inotify == "auto":
                    inotify = None
                    self.disp(
                        u"inotify module not found, deactivating feature. You can install"
                        u" it with {install}".format(install=INOTIFY_INSTALL)
                    )
                else:
                    self.disp(
                        u"inotify not found, can't activate the feature! Please install "
                        u"it with {install}".format(install=INOTIFY_INSTALL),
                        error=True,
                    )
                    self.host.quit(1)
            else:
                # we deactivate logging in inotify, which is quite annoying
                try:
                    inotify.adapters._LOGGER.setLevel(40)
                except AttributeError:
                    self.disp(
                        u"Logger doesn't exists, inotify may have chanded", error=True
                    )
        else:
            inotify = None

        sat_conf = config.parseMainConf()
        SYNTAX_EXT.update(config.getConfig(sat_conf, "jp", CONF_SYNTAX_EXT, {}))

        try:
            self.open_cb_cmd = config.getConfig(
                sat_conf, "jp", "blog_preview_open_cmd", Exception
            )
        except (NoOptionError, NoSectionError):
            self.open_cb_cmd = None
            open_cb = self.showPreview
        else:
            open_cb = self.openPreviewExt

        self.update_cb_cmd = config.getConfig(
            sat_conf, "jp", "blog_preview_update_cmd", self.open_cb_cmd
        )
        if self.update_cb_cmd is None:
            update_cb = self.showPreview
        else:
            update_cb = self.updatePreviewExt

        # which file do we need to edit?
        if self.args.file == "current":
            self.content_file_path = self.getCurrentFile(self.profile)
        else:
            self.content_file_path = os.path.abspath(self.args.file)

        self.syntax = guessSyntaxFromPath(self.host, sat_conf, self.content_file_path)

        # at this point the syntax is converted, we can display the preview
        preview_file = tempfile.NamedTemporaryFile(suffix=".xhtml", delete=False)
        self.preview_file_path = preview_file.name
        preview_file.close()
        self.updateContent()

        if inotify is None:
            # XXX: we don't delete file automatically because browser need it
            #      (and webbrowser.open can return before it is read)
            self.disp(
                u"temporary file created at {}\nthis file will NOT BE DELETED "
                u"AUTOMATICALLY, please delete it yourself when you have finished".format(
                    self.preview_file_path
                )
            )
            open_cb()
        else:
            open_cb()
            i = inotify.adapters.Inotify(
                block_duration_s=60
            )  # no need for 1 s duraction, inotify drive actions here

            def add_watch():
                i.add_watch(
                    self.content_file_path.encode('utf-8'),
                    mask=inotify.constants.IN_CLOSE_WRITE
                    | inotify.constants.IN_DELETE_SELF
                    | inotify.constants.IN_MOVE_SELF,
                )

            add_watch()

            try:
                for event in i.event_gen():
                    if event is not None:
                        self.disp(u"Content updated", 1)
                        if {"IN_DELETE_SELF", "IN_MOVE_SELF"}.intersection(event[1]):
                            self.disp(
                                u"{} event catched, changing the watch".format(
                                    ", ".join(event[1])
                                ),
                                2,
                            )
                            try:
                                add_watch()
                            except InotifyError:
                                # if the new file is not here yet we can have an error
                                # as a workaround, we do a little rest
                                time.sleep(1)
                                add_watch()
                        self.updateContent()
                        update_cb()
            except InotifyError:
                self.disp(
                    u"Can't catch inotify events, as the file been deleted?", error=True
                )
            finally:
                os.unlink(self.preview_file_path)
                try:
                    i.remove_watch(self.content_file_path)
                except InotifyError:
                    pass


class Import(base.CommandAnswering):
    def __init__(self, host):
        super(Import, self).__init__(
            host,
            "import",
            use_pubsub=True,
            use_progress=True,
            help=_(u"import an external blog"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "importer",
            type=base.unicode_decoder,
            nargs="?",
            help=_(u"importer name, nothing to display importers list"),
        )
        self.parser.add_argument(
            "--host", type=base.unicode_decoder, help=_(u"original blog host")
        )
        self.parser.add_argument(
            "--no-images-upload",
            action="store_true",
            help=_(u"do *NOT* upload images (default: do upload images)"),
        )
        self.parser.add_argument(
            "--upload-ignore-host",
            help=_(u"do not upload images from this host (default: upload all images)"),
        )
        self.parser.add_argument(
            "--ignore-tls-errors",
            action="store_true",
            help=_("ignore invalide TLS certificate for uploads"),
        )
        self.parser.add_argument(
            "-o",
            "--option",
            action="append",
            nargs=2,
            default=[],
            metavar=(u"NAME", u"VALUE"),
            help=_(u"importer specific options (see importer description)"),
        )
        self.parser.add_argument(
            "location",
            type=base.unicode_decoder,
            nargs="?",
            help=_(
                u"importer data location (see importer description), nothing to show "
                u"importer description"
            ),
        )

    def onProgressStarted(self, metadata):
        self.disp(_(u"Blog upload started"), 2)

    def onProgressFinished(self, metadata):
        self.disp(_(u"Blog uploaded successfully"), 2)
        redirections = {
            k[len(URL_REDIRECT_PREFIX) :]: v
            for k, v in metadata.iteritems()
            if k.startswith(URL_REDIRECT_PREFIX)
        }
        if redirections:
            conf = u"\n".join(
                [
                    u"url_redirections_dict = {}".format(
                        # we need to add ' ' before each new line
                        # and to double each '%' for ConfigParser
                        u"\n ".join(
                            json.dumps(redirections, indent=1, separators=(",", ": "))
                            .replace(u"%", u"%%")
                            .split(u"\n")
                        )
                    ),
                ]
            )
            self.disp(
                _(
                    u"\nTo redirect old URLs to new ones, put the following lines in your"
                    u" sat.conf file, in [libervia] section:\n\n{conf}".format(conf=conf)
                )
            )

    def onProgressError(self, error_msg):
        self.disp(_(u"Error while uploading blog: {}").format(error_msg), error=True)

    def error(self, failure):
        self.disp(
            _("Error while trying to upload a blog: {reason}").format(reason=failure),
            error=True,
        )
        self.host.quit(1)

    def start(self):
        if self.args.location is None:
            for name in ("option", "service", "no_images_upload"):
                if getattr(self.args, name):
                    self.parser.error(
                        _(
                            u"{name} argument can't be used without location argument"
                        ).format(name=name)
                    )
            if self.args.importer is None:
                self.disp(
                    u"\n".join(
                        [
                            u"{}: {}".format(name, desc)
                            for name, desc in self.host.bridge.blogImportList()
                        ]
                    )
                )
            else:
                try:
                    short_desc, long_desc = self.host.bridge.blogImportDesc(
                        self.args.importer
                    )
                except Exception as e:
                    msg = [l for l in unicode(e).split("\n") if l][
                        -1
                    ]  # we only keep the last line
                    self.disp(msg)
                    self.host.quit(1)
                else:
                    self.disp(
                        u"{name}: {short_desc}\n\n{long_desc}".format(
                            name=self.args.importer,
                            short_desc=short_desc,
                            long_desc=long_desc,
                        )
                    )
            self.host.quit()
        else:
            # we have a location, an import is requested
            options = {key: value for key, value in self.args.option}
            if self.args.host:
                options["host"] = self.args.host
            if self.args.ignore_tls_errors:
                options["ignore_tls_errors"] = C.BOOL_TRUE
            if self.args.no_images_upload:
                options["upload_images"] = C.BOOL_FALSE
                if self.args.upload_ignore_host:
                    self.parser.error(
                        u"upload-ignore-host option can't be used when no-images-upload "
                        u"is set"
                    )
            elif self.args.upload_ignore_host:
                options["upload_ignore_host"] = self.args.upload_ignore_host

            def gotId(id_):
                self.progress_id = id_

            self.host.bridge.blogImport(
                self.args.importer,
                self.args.location,
                options,
                self.args.service,
                self.args.node,
                self.profile,
                callback=gotId,
                errback=self.error,
            )


class Blog(base.CommandBase):
    subcommands = (Set, Get, Edit, Preview, Import)

    def __init__(self, host):
        super(Blog, self).__init__(
            host, "blog", use_profile=False, help=_("blog/microblog management")
        )
