#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0077
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
from sat.core import exceptions
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.protocols.jabber import jid, xmlstream, client, error as jabber_error
from twisted.internet import defer, reactor
from sat.tools import xml_tools

from wokkel import data_form

NS_REG = "jabber:iq:register"

PLUGIN_INFO = {
    C.PI_NAME: "XEP 0077 Plugin",
    C.PI_IMPORT_NAME: "XEP-0077",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0077"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0077",
    C.PI_DESCRIPTION: _("""Implementation of in-band registration"""),
}

# FIXME: this implementation is incomplete


class RegisteringAuthenticator(xmlstream.ConnectAuthenticator):
    # FIXME: request IQ is not send to check available fields,
    #        while XEP recommand to use it
    # FIXME: doesn't handle data form or oob
    namespace = 'jabber:client'

    def __init__(self, jid_, password, email=None, check_certificate=True):
        log.debug(_(u"Registration asked for {jid}").format(jid=jid_))
        xmlstream.ConnectAuthenticator.__init__(self, jid_.host)
        self.jid = jid_
        self.password = password
        self.email = email
        self.check_certificate = check_certificate
        self.registered = defer.Deferred()

    def associateWithStream(self, xs):
        xmlstream.ConnectAuthenticator.associateWithStream(self, xs)
        xs.addObserver(xmlstream.STREAM_AUTHD_EVENT, self.register)

        xs.initializers = [client.CheckVersionInitializer(xs)]
        tls_init = xmlstream.TLSInitiatingInitializer(xs)
        tls_init.required = False
        tls_init.check_certificate = self.check_certificate
        xs.initializers.append(tls_init)

    def register(self, xmlstream):
        log.debug(_(u"Stream started with {server}, now registering"
                    .format(server=self.jid.host)))
        iq = XEP_0077.buildRegisterIQ(self.xmlstream, self.jid, self.password, self.email)
        d = iq.send(self.jid.host).addCallbacks(self.registrationCb, self.registrationEb)
        d.chainDeferred(self.registered)

    def registrationCb(self, answer):
        log.debug(_(u"Registration answer: {}").format(answer.toXml()))
        self.xmlstream.sendFooter()

    def registrationEb(self, failure_):
        log.info(_("Registration failure: {}").format(unicode(failure_.value)))
        self.xmlstream.sendFooter()
        raise failure_


class ServerRegister(xmlstream.XmlStreamFactory):

    def __init__(self, *args, **kwargs):
        xmlstream.XmlStreamFactory.__init__(self, *args, **kwargs)
        self.addBootstrap(xmlstream.STREAM_END_EVENT, self._disconnected)

    def clientConnectionLost(self, connector, reason):
        connector.disconnect()

    def _disconnected(self, reason):
        if not self.authenticator.registered.called:
            err = jabber_error.StreamError(u"Server unexpectedly closed the connection")
            try:
                if reason.value.args[0][0][2] == "certificate verify failed":
                    err = exceptions.InvalidCertificate()
            except (IndexError, TypeError):
                pass
            self.authenticator.registered.errback(err)


