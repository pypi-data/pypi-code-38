#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0096
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
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error
import os


NS_SI_FT = "http://jabber.org/protocol/si/profile/file-transfer"
IQ_SET = '/iq[@type="set"]'
SI_PROFILE_NAME = "file-transfer"
SI_PROFILE = "http://jabber.org/protocol/si/profile/" + SI_PROFILE_NAME

PLUGIN_INFO = {
    C.PI_NAME: "XEP-0096 Plugin",
    C.PI_IMPORT_NAME: "XEP-0096",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0096"],
    C.PI_DEPENDENCIES: ["XEP-0020", "XEP-0095", "XEP-0065", "XEP-0047", "FILE"],
    C.PI_MAIN: "XEP_0096",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of SI File Transfer"""),
}


class XEP_0096(object):
    # TODO: call self._f.unregister when unloading order will be managing (i.e. when depenencies will be unloaded at the end)

    def __init__(self, host):
        log.info(_("Plugin XEP_0096 initialization"))
        self.host = host
        self.managed_stream_m = [
            self.host.plugins["XEP-0065"].NAMESPACE,
            self.host.plugins["XEP-0047"].NAMESPACE,
        ]  # Stream methods managed
        self._f = self.host.plugins["FILE"]
        self._f.register(
            NS_SI_FT, self.sendFile, priority=0, method_name=u"Stream Initiation"
        )
        self._si = self.host.plugins["XEP-0095"]
        self._si.registerSIProfile(SI_PROFILE_NAME, self._transferRequest)
        host.bridge.addMethod(
            "siSendFile", ".plugin", in_sign="sssss", out_sign="s", method=self._sendFile
        )

    def unload(self):
        self._si.unregisterSIProfile(SI_PROFILE_NAME)

    def _badRequest(self, client, iq_elt, message=None):
        """Send a bad-request error

        @param iq_elt(domish.Element): initial <IQ> element of the SI request
        @param message(None, unicode): informational message to display in the logs
        """
        if message is not None:
            log.warning(message)
        self._si.sendError(client, iq_elt, "bad-request")

    def _parseRange(self, parent_elt, file_size):
        """find and parse <range/> element

        @param parent_elt(domish.Element): direct parent of the <range/> element
        @return (tuple[bool, int, int]): a tuple with
            - True if range is required
            - range_offset
            - range_length
        """
        try:
            range_elt = parent_elt.elements(NS_SI_FT, "range").next()
        except StopIteration:
            range_ = False
            range_offset = None
            range_length = None
        else:
            range_ = True

            try:
                range_offset = int(range_elt["offset"])
            except KeyError:
                range_offset = 0

            try:
                range_length = int(range_elt["length"])
            except KeyError:
                range_length = file_size

            if range_offset != 0 or range_length != file_size:
                raise NotImplementedError  # FIXME

        return range_, range_offset, range_length

    def _transferRequest(self, client, iq_elt, si_id, si_mime_type, si_elt):
        """Called when a file transfer is requested

        @param iq_elt(domish.Element): initial <IQ> element of the SI request
        @param si_id(unicode): Stream Initiation session id
        @param si_mime_type("unicode"): Mime type of the file (or default "application/octet-stream" if unknown)
        @param si_elt(domish.Element): request
        """
        log.info(_("XEP-0096 file transfer requested"))
        peer_jid = jid.JID(iq_elt["from"])

        try:
            file_elt = si_elt.elements(NS_SI_FT, "file").next()
        except StopIteration:
            return self._badRequest(
                client, iq_elt, "No <file/> element found in SI File Transfer request"
            )

        try:
            feature_elt = self.host.plugins["XEP-0020"].getFeatureElt(si_elt)
        except exceptions.NotFound:
            return self._badRequest(
                client, iq_elt, "No <feature/> element found in SI File Transfer request"
            )

        try:
            filename = file_elt["name"]
            file_size = int(file_elt["size"])
        except (KeyError, ValueError):
            return self._badRequest(client, iq_elt, "Malformed SI File Transfer request")

        file_date = file_elt.getAttribute("date")
        file_hash = file_elt.getAttribute("hash")

        log.info(
            u"File proposed: name=[{name}] size={size}".format(
                name=filename, size=file_size
            )
        )

        try:
            file_desc = unicode(file_elt.elements(NS_SI_FT, "desc").next())
        except StopIteration:
            file_desc = ""

        try:
            range_, range_offset, range_length = self._parseRange(file_elt, file_size)
        except ValueError:
            return self._badRequest(client, iq_elt, "Malformed SI File Transfer request")

        try:
            stream_method = self.host.plugins["XEP-0020"].negotiate(
                feature_elt, "stream-method", self.managed_stream_m, namespace=None
            )
        except KeyError:
            return self._badRequest(client, iq_elt, "No stream method found")

        if stream_method:
            if stream_method == self.host.plugins["XEP-0065"].NAMESPACE:
                plugin = self.host.plugins["XEP-0065"]
            elif stream_method == self.host.plugins["XEP-0047"].NAMESPACE:
                plugin = self.host.plugins["XEP-0047"]
            else:
                log.error(
                    u"Unknown stream method, this should not happen at this stage, cancelling transfer"
                )
        else:
            log.warning(u"Can't find a valid stream method")
            self._si.sendError(client, iq_elt, "not-acceptable")
            return

        # if we are here, the transfer can start, we just need user's agreement
        data = {
            "name": filename,
            "peer_jid": peer_jid,
            "size": file_size,
            "date": file_date,
            "hash": file_hash,
            "desc": file_desc,
            "range": range_,
            "range_offset": range_offset,
            "range_length": range_length,
            "si_id": si_id,
            "progress_id": si_id,
            "stream_method": stream_method,
            "stream_plugin": plugin,
        }

        d = self._f.getDestDir(client, peer_jid, data, data, stream_object=True)
        d.addCallback(self.confirmationCb, client, iq_elt, data)

    def confirmationCb(self, accepted, client, iq_elt, data):
        """Called on confirmation answer

        @param accepted(bool): True if file transfer is accepted
        @param iq_elt(domish.Element): initial SI request
        @param data(dict): session data
        """
        if not accepted:
            log.info(u"File transfer declined")
            self._si.sendError(client, iq_elt, "forbidden")
            return
        # data, timeout, stream_method, failed_methods = client._xep_0096_waiting_for_approval[sid]
        # can_range = data['can_range'] == "True"
        # range_offset = 0
        # if timeout.active():
        #     timeout.cancel()
        # try:
        #     dest_path = frontend_data['dest_path']
        # except KeyError:
        #     log.error(_('dest path not found in frontend_data'))
        #     del client._xep_0096_waiting_for_approval[sid]
        #     return
        # if stream_method == self.host.plugins["XEP-0065"].NAMESPACE:
        #     plugin = self.host.plugins["XEP-0065"]
        # elif stream_method == self.host.plugins["XEP-0047"].NAMESPACE:
        #     plugin = self.host.plugins["XEP-0047"]
        # else:
        #     log.error(_("Unknown stream method, this should not happen at this stage, cancelling transfer"))
        #     del client._xep_0096_waiting_for_approval[sid]
        #     return

        # file_obj = self._getFileObject(dest_path, can_range)
        # range_offset = file_obj.tell()
        d = data["stream_plugin"].createSession(
            client, data["stream_object"], client.jid, data["peer_jid"], data["si_id"]
        )
        d.addCallback(self._transferCb, client, data)
        d.addErrback(self._transferEb, client, data)

        # we can send the iq result
        feature_elt = self.host.plugins["XEP-0020"].chooseOption(
            {"stream-method": data["stream_method"]}, namespace=None
        )
        misc_elts = []
        misc_elts.append(domish.Element((SI_PROFILE, "file")))
        # if can_range:
        #     range_elt = domish.Element((None, "range"))
        #     range_elt['offset'] = str(range_offset)
        #     #TODO: manage range length
        #     misc_elts.append(range_elt)
        self._si.acceptStream(client, iq_elt, feature_elt, misc_elts)

    def _transferCb(self, __, client, data):
        """Called by the stream method when transfer successfuly finished

        @param data: session data
        """
        # TODO: check hash
        data["stream_object"].close()
        log.info(u"Transfer {si_id} successfuly finished".format(**data))

    def _transferEb(self, failure, client, data):
        """Called when something went wrong with the transfer

        @param id: stream id
        @param data: session data
        """
        log.warning(
            u"Transfer {si_id} failed: {reason}".format(
                reason=unicode(failure.value), **data
            )
        )
        data["stream_object"].close()

    def _sendFile(self, peer_jid_s, filepath, name, desc, profile=C.PROF_KEY_NONE):
        client = self.host.getClient(profile)
        return self.sendFile(
            client, jid.JID(peer_jid_s), filepath, name or None, desc or None
        )

    def sendFile(self, client, peer_jid, filepath, name=None, desc=None, extra=None):
        """Send a file using XEP-0096

        @param peer_jid(jid.JID): recipient
        @param filepath(str): absolute path to the file to send
        @param name(unicode): name of the file to send
            name must not contain "/" characters
        @param desc: description of the file
        @param extra: not used here
        @return: an unique id to identify the transfer
        """
        feature_elt = self.host.plugins["XEP-0020"].proposeFeatures(
            {"stream-method": self.managed_stream_m}, namespace=None
        )

        file_transfer_elts = []

        statinfo = os.stat(filepath)
        file_elt = domish.Element((SI_PROFILE, "file"))
        file_elt["name"] = name or os.path.basename(filepath)
        assert "/" not in file_elt["name"]
        size = statinfo.st_size
        file_elt["size"] = str(size)
        if desc:
            file_elt.addElement("desc", content=desc)
        file_transfer_elts.append(file_elt)

        file_transfer_elts.append(domish.Element((None, "range")))

        sid, offer_d = self._si.proposeStream(
            client, peer_jid, SI_PROFILE, feature_elt, file_transfer_elts
        )
        args = [filepath, sid, size, client]
        offer_d.addCallbacks(self._fileCb, self._fileEb, args, None, args)
        return sid

    def _fileCb(self, result_tuple, filepath, sid, size, client):
        iq_elt, si_elt = result_tuple

        try:
            feature_elt = self.host.plugins["XEP-0020"].getFeatureElt(si_elt)
        except exceptions.NotFound:
            log.warning(u"No <feature/> element found in result while expected")
            return

        choosed_options = self.host.plugins["XEP-0020"].getChoosedOptions(
            feature_elt, namespace=None
        )
        try:
            stream_method = choosed_options["stream-method"]
        except KeyError:
            log.warning(u"No stream method choosed")
            return

        try:
            file_elt = si_elt.elements(NS_SI_FT, "file").next()
        except StopIteration:
            pass
        else:
            range_, range_offset, range_length = self._parseRange(file_elt, size)

        if stream_method == self.host.plugins["XEP-0065"].NAMESPACE:
            plugin = self.host.plugins["XEP-0065"]
        elif stream_method == self.host.plugins["XEP-0047"].NAMESPACE:
            plugin = self.host.plugins["XEP-0047"]
        else:
            log.warning(u"Invalid stream method received")
            return

        stream_object = stream.FileStreamObject(
            self.host, client, filepath, uid=sid, size=size
        )
        d = plugin.startStream(client, stream_object, client.jid,
                               jid.JID(iq_elt["from"]), sid)
        d.addCallback(self._sendCb, client, sid, stream_object)
        d.addErrback(self._sendEb, client, sid, stream_object)

    def _fileEb(self, failure, filepath, sid, size, client):
        if failure.check(error.StanzaError):
            stanza_err = failure.value
            if stanza_err.code == "403" and stanza_err.condition == "forbidden":
                from_s = stanza_err.stanza["from"]
                log.info(u"File transfer refused by {}".format(from_s))
                msg = D_(u"The contact {} has refused your file").format(from_s)
                title = D_(u"File refused")
                xml_tools.quickNote(self.host, client, msg, title, C.XMLUI_DATA_LVL_INFO)
            else:
                log.warning(_(u"Error during file transfer"))
                msg = D_(
                    u"Something went wrong during the file transfer session initialisation: {reason}"
                ).format(reason=unicode(stanza_err))
                title = D_(u"File transfer error")
                xml_tools.quickNote(self.host, client, msg, title, C.XMLUI_DATA_LVL_ERROR)
        elif failure.check(exceptions.DataError):
            log.warning(u"Invalid stanza received")
        else:
            log.error(u"Error while proposing stream: {}".format(failure))

    def _sendCb(self, __, client, sid, stream_object):
        log.info(
            _(u"transfer {sid} successfuly finished [{profile}]").format(
                sid=sid, profile=client.profile
            )
        )
        stream_object.close()

    def _sendEb(self, failure, client, sid, stream_object):
        log.warning(
            _(u"transfer {sid} failed [{profile}]: {reason}").format(
                sid=sid, profile=client.profile, reason=unicode(failure.value)
            )
        )
        stream_object.close()
