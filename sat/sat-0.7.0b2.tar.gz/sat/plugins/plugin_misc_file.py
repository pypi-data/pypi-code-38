#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for file tansfer
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
from sat.tools import xml_tools
from sat.tools import stream
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
import os
import os.path


PLUGIN_INFO = {
    C.PI_NAME: "File Tansfer",
    C.PI_IMPORT_NAME: "FILE",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_MAIN: "FilePlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """File Tansfer Management:
This plugin manage the various ways of sending a file, and choose the best one."""
    ),
}


SENDING = D_(u"Please select a file to send to {peer}")
SENDING_TITLE = D_(u"File sending")
CONFIRM = D_(
    u'{peer} wants to send the file "{name}" to you:\n{desc}\n\nThe file has a size of {size_human}\n\nDo you accept ?'
)
CONFIRM_TITLE = D_(u"Confirm file transfer")
CONFIRM_OVERWRITE = D_(u"File {} already exists, are you sure you want to overwrite ?")
CONFIRM_OVERWRITE_TITLE = D_(u"File exists")
SECURITY_LIMIT = 30

PROGRESS_ID_KEY = "progress_id"


class FilePlugin(object):
    File = stream.SatFile

    def __init__(self, host):
        log.info(_("plugin File initialization"))
        self.host = host
        host.bridge.addMethod(
            "fileSend",
            ".plugin",
            in_sign="ssssa{ss}s",
            out_sign="a{ss}",
            method=self._fileSend,
            async=True,
        )
        self._file_callbacks = []
        host.importMenu(
            (D_("Action"), D_("send file")),
            self._fileSendMenu,
            security_limit=10,
            help_string=D_("Send a file"),
            type_=C.MENU_SINGLE,
        )

    def _fileSend(
        self,
        peer_jid_s,
        filepath,
        name="",
        file_desc="",
        extra=None,
        profile=C.PROF_KEY_NONE,
    ):
        client = self.host.getClient(profile)
        return self.fileSend(
            client, jid.JID(peer_jid_s), filepath, name or None, file_desc or None, extra
        )

    @defer.inlineCallbacks
    def fileSend(
        self, client, peer_jid, filepath, filename=None, file_desc=None, extra=None
    ):
        """Send a file using best available method

        @param peer_jid(jid.JID): jid of the destinee
        @param filepath(str): absolute path to the file
        @param filename(unicode, None): name to use, or None to find it from filepath
        @param file_desc(unicode, None): description of the file
        @param profile: %(doc_profile)s
        @return (dict): action dictionary, with progress id in case of success, else xmlui message
        """
        if not os.path.isfile(filepath):
            raise exceptions.DataError(u"The given path doesn't link to a file")
        if not filename:
            filename = os.path.basename(filepath) or "_"
        for namespace, callback, priority, method_name in self._file_callbacks:
            has_feature = yield self.host.hasFeature(client, namespace, peer_jid)
            if has_feature:
                log.info(
                    u"{name} method will be used to send the file".format(
                        name=method_name
                    )
                )
                progress_id = yield callback(
                    client, peer_jid, filepath, filename, file_desc, extra
                )
                defer.returnValue({"progress": progress_id})
        msg = u"Can't find any method to send file to {jid}".format(jid=peer_jid.full())
        log.warning(msg)
        defer.returnValue(
            {
                "xmlui": xml_tools.note(
                    u"Can't transfer file", msg, C.XMLUI_DATA_LVL_WARNING
                ).toXml()
            }
        )

    def _onFileChoosed(self, client, peer_jid, data):
        cancelled = C.bool(data.get("cancelled", C.BOOL_FALSE))
        if cancelled:
            return
        path = data["path"]
        return self.fileSend(client, peer_jid, path)

    def _fileSendMenu(self, data, profile):
        """ XMLUI activated by menu: return file sending UI

        @param profile: %(doc_profile)s
        """
        try:
            jid_ = jid.JID(data["jid"])
        except RuntimeError:
            raise exceptions.DataError(_("Invalid JID"))

        file_choosed_id = self.host.registerCallback(
            lambda data, profile: self._onFileChoosed(
                self.host.getClient(profile), jid_, data
            ),
            with_data=True,
            one_shot=True,
        )
        xml_ui = xml_tools.XMLUI(
            C.XMLUI_DIALOG,
            dialog_opt={
                C.XMLUI_DATA_TYPE: C.XMLUI_DIALOG_FILE,
                C.XMLUI_DATA_MESS: _(SENDING).format(peer=jid_.full()),
            },
            title=_(SENDING_TITLE),
            submit_id=file_choosed_id,
        )

        return {"xmlui": xml_ui.toXml()}

    def register(self, namespace, callback, priority=0, method_name=None):
        """Register a fileSending method

        @param namespace(unicode): XEP namespace
        @param callback(callable): method to call (must have the same signature as [fileSend])
        @param priority(int): pririoty of this method, the higher available will be used
        @param method_name(unicode): short name for the method, namespace will be used if None
        """
        for data in self._file_callbacks:
            if namespace == data[0]:
                raise exceptions.ConflictError(
                    u"A method with this namespace is already registered"
                )
        self._file_callbacks.append(
            (namespace, callback, priority, method_name or namespace)
        )
        self._file_callbacks.sort(key=lambda data: data[2], reverse=True)

    def unregister(self, namespace):
        for idx, data in enumerate(self._file_callbacks):
            if data[0] == namespace:
                del [idx]
                return
        raise exceptions.NotFound(u"The namespace to unregister doesn't exist")

    # Dialogs with user
    # the overwrite check is done here

    def openFileWrite(self, client, file_path, transfer_data, file_data, stream_object):
        """create SatFile or FileStremaObject for the requested file and fill suitable data
        """
        if stream_object:
            assert "stream_object" not in transfer_data
            transfer_data["stream_object"] = stream.FileStreamObject(
                self.host,
                client,
                file_path,
                mode="wb",
                uid=file_data[PROGRESS_ID_KEY],
                size=file_data["size"],
                data_cb=file_data.get("data_cb"),
            )
        else:
            assert "file_obj" not in transfer_data
            transfer_data["file_obj"] = stream.SatFile(
                self.host,
                client,
                file_path,
                mode="wb",
                uid=file_data[PROGRESS_ID_KEY],
                size=file_data["size"],
                data_cb=file_data.get("data_cb"),
            )

    def _gotConfirmation(
        self, data, client, peer_jid, transfer_data, file_data, stream_object
    ):
        """Called when the permission and dest path have been received

        @param peer_jid(jid.JID): jid of the file sender
        @param transfer_data(dict): same as for [self.getDestDir]
        @param file_data(dict): same as for [self.getDestDir]
        @param stream_object(bool): same as for [self.getDestDir]
        return (bool): True if copy is wanted and OK
            False if user wants to cancel
            if file exists ask confirmation and call again self._getDestDir if needed
        """
        if data.get("cancelled", False):
            return False
        path = data["path"]
        file_data["file_path"] = file_path = os.path.join(path, file_data["name"])
        log.debug(u"destination file path set to {}".format(file_path))

        # we manage case where file already exists
        if os.path.exists(file_path):

            def check_overwrite(overwrite):
                if overwrite:
                    self.openFileWrite(
                        client, file_path, transfer_data, file_data, stream_object
                    )
                    return True
                else:
                    return self.getDestDir(client, peer_jid, transfer_data, file_data)

            exists_d = xml_tools.deferConfirm(
                self.host,
                _(CONFIRM_OVERWRITE).format(file_path),
                _(CONFIRM_OVERWRITE_TITLE),
                action_extra={
                    "meta_from_jid": peer_jid.full(),
                    "meta_type": C.META_TYPE_OVERWRITE,
                    "meta_progress_id": file_data[PROGRESS_ID_KEY],
                },
                security_limit=SECURITY_LIMIT,
                profile=client.profile,
            )
            exists_d.addCallback(check_overwrite)
            return exists_d

        self.openFileWrite(client, file_path, transfer_data, file_data, stream_object)
        return True

    def getDestDir(self, client, peer_jid, transfer_data, file_data, stream_object=False):
        """Request confirmation and destination dir to user

        Overwrite confirmation is managed.
        if transfer is confirmed, 'file_obj' is added to transfer_data
        @param peer_jid(jid.JID): jid of the file sender
        @param filename(unicode): name of the file
        @param transfer_data(dict): data of the transfer session,
            it will be only used to store the file_obj.
            "file_obj" (or "stream_object") key *MUST NOT* exist before using getDestDir
        @param file_data(dict): information about the file to be transfered
            It MUST contain the following keys:
                - peer_jid (jid.JID): other peer jid
                - name (unicode): name of the file to trasnsfer
                    the name must not be empty or contain a "/" character
                - size (int): size of the file
                - desc (unicode): description of the file
                - progress_id (unicode): id to use for progression
            It *MUST NOT* contain the "peer" key
            It may contain:
                - data_cb (callable): method called on each data read/write
            "file_path" will be added to this dict once destination selected
            "size_human" will also be added with human readable file size
        @param stream_object(bool): if True, a stream_object will be used instead of file_obj
            a stream.FileStreamObject will be used
        return (defer.Deferred): True if transfer is accepted
        """
        cont, ret_value = self.host.trigger.returnPoint(
            "FILE_getDestDir", client, peer_jid, transfer_data, file_data, stream_object
        )
        if not cont:
            return ret_value
        filename = file_data["name"]
        assert filename and not "/" in filename
        assert PROGRESS_ID_KEY in file_data
        # human readable size
        file_data["size_human"] = u"{:.6n} Mio".format(
            float(file_data["size"]) / (1024 ** 2)
        )
        d = xml_tools.deferDialog(
            self.host,
            _(CONFIRM).format(peer=peer_jid.full(), **file_data),
            _(CONFIRM_TITLE),
            type_=C.XMLUI_DIALOG_FILE,
            options={C.XMLUI_DATA_FILETYPE: C.XMLUI_DATA_FILETYPE_DIR},
            action_extra={
                "meta_from_jid": peer_jid.full(),
                "meta_type": C.META_TYPE_FILE,
                "meta_progress_id": file_data[PROGRESS_ID_KEY],
            },
            security_limit=SECURITY_LIMIT,
            profile=client.profile,
        )
        d.addCallback(
            self._gotConfirmation,
            client,
            peer_jid,
            transfer_data,
            file_data,
            stream_object,
        )
        return d
