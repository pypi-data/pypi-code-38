#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
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
import sys
import os
import os.path
import tarfile
from sat.core.i18n import _
from sat.tools.common import data_format
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from sat_frontends.tools import jid
from sat.tools.common.ansi import ANSI as A
import tempfile
import xml.etree.ElementTree as ET  # FIXME: used temporarily to manage XMLUI
from functools import partial
import json

__commands__ = ["File"]


class Send(base.CommandBase):
    def __init__(self, host):
        super(Send, self).__init__(
            host,
            "send",
            use_progress=True,
            use_verbose=True,
            help=_("send a file to a contact"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "files", type=str, nargs="+", metavar="file", help=_(u"a list of file")
        )
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_(u"the destination jid")
        )
        self.parser.add_argument(
            "-b", "--bz2", action="store_true", help=_(u"make a bzip2 tarball")
        )
        self.parser.add_argument(
            "-d",
            "--path",
            type=base.unicode_decoder,
            help=(u"path to the directory where the file must be stored"),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            type=base.unicode_decoder,
            help=(u"namespace of the file"),
        )
        self.parser.add_argument(
            "-n",
            "--name",
            type=base.unicode_decoder,
            default=u"",
            help=(u"name to use (DEFAULT: use source file name)"),
        )

    def start(self):
        """Send files to jabber contact"""
        self.send_files()

    def onProgressStarted(self, metadata):
        self.disp(_(u"File copy started"), 2)

    def onProgressFinished(self, metadata):
        self.disp(_(u"File sent successfully"), 2)

    def onProgressError(self, error_msg):
        if error_msg == C.PROGRESS_ERROR_DECLINED:
            self.disp(_(u"The file has been refused by your contact"))
        else:
            self.disp(_(u"Error while sending file: {}").format(error_msg), error=True)

    def gotId(self, data, file_):
        """Called when a progress id has been received

        @param pid(unicode): progress id
        @param file_(str): file path
        """
        # FIXME: this show progress only for last progress_id
        self.disp(_(u"File request sent to {jid}".format(jid=self.full_dest_jid)), 1)
        try:
            self.progress_id = data["progress"]
        except KeyError:
            # TODO: if 'xmlui' key is present, manage xmlui message display
            self.disp(
                _(u"Can't send file to {jid}".format(jid=self.full_dest_jid)), error=True
            )
            self.host.quit(2)

    def error(self, failure):
        self.disp(
            _("Error while trying to send a file: {reason}").format(reason=failure),
            error=True,
        )
        self.host.quit(1)

    def send_files(self):
        for file_ in self.args.files:
            if not os.path.exists(file_):
                self.disp(_(u"file [{}] doesn't exist !").format(file_), error=True)
                self.host.quit(1)
            if not self.args.bz2 and os.path.isdir(file_):
                self.disp(
                    _(
                        u"[{}] is a dir ! Please send files inside or use compression"
                    ).format(file_)
                )
                self.host.quit(1)

        self.full_dest_jid = self.host.get_full_jid(self.args.jid)
        extra = {}
        if self.args.path:
            extra[u"path"] = self.args.path
        if self.args.namespace:
            extra[u"namespace"] = self.args.namespace

        if self.args.bz2:
            with tempfile.NamedTemporaryFile("wb", delete=False) as buf:
                self.host.addOnQuitCallback(os.unlink, buf.name)
                self.disp(_(u"bz2 is an experimental option, use with caution"))
                # FIXME: check free space
                self.disp(_(u"Starting compression, please wait..."))
                sys.stdout.flush()
                bz2 = tarfile.open(mode="w:bz2", fileobj=buf)
                archive_name = u"{}.tar.bz2".format(
                    os.path.basename(self.args.files[0]) or u"compressed_files"
                )
                for file_ in self.args.files:
                    self.disp(_(u"Adding {}").format(file_), 1)
                    bz2.add(file_)
                bz2.close()
                self.disp(_(u"Done !"), 1)

                self.host.bridge.fileSend(
                    self.full_dest_jid,
                    buf.name,
                    self.args.name or archive_name,
                    "",
                    extra,
                    self.profile,
                    callback=lambda pid, file_=buf.name: self.gotId(pid, file_),
                    errback=self.error,
                )
        else:
            for file_ in self.args.files:
                path = os.path.abspath(file_)
                self.host.bridge.fileSend(
                    self.full_dest_jid,
                    path,
                    self.args.name,
                    "",
                    extra,
                    self.profile,
                    callback=lambda pid, file_=file_: self.gotId(pid, file_),
                    errback=self.error,
                )