class XEP_0077(object):
    def __init__(self, host):
        log.info(_("Plugin XEP_0077 initialization"))
        self.host = host
        host.bridge.addMethod(
            "inBandRegister",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self._inBandRegister,
            async=True,
        )
        host.bridge.addMethod(
            "inBandAccountNew",
            ".plugin",
            in_sign="ssssi",
            out_sign="",
            method=self._registerNewAccount,
            async=True,
        )
        host.bridge.addMethod(
            "inBandUnregister",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self._unregister,
            async=True,
        )
        host.bridge.addMethod(
            "inBandPasswordChange",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self._changePassword,
            async=True,
        )

    @staticmethod
    def buildRegisterIQ(xmlstream_, jid_, password, email=None):
        iq_elt = xmlstream.IQ(xmlstream_, "set")
        iq_elt["to"] = jid_.host
        query_elt = iq_elt.addElement(("jabber:iq:register", "query"))
        username_elt = query_elt.addElement("username")
        username_elt.addContent(jid_.user)
        password_elt = query_elt.addElement("password")
        password_elt.addContent(password)
        if email is not None:
            email_elt = query_elt.addElement("email")
            email_elt.addContent(email)
        return iq_elt

    def _regCb(self, answer, client, post_treat_cb):
        """Called after the first get IQ"""
        try:
            query_elt = answer.elements(NS_REG, "query").next()
        except StopIteration:
            raise exceptions.DataError("Can't find expected query element")

        try:
            x_elem = query_elt.elements(data_form.NS_X_DATA, "x").next()
        except StopIteration:
            # XXX: it seems we have an old service which doesn't manage data forms
            log.warning(_("Can't find data form"))
            raise exceptions.DataError(
                _("This gateway can't be managed by SàT, sorry :(")
            )

        def submitForm(data, profile):
            form_elt = xml_tools.XMLUIResultToElt(data)

            iq_elt = client.IQ()
            iq_elt["id"] = answer["id"]
            iq_elt["to"] = answer["from"]
            query_elt = iq_elt.addElement("query", NS_REG)
            query_elt.addChild(form_elt)
            d = iq_elt.send()
            d.addCallback(self._regSuccess, client, post_treat_cb)
            d.addErrback(self._regFailure, client)
            return d

        form = data_form.Form.fromElement(x_elem)
        submit_reg_id = self.host.registerCallback(
            submitForm, with_data=True, one_shot=True
        )
        return xml_tools.dataForm2XMLUI(form, submit_reg_id)

    def _regEb(self, failure, client):
        """Called when something is wrong with registration"""
        log.info(_("Registration failure: %s") % unicode(failure.value))
        raise failure

    def _regSuccess(self, answer, client, post_treat_cb):
        log.debug(_(u"registration answer: %s") % answer.toXml())
        if post_treat_cb is not None:
            post_treat_cb(jid.JID(answer["from"]), client.profile)
        return {}

    def _regFailure(self, failure, client):
        log.info(_(u"Registration failure: %s") % unicode(failure.value))
        if failure.value.condition == "conflict":
            raise exceptions.ConflictError(
                _("Username already exists, please choose an other one")
            )
        raise failure

    def _inBandRegister(self, to_jid_s, profile_key=C.PROF_KEY_NONE):
        return self.inBandRegister, jid.JID(to_jid_s, profile_key)

    def inBandRegister(self, to_jid, post_treat_cb=None, profile_key=C.PROF_KEY_NONE):
        """register to a service

        @param to_jid(jid.JID): jid of the service to register to
        """
        # FIXME: this post_treat_cb arguments seems wrong, check it
        client = self.host.getClient(profile_key)
        log.debug(_(u"Asking registration for {}").format(to_jid.full()))
        reg_request = client.IQ(u"get")
        reg_request["from"] = client.jid.full()
        reg_request["to"] = to_jid.full()
        reg_request.addElement("query", NS_REG)
        d = reg_request.send(to_jid.full()).addCallbacks(
            self._regCb,
            self._regEb,
            callbackArgs=[client, post_treat_cb],
            errbackArgs=[client],
        )
        return d

    def _registerNewAccount(self, jid_, password, email, host, port):
        kwargs = {}
        if email:
            kwargs["email"] = email
        if host:
            kwargs["host"] = host
        if port:
            kwargs["port"] = port
        return self.registerNewAccount(jid.JID(jid_), password, **kwargs)

    def registerNewAccount(
        self, jid_, password, email=None, host=u"127.0.0.1", port=C.XMPP_C2S_PORT
    ):
        """register a new account on a XMPP server

        @param jid_(jid.JID): request jid to register
        @param password(unicode): password of the account
        @param email(unicode): email of the account
        @param host(unicode): host of the server to register to
        @param port(int): port of the server to register to
        """
        check_certificate = host != u"127.0.0.1"
        authenticator = RegisteringAuthenticator(
            jid_, password, email, check_certificate=check_certificate)
        registered_d = authenticator.registered
        server_register = ServerRegister(authenticator)
        reactor.connectTCP(host, port, server_register)
        return registered_d

    def _changePassword(self, new_password, profile_key):
        client = self.host.getClient(profile_key)
        return self.changePassword(client, new_password)

    def changePassword(self, client, new_password):
        iq_elt = self.buildRegisterIQ(client.xmlstream, client.jid, new_password)
        d = iq_elt.send(client.jid.host)
        d.addCallback(
            lambda __: self.host.memory.setParam(
                "Password", new_password, "Connection", profile_key=client.profile
            )
        )
        return d

    def _unregister(self, to_jid_s, profile_key):
        client = self.host.getClient(profile_key)
        return self.unregister(client, jid.JID(to_jid_s))

    def unregister(self, client, to_jid):
        """remove registration from a server/service

        BEWARE! if you remove registration from profile own server, this will
        DELETE THE XMPP ACCOUNT WITHOUT WARNING
        @param to_jid(jid.JID): jid of the service or server
        """
        iq_elt = client.IQ()
        iq_elt["to"] = to_jid.full()
        query_elt = iq_elt.addElement((NS_REG, u"query"))
        query_elt.addElement(u"remove")
        return iq_elt.send()
