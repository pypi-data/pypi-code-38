#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Message Archive Management (XEP-0313)
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

from sat.core.constants import Const as C
from sat.core.i18n import _
from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools.common import data_format
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from zope.interface import implements
from datetime import datetime
from dateutil import tz
from wokkel import disco
from wokkel import data_form
import uuid

# XXX: mam and rsm come from sat_tmp.wokkel
from wokkel import rsm
from wokkel import mam


log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: u"Message Archive Management",
    C.PI_IMPORT_NAME: u"XEP-0313",
    C.PI_TYPE: u"XEP",
    C.PI_PROTOCOLS: [u"XEP-0313"],
    C.PI_DEPENDENCIES: [u"XEP-0059", u"XEP-0359"],
    C.PI_MAIN: u"XEP_0313",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: _(u"""Implementation of Message Archive Management"""),
}

MAM_PREFIX = u"mam_"
FILTER_PREFIX = MAM_PREFIX + "filter_"
KEY_LAST_STANZA_ID = u"last_stanza_id"
MESSAGE_RESULT = "/message/result[@xmlns='{mam_ns}' and @queryid='{query_id}']"
MESSAGE_STANZA_ID = '/message/stanza-id[@xmlns="{ns_stanza_id}"]'


class XEP_0313(object):
    def __init__(self, host):
        log.info(_("Message Archive Management plugin initialization"))
        self.host = host
        self.host.registerNamespace(u"mam", mam.NS_MAM)
        self._rsm = host.plugins[u"XEP-0059"]
        self._sid = host.plugins[u"XEP-0359"]
        # Deferred used to store last stanza id in order of reception
        self._last_stanza_id_d = defer.Deferred()
        self._last_stanza_id_d.callback(None)
        host.bridge.addMethod(
            "MAMGet", ".plugin", in_sign='sss',
            out_sign='(a(sdssa{ss}a{ss}sa{ss})a{ss}s)', method=self._getArchives,
            async=True)

    @defer.inlineCallbacks
    def profileConnected(self, client):
        stanza_id_data = yield self.host.memory.storage.getPrivates(
            mam.NS_MAM, [KEY_LAST_STANZA_ID], profile=client.profile)
        stanza_id = stanza_id_data.get(KEY_LAST_STANZA_ID)
        if stanza_id is None:
            log.info(u"can't retrieve last stanza ID, checking history")
            last_mess = yield self.host.memory.historyGet(
                None, None, limit=1, filters={u'not_types': C.MESS_TYPE_GROUPCHAT,
                                              u'last_stanza_id': True},
                profile=client.profile)
            if not last_mess:
                log.info(_(u"It seems that we have no MAM history yet"))
                return
            stanza_id = last_mess[0][-1][u'stanza_id']
        rsm_req = rsm.RSMRequest(max_=100, after=stanza_id)
        mam_req = mam.MAMRequest(rsm_=rsm_req)
        complete = False
        count = 0
        while not complete:
            mam_data = yield self.getArchives(client, mam_req,
                                              service=client.jid.userhostJID())
            elt_list, rsm_response, mam_response = mam_data
            complete = mam_response[u"complete"]
            # we update MAM request for next iteration
            mam_req.rsm.after = rsm_response.last
            if not elt_list:
                break
            else:
                count += len(elt_list)

            for mess_elt in elt_list:
                try:
                    fwd_message_elt = self.getMessageFromResult(
                        client, mess_elt, mam_req)
                except exceptions.DataError:
                    continue

                try:
                    destinee = jid.JID(fwd_message_elt['to'])
                except KeyError:
                    log.warning(_(u'missing "to" attribute in forwarded message'))
                    destinee = client.jid
                if destinee.userhostJID() == client.jid.userhostJID():
                    # message to use, we insert the forwarded message in the normal
                    # workflow
                    client.xmlstream.dispatch(fwd_message_elt)
                else:
                    # this message should be from us, we just add it to history
                    try:
                        from_jid = jid.JID(fwd_message_elt['from'])
                    except KeyError:
                        log.warning(_(u'missing "from" attribute in forwarded message'))
                        from_jid = client.jid
                    if from_jid.userhostJID() != client.jid.userhostJID():
                        log.warning(_(
                            u'was expecting a message sent by our jid, but this one if '
                            u'from {from_jid}, ignoring\n{xml}').format(
                                from_jid=from_jid.full(), xml=mess_elt.toXml()))
                        continue
                    # adding message to history
                    mess_data = client.messageProt.parseMessage(fwd_message_elt)
                    yield client.messageProt.addToHistory(mess_data)

        if not count:
            log.info(_(u"We have received no message while offline"))
        else:
            log.info(_(u"We have received {num_mess} message(s) while offline.")
                .format(num_mess=count))

    def getHandler(self, client):
        mam_client = client._mam = SatMAMClient(self)
        return mam_client

    def parseExtra(self, extra, with_rsm=True):
        """Parse extra dictionnary to retrieve MAM arguments

        @param extra(dict): data for parse
        @param with_rsm(bool): if True, RSM data will be parsed too
        @return (data_form, None): request with parsed arguments
            or None if no MAM arguments have been found
        """
        mam_args = {}
        form_args = {}
        for arg in (u"start", u"end"):
            try:
                value = extra.pop(MAM_PREFIX + arg)
                form_args[arg] = datetime.fromtimestamp(float(value), tz.tzutc())
            except (TypeError, ValueError):
                log.warning(u"Bad value for {arg} filter ({value}), ignoring".format(
                    arg=arg, value=value))
            except KeyError:
                continue

        try:
            form_args[u"with_jid"] = jid.JID(extra.pop(
                MAM_PREFIX + u"with"))
        except (jid.InvalidFormat):
            log.warning(u"Bad value for jid filter")
        except KeyError:
            pass

        for name, value in extra.iteritems():
            if name.startswith(FILTER_PREFIX):
                var = name[len(FILTER_PREFIX):]
                extra_fields = form_args.setdefault(u"extra_fields", [])
                extra_fields.append(data_form.Field(var=var, value=value))

        for arg in (u"node", u"query_id"):
            try:
                value = extra.pop(MAM_PREFIX + arg)
                mam_args[arg] = value
            except KeyError:
                continue

        if with_rsm:
            rsm_request = self._rsm.parseExtra(extra)
            if rsm_request is not None:
                mam_args["rsm_"] = rsm_request

        if form_args:
            mam_args["form"] = mam.buildForm(**form_args)

        # we only set orderBy if we have other MAM args
        # else we would make a MAM query while it's not expected
        if u"order_by" in extra and mam_args:
            order_by = extra.pop(u"order_by")
            assert isinstance(order_by, list)
            mam_args["orderBy"] = order_by

        return mam.MAMRequest(**mam_args) if mam_args else None

    def serialise(self, mam_response, data=None):
        """Serialise data for MAM

        Key set in data can be:
            - mam_complete: a bool const indicating if all items have been received
            - mam_stable: a bool const which is False if items order may be changed
        All values are set as strings.
        @param mam_response(dict): response data to serialise
        @param data(dict, None): dict to update with mam_* data.
            If None, a new dict is created
        @return (dict): data dict
        """
        if data is None:
            data = {}
        data[u"mam_complete"] = C.boolConst(mam_response[u'complete'])
        data[u"mam_stable"] = C.boolConst(mam_response[u'stable'])
        return data

    def getMessageFromResult(self, client, mess_elt, mam_req, service=None):
        """Extract usable <message/> from MAM query result

        The message will be validated, and stanza-id/delay will be added if necessary.
        @param mess_elt(domish.Element): result <message/> element wrapping the message
            to retrieve
        @param mam_req(mam.MAMRequest): request used (needed to get query_id)
        @param service(jid.JID, None): MAM service where the request has been sent
            None if it's user server
        @return domish.Element): <message/> that can be used directly with onMessage
        """
        if mess_elt.name != u"message":
            log.warning(u"unexpected stanza in archive: {xml}".format(
                xml=mess_elt.toXml()))
            raise exceptions.DataError(u"Invalid element")
        service_jid = client.jid.userhostJID() if service is None else service
        mess_from = mess_elt[u"from"]
        # we check that the message has been sent by the right service
        # if service is None (i.e. message expected from our own server)
        # from can be server jid or user's bare jid
        if (mess_from != service_jid.full()
            and not (service is None and mess_from == client.jid.host)):
            log.error(u"Message is not from our server, something went wrong: "
                      u"{xml}".format(xml=mess_elt.toXml()))
            raise exceptions.DataError(u"Invalid element")
        try:
            result_elt = next(mess_elt.elements(mam.NS_MAM, u"result"))
            forwarded_elt = next(result_elt.elements(C.NS_FORWARD, u"forwarded"))
            try:
                delay_elt = next(forwarded_elt.elements(C.NS_DELAY, u"delay"))
            except StopIteration:
                # delay_elt is not mandatory
                delay_elt = None
            fwd_message_elt = next(forwarded_elt.elements(C.NS_CLIENT, u"message"))
        except StopIteration:
            log.warning(u"Invalid message received from MAM: {xml}".format(
                xml=mess_elt.toXml()))
            raise exceptions.DataError(u"Invalid element")
        else:
            if not result_elt[u"queryid"] == mam_req.query_id:
                log.error(u"Unexpected query id (was expecting {query_id}): {xml}"
                    .format(query_id=mam.query_id, xml=mess_elt.toXml()))
                raise exceptions.DataError(u"Invalid element")
            stanza_id = self._sid.getStanzaId(fwd_message_elt,
                                              service_jid)
            if stanza_id is None:
                # not stanza-id element is present, we add one so message
                # will be archived with it, and we won't request several times
                # the same MAM achive
                try:
                    stanza_id = result_elt[u"id"]
                except AttributeError:
                    log.warning(u'Invalid MAM result: missing "id" attribute: {xml}'
                                .format(xml=result_elt.toXml()))
                    raise exceptions.DataError(u"Invalid element")
                self._sid.addStanzaId(client, fwd_message_elt, stanza_id, by=service_jid)

            if delay_elt is not None:
                fwd_message_elt.addChild(delay_elt)

            return fwd_message_elt

    def queryFields(self, client, service=None):
        """Ask the server about supported fields.

        @param service: entity offering the MAM service (None for user archives)
        @return (D(data_form.Form)): form with the implemented fields (cf XEP-0313 §4.1.5)
        """
        return client._mam.queryFields(service)

    def queryArchive(self, client, mam_req, service=None):
        """Query a user, MUC or pubsub archive.

        @param mam_req(mam.MAMRequest): MAM query instance
        @param service(jid.JID, None): entity offering the MAM service
            None for user server
        @return (D(domish.Element)): <IQ/> result
        """
        return client._mam.queryArchive(mam_req, service)

    def _appendMessage(self, elt_list, message_cb, message_elt):
        if message_cb is not None:
            elt_list.append(message_cb(message_elt))
        else:
            elt_list.append(message_elt)

    def _queryFinished(self, iq_result, client, elt_list, event):
        client.xmlstream.removeObserver(event, self._appendMessage)
        try:
            fin_elt = iq_result.elements(mam.NS_MAM, "fin").next()
        except StopIteration:
            raise exceptions.DataError(u"Invalid MAM result")

        mam_response = {u"complete": C.bool(fin_elt.getAttribute(u"complete", C.BOOL_FALSE)),
                        u"stable": C.bool(fin_elt.getAttribute(u"stable", C.BOOL_TRUE))}

        try:
            rsm_response = rsm.RSMResponse.fromElement(fin_elt)
        except rsm.RSMNotFoundError:
            rsm_response = None

        return (elt_list, rsm_response, mam_response)

    def serializeArchiveResult(self, data, client, mam_req, service):
        elt_list, rsm_response, mam_response = data
        mess_list = []
        for elt in elt_list:
            fwd_message_elt = self.getMessageFromResult(client, elt, mam_req,
                                                        service=service)
            mess_data = client.messageProt.parseMessage(fwd_message_elt)
            mess_list.append(client.messageGetBridgeArgs(mess_data))
        metadata = self._rsm.serialise(rsm_response)
        self.serialise(mam_response, metadata)
        return mess_list, metadata, client.profile

    def _getArchives(self, service, extra_ser, profile_key):
        """
        @return: tuple with:
            - list of message with same data as in bridge.messageNew
            - response metadata with:
                - rsm data (rsm_first, rsm_last, rsm_count, rsm_index)
                - mam data (mam_complete, mam_stable)
            - profile
        """
        client = self.host.getClient(profile_key)
        service = jid.JID(service) if service else None
        extra = data_format.deserialise(extra_ser, {})
        mam_req = self.parseExtra(extra)

        d = self.getArchives(client, mam_req, service=service)
        d.addCallback(self.serializeArchiveResult, client, mam_req, service)
        return d

    def getArchives(self, client, query, service=None, message_cb=None):
        """Query archive and gather page result

        @param query(mam.MAMRequest): MAM request
        @param service(jid.JID, None): MAM service to use
            None to use our own server
        @param message_cb(callable, None): callback to use on each message
            this method can be used to unwrap messages
        @return (tuple[list[domish.Element], rsm.RSMResponse, dict): result data with:
            - list of found elements
            - RSM response
            - MAM response, which is a dict with following value:
                - complete: a boolean which is True if all items have been received
                - stable: a boolean which is False if items order may be changed
        """
        if query.query_id is None:
            query.query_id = unicode(uuid.uuid4())
        elt_list = []
        event = MESSAGE_RESULT.format(mam_ns=mam.NS_MAM, query_id=query.query_id)
        client.xmlstream.addObserver(event, self._appendMessage, 0, elt_list, message_cb)
        d = self.queryArchive(client, query, service)
        d.addCallback(self._queryFinished, client, elt_list, event)
        return d

    def getPrefs(self, client, service=None):
        """Retrieve the current user preferences.

        @param service: entity offering the MAM service (None for user archives)
        @return: the server response as a Deferred domish.Element
        """
        # http://xmpp.org/extensions/xep-0313.html#prefs
        return client._mam.queryPrefs(service)

    def _setPrefs(self, service_s=None, default="roster", always=None, never=None,
                  profile_key=C.PROF_KEY_NONE):
        service = jid.JID(service_s) if service_s else None
        always_jid = [jid.JID(entity) for entity in always]
        never_jid = [jid.JID(entity) for entity in never]
        # TODO: why not build here a MAMPrefs object instead of passing the args separately?
        return self.setPrefs(service, default, always_jid, never_jid, profile_key)

    def setPrefs(self, client, service=None, default="roster", always=None, never=None):
        """Set news user preferences.

        @param service: entity offering the MAM service (None for user archives)
        @param default (unicode): a value in ('always', 'never', 'roster')
        @param always (list): a list of JID instances
        @param never (list): a list of JID instances
        @param profile_key (unicode): %(doc_profile_key)s
        @return: the server response as a Deferred domish.Element
        """
        # http://xmpp.org/extensions/xep-0313.html#prefs
        return client._mam.setPrefs(service, default, always, never)

    def onMessageStanzaId(self, message_elt, client):
        """Called when a message with a stanza-id is received

        the messages' stanza ids are stored when received, so the last one can be used
        to retrieve missing history on next connection
        @param message_elt(domish.Element): <message> with a stanza-id
        """
        service_jid = client.jid.userhostJID()
        stanza_id = self._sid.getStanzaId(message_elt, service_jid)
        if stanza_id is None:
            log.debug(u"Ignoring <message>, stanza id is not from our server")
        else:
            # we use self._last_stanza_id_d do be sure that last_stanza_id is stored in
            # the order of reception
            self._last_stanza_id_d.addCallback(
                lambda __: self.host.memory.storage.setPrivateValue(
                    namespace=mam.NS_MAM,
                    key=KEY_LAST_STANZA_ID,
                    value=stanza_id,
                    profile=client.profile))


class SatMAMClient(mam.MAMClient):
    implements(disco.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    @property
    def host(self):
        return self.parent.host_app

    def connectionInitialized(self):
        observer_xpath = MESSAGE_STANZA_ID.format(
            ns_stanza_id=self.host.ns_map[u'stanza_id'])
        self.xmlstream.addObserver(
            observer_xpath, self.plugin_parent.onMessageStanzaId, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(mam.NS_MAM)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