class Request(base.CommandBase):
    def __init__(self, host):
        super(Request, self).__init__(
            host,
            "request",
            use_progress=True,
            use_verbose=True,
            help=_("request a file from a contact"),
        )
        self.need_loop = True

    @property
    def filename(self):
        return self.args.name or self.args.hash or u"output"

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_(u"the destination jid")
        )
        self.parser.add_argument(
            "-D",
            "--dest",
            type=base.unicode_decoder,
            help=_(
                u"destination path where the file will be saved (default: [current_dir]/[name|hash])"
            ),
        )
        self.parser.add_argument(
            "-n",
            "--name",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"name of the file"),
        )
        self.parser.add_argument(
            "-H",
            "--hash",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"hash of the file"),
        )
        self.parser.add_argument(
            "-a",
            "--hash-algo",
            type=base.unicode_decoder,
            default=u"sha-256",
            help=_(u"hash algorithm use for --hash (default: sha-256)"),
        )
        self.parser.add_argument(
            "-d",
            "--path",
            type=base.unicode_decoder,
            help=(u"path to the directory containing the file"),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            type=base.unicode_decoder,
            help=(u"namespace of the file"),
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_(u"overwrite existing file without confirmation"),
        )

    def onProgressStarted(self, metadata):
        self.disp(_(u"File copy started"), 2)

    def onProgressFinished(self, metadata):
        self.disp(_(u"File received successfully"), 2)

    def onProgressError(self, error_msg):
        if error_msg == C.PROGRESS_ERROR_DECLINED:
            self.disp(_(u"The file request has been refused"))
        else:
            self.disp(_(u"Error while requesting file: {}").format(error_msg), error=True)

    def gotId(self, progress_id):
        """Called when a progress id has been received

        @param progress_id(unicode): progress id
        """
        self.progress_id = progress_id

    def error(self, failure):
        self.disp(
            _("Error while trying to send a file: {reason}").format(reason=failure),
            error=True,
        )
        self.host.quit(1)

    def start(self):
        if not self.args.name and not self.args.hash:
            self.parser.error(_(u"at least one of --name or --hash must be provided"))
        #  extra = dict(self.args.extra)
        if self.args.dest:
            path = os.path.abspath(os.path.expanduser(self.args.dest))
            if os.path.isdir(path):
                path = os.path.join(path, self.filename)
        else:
            path = os.path.abspath(self.filename)

        if os.path.exists(path) and not self.args.force:
            message = _(u"File {path} already exists! Do you want to overwrite?").format(
                path=path
            )
            confirm = raw_input(u"{} (y/N) ".format(message).encode("utf-8"))
            if confirm not in (u"y", u"Y"):
                self.disp(_(u"file request cancelled"))
                self.host.quit(2)

        self.full_dest_jid = self.host.get_full_jid(self.args.jid)
        extra = {}
        if self.args.path:
            extra[u"path"] = self.args.path
        if self.args.namespace:
            extra[u"namespace"] = self.args.namespace
        self.host.bridge.fileJingleRequest(
            self.full_dest_jid,
            path,
            self.args.name,
            self.args.hash,
            self.args.hash_algo if self.args.hash else u"",
            extra,
            self.profile,
            callback=self.gotId,
            errback=partial(
                self.errback,
                msg=_(u"can't request file: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Receive(base.CommandAnswering):
    def __init__(self, host):
        super(Receive, self).__init__(
            host,
            "receive",
            use_progress=True,
            use_verbose=True,
            help=_("wait for a file to be sent by a contact"),
        )
        self._overwrite_refused = False  # True when one overwrite as already been refused
        self.action_callbacks = {
            C.META_TYPE_FILE: self.onFileAction,
            C.META_TYPE_OVERWRITE: self.onOverwriteAction,
        }

    def onProgressStarted(self, metadata):
        self.disp(_(u"File copy started"), 2)

    def onProgressFinished(self, metadata):
        self.disp(_(u"File received successfully"), 2)
        if metadata.get("hash_verified", False):
            try:
                self.disp(
                    _(u"hash checked: {algo}:{checksum}").format(
                        algo=metadata["hash_algo"], checksum=metadata["hash"]
                    ),
                    1,
                )
            except KeyError:
                self.disp(_(u"hash is checked but hash value is missing", 1), error=True)
        else:
            self.disp(_(u"hash can't be verified"), 1)

    def onProgressError(self, error_msg):
        self.disp(_(u"Error while receiving file: {}").format(error_msg), error=True)

    def getXmluiId(self, action_data):
        # FIXME: we temporarily use ElementTree, but a real XMLUI managing module
        #        should be available in the futur
        # TODO: XMLUI module
        try:
            xml_ui = action_data["xmlui"]
        except KeyError:
            self.disp(_(u"Action has no XMLUI"), 1)
        else:
            ui = ET.fromstring(xml_ui.encode("utf-8"))
            xmlui_id = ui.get("submit")
            if not xmlui_id:
                self.disp(_(u"Invalid XMLUI received"), error=True)
            return xmlui_id

    def onFileAction(self, action_data, action_id, security_limit, profile):
        xmlui_id = self.getXmluiId(action_data)
        if xmlui_id is None:
            return self.host.quitFromSignal(1)
        try:
            from_jid = jid.JID(action_data["meta_from_jid"])
        except KeyError:
            self.disp(_(u"Ignoring action without from_jid data"), 1)
            return
        try:
            progress_id = action_data["meta_progress_id"]
        except KeyError:
            self.disp(_(u"ignoring action without progress id"), 1)
            return

        if not self.bare_jids or from_jid.bare in self.bare_jids:
            if self._overwrite_refused:
                self.disp(_(u"File refused because overwrite is needed"), error=True)
                self.host.bridge.launchAction(
                    xmlui_id, {"cancelled": C.BOOL_TRUE}, profile_key=profile
                )
                return self.host.quitFromSignal(2)
            self.progress_id = progress_id
            xmlui_data = {"path": self.path}
            self.host.bridge.launchAction(xmlui_id, xmlui_data, profile_key=profile)

    def onOverwriteAction(self, action_data, action_id, security_limit, profile):
        xmlui_id = self.getXmluiId(action_data)
        if xmlui_id is None:
            return self.host.quitFromSignal(1)
        try:
            progress_id = action_data["meta_progress_id"]
        except KeyError:
            self.disp(_(u"ignoring action without progress id"), 1)
            return
        self.disp(_(u"Overwriting needed"), 1)

        if progress_id == self.progress_id:
            if self.args.force:
                self.disp(_(u"Overwrite accepted"), 2)
            else:
                self.disp(_(u"Refused to overwrite"), 2)
                self._overwrite_refused = True

            xmlui_data = {"answer": C.boolConst(self.args.force)}
            self.host.bridge.launchAction(xmlui_id, xmlui_data, profile_key=profile)

    def add_parser_options(self):
        self.parser.add_argument(
            "jids",
            type=base.unicode_decoder,
            nargs="*",
            help=_(u"jids accepted (accept everything if none is specified)"),
        )
        self.parser.add_argument(
            "-m",
            "--multiple",
            action="store_true",
            help=_(u"accept multiple files (you'll have to stop manually)"),
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_(
                u"force overwritting of existing files (/!\\ name is choosed by sender)"
            ),
        )
        self.parser.add_argument(
            "--path",
            default=".",
            metavar="DIR",
            help=_(u"destination path (default: working directory)"),
        )

    def start(self):
        self.bare_jids = [jid.JID(jid_).bare for jid_ in self.args.jids]
        self.path = os.path.abspath(self.args.path)
        if not os.path.isdir(self.path):
            self.disp(_(u"Given path is not a directory !", error=True))
            self.host.quit(2)
        if self.args.multiple:
            self.host.quit_on_progress_end = False
        self.disp(_(u"waiting for incoming file request"), 2)


class Upload(base.CommandBase):
    def __init__(self, host):
        super(Upload, self).__init__(
            host, "upload", use_progress=True, use_verbose=True, help=_("upload a file")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument("file", type=str, help=_("file to upload"))
        self.parser.add_argument(
            "jid",
            type=base.unicode_decoder,
            nargs="?",
            help=_("jid of upload component (nothing to autodetect)"),
        )
        self.parser.add_argument(
            "--ignore-tls-errors",
            action="store_true",
            help=_("ignore invalide TLS certificate"),
        )

    def onProgressStarted(self, metadata):
        self.disp(_(u"File upload started"), 2)

    def onProgressFinished(self, metadata):
        self.disp(_(u"File uploaded successfully"), 2)
        try:
            url = metadata["url"]
        except KeyError:
            self.disp(u"download URL not found in metadata")
        else:
            self.disp(_(u"URL to retrieve the file:"), 1)
            # XXX: url is display alone on a line to make parsing easier
            self.disp(url)

    def onProgressError(self, error_msg):
        self.disp(_(u"Error while uploading file: {}").format(error_msg), error=True)

    def gotId(self, data, file_):
        """Called when a progress id has been received

        @param pid(unicode): progress id
        @param file_(str): file path
        """
        try:
            self.progress_id = data["progress"]
        except KeyError:
            # TODO: if 'xmlui' key is present, manage xmlui message display
            self.disp(_(u"Can't upload file"), error=True)
            self.host.quit(2)

    def error(self, failure):
        self.disp(
            _("Error while trying to upload a file: {reason}").format(reason=failure),
            error=True,
        )
        self.host.quit(1)

    def start(self):
        file_ = self.args.file
        if not os.path.exists(file_):
            self.disp(_(u"file [{}] doesn't exist !").format(file_), error=True)
            self.host.quit(1)
        if os.path.isdir(file_):
            self.disp(_(u"[{}] is a dir! Can't upload a dir").format(file_))
            self.host.quit(1)

        self.full_dest_jid = (
            self.host.get_full_jid(self.args.jid) if self.args.jid is not None else ""
        )
        options = {}
        if self.args.ignore_tls_errors:
            options["ignore_tls_errors"] = C.BOOL_TRUE

        path = os.path.abspath(file_)
        self.host.bridge.fileUpload(
            path,
            "",
            self.full_dest_jid,
            options,
            self.profile,
            callback=lambda pid, file_=file_: self.gotId(pid, file_),
            errback=self.error,
        )


class ShareList(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        super(ShareList, self).__init__(
            host,
            "list",
            use_output=C.OUTPUT_LIST_DICT,
            extra_outputs=extra_outputs,
            help=_(u"retrieve files shared by an entity"),
            use_verbose=True,
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-d",
            "--path",
            default=u"",
            help=_(u"path to the directory containing the files"),
        )
        self.parser.add_argument(
            "jid",
            type=base.unicode_decoder,
            nargs="?",
            default="",
            help=_("jid of sharing entity (nothing to check our own jid)"),
        )

    def file_gen(self, files_data):
        for file_data in files_data:
            yield file_data[u"name"]
            yield file_data.get(u"size", "")
            yield file_data.get(u"hash", "")

    def _name_filter(self, name, row):
        if row.type == C.FILE_TYPE_DIRECTORY:
            return A.color(C.A_DIRECTORY, name)
        elif row.type == C.FILE_TYPE_FILE:
            return A.color(C.A_FILE, name)
        else:
            self.disp(_(u"unknown file type: {type}").format(type=row.type), error=True)
            return name

    def _size_filter(self, size, row):
        if not size:
            return u""
        size = int(size)
        #  cf. https://stackoverflow.com/a/1094933 (thanks)
        suffix = u"o"
        for unit in [u"", u"Ki", u"Mi", u"Gi", u"Ti", u"Pi", u"Ei", u"Zi"]:
            if abs(size) < 1024.0:
                return A.color(A.BOLD, u"{:.2f}".format(size), unit, suffix)
            size /= 1024.0

        return A.color(A.BOLD, u"{:.2f}".format(size), u"Yi", suffix)

    def default_output(self, files_data):
        """display files a way similar to ls"""
        files_data.sort(key=lambda d: d["name"].lower())
        show_header = False
        if self.verbosity == 0:
            headers = (u"name", u"type")
        elif self.verbosity == 1:
            headers = (u"name", u"type", u"size")
        elif self.verbosity > 1:
            show_header = True
            headers = (u"name", u"type", u"size", u"hash")
        table = common.Table.fromDict(
            self.host,
            files_data,
            headers,
            filters={u"name": self._name_filter, u"size": self._size_filter},
            defaults={u"size": u"", u"hash": u""},
        )
        table.display_blank(show_header=show_header, hide_cols=["type"])

    def _FISListCb(self, files_data):
        self.output(files_data)
        self.host.quit()

    def start(self):
        self.host.bridge.FISList(
            self.args.jid,
            self.args.path,
            {},
            self.profile,
            callback=self._FISListCb,
            errback=partial(
                self.errback,
                msg=_(u"can't retrieve shared files: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class SharePath(base.CommandBase):
    def __init__(self, host):
        super(SharePath, self).__init__(
            host, "path", help=_(u"share a file or directory"), use_verbose=True
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-n",
            "--name",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"virtual name to use (default: use directory/file name)"),
        )
        perm_group = self.parser.add_mutually_exclusive_group()
        perm_group.add_argument(
            "-j",
            "--jid",
            type=base.unicode_decoder,
            action="append",
            dest="jids",
            default=[],
            help=_(u"jid of contacts allowed to retrieve the files"),
        )
        perm_group.add_argument(
            "--public",
            action="store_true",
            help=_(
                u"share publicly the file(s) (/!\\ *everybody* will be able to access them)"
            ),
        )
        self.parser.add_argument(
            "path",
            type=base.unicode_decoder,
            help=_(u"path to a file or directory to share"),
        )

    def _FISSharePathCb(self, name):
        self.disp(
            _(u'{path} shared under the name "{name}"').format(path=self.path, name=name)
        )
        self.host.quit()

    def start(self):
        self.path = os.path.abspath(self.args.path)
        if self.args.public:
            access = {u"read": {u"type": u"public"}}
        else:
            jids = self.args.jids
            if jids:
                access = {u"read": {u"type": "whitelist", u"jids": jids}}
            else:
                access = {}
        self.host.bridge.FISSharePath(
            self.args.name,
            self.path,
            json.dumps(access, ensure_ascii=False),
            self.profile,
            callback=self._FISSharePathCb,
            errback=partial(
                self.errback,
                msg=_(u"can't share path: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class ShareInvite(base.CommandBase):
    def __init__(self, host):
        super(ShareInvite, self).__init__(
            host, "invite", help=_(u"send invitation for a shared repository")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-n",
            "--name",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"name of the repository"),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"namespace of the repository"),
        )
        self.parser.add_argument(
            "-P",
            "--path",
            type=base.unicode_decoder,
            help=_(u"path to the repository"),
        )
        self.parser.add_argument(
            "-t",
            "--type",
            choices=[u"files", u"photos"],
            default=u"files",
            help=_(u"type of the repository"),
        )
        self.parser.add_argument(
            "-T",
            "--thumbnail",
            type=base.unicode_decoder,
            help=_(u"https URL of a image to use as thumbnail"),
        )
        self.parser.add_argument(
            "service",
            type=base.unicode_decoder,
            help=_(u"jid of the file sharing service hosting the repository"),
        )
        self.parser.add_argument(
            "jid",
            type=base.unicode_decoder,
            help=_(u"jid of the person to invite"),
        )

    def _FISInviteCb(self):
        self.disp(
            _(u'invitation sent to {entity}').format(entity=self.args.jid)
        )
        self.host.quit()

    def start(self):
        self.path = os.path.normpath(self.args.path) if self.args.path else u""
        extra = {}
        if self.args.thumbnail is not None:
            if not self.args.thumbnail.startswith(u'http'):
                self.parser.error(_(u"only http(s) links are allowed with --thumbnail"))
            else:
                extra[u'thumb_url'] = self.args.thumbnail
        self.host.bridge.FISInvite(
            self.args.jid,
            self.args.service,
            self.args.type,
            self.args.namespace,
            self.path,
            self.args.name,
            data_format.serialise(extra),
            self.profile,
            callback=self._FISInviteCb,
            errback=partial(
                self.errback,
                msg=_(u"can't send invitation: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Share(base.CommandBase):
    subcommands = (ShareList, SharePath, ShareInvite)

    def __init__(self, host):
        super(Share, self).__init__(
            host, "share", use_profile=False, help=_(u"files sharing management")
        )


class File(base.CommandBase):
    subcommands = (Send, Request, Receive, Upload, Share)

    def __init__(self, host):
        super(File, self).__init__(
            host, "file", use_profile=False, help=_(u"files sending/receiving/management")
        )
