#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing smtp server
# Copyright (C) 2011  Jérôme Poisson (goffi@goffi.org)

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
from twisted.cred import portal, checkers, credentials
from twisted.cred import error as cred_error
from twisted.mail import smtp
from twisted.python import failure
from email.parser import Parser
from email.utils import parseaddr
from twisted.mail.imap4 import LOGINCredentials, PLAINCredentials
from twisted.internet import reactor
import sys

from zope.interface import implements

PLUGIN_INFO = {
    C.PI_NAME: "SMTP server Plugin",
    C.PI_IMPORT_NAME: "SMTP",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["Maildir"],
    C.PI_MAIN: "SMTP_server",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Create a SMTP server that you can use to send your "normal" type messages"""
    ),
}


class SMTP_server(object):

    params = """
    <params>
    <general>
    <category name="Mail Server">
        <param name="SMTP Port" value="10125" type="int" constraint="1;65535" />
    </category>
    </general>
    </params>
    """

    def __init__(self, host):
        log.info(_("Plugin SMTP Server initialization"))
        self.host = host

        # parameters
        host.memory.updateParams(self.params)

        port = int(self.host.memory.getParamA("SMTP Port", "Mail Server"))
        log.info(_("Launching SMTP server on port %d") % port)

        self.server_factory = SmtpServerFactory(self.host)
        reactor.listenTCP(port, self.server_factory)


class SatSmtpMessage(object):
    implements(smtp.IMessage)

    def __init__(self, host, profile):
        self.host = host
        self.profile = profile
        self.message = []

    def lineReceived(self, line):
        """handle another line"""
        self.message.append(line)

    def eomReceived(self):
        """handle end of message"""
        mail = Parser().parsestr("\n".join(self.message))
        try:
            self.host._sendMessage(
                parseaddr(mail["to"].decode("utf-8", "replace"))[1],
                mail.get_payload().decode(
                    "utf-8", "replace"
                ),  # TODO: manage other charsets
                subject=mail["subject"].decode("utf-8", "replace"),
                mess_type="normal",
                profile_key=self.profile,
            )
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.error(
                _(u"Can't send message: %s") % exc_value
            )  # The email is invalid or incorreclty parsed
            return defer.fail()
        self.message = None
        return defer.succeed(None)

    def connectionLost(self):
        """handle message truncated"""
        raise smtp.SMTPError


class SatSmtpDelivery(object):
    implements(smtp.IMessageDelivery)

    def __init__(self, host, profile):
        self.host = host
        self.profile = profile

    def receivedHeader(self, helo, origin, recipients):
        """
        Generate the Received header for a message
        @param helo: The argument to the HELO command and the client's IP
        address.
        @param origin: The address the message is from
        @param recipients: A list of the addresses for which this message
        is bound.
        @return: The full \"Received\" header string.
        """
        return "Received:"

    def validateTo(self, user):
        """
        Validate the address for which the message is destined.
        @param user: The address to validate.
        @return: A Deferred which becomes, or a callable which
        takes no arguments and returns an object implementing IMessage.
        This will be called and the returned object used to deliver the
        message when it arrives.
        """
        return lambda: SatSmtpMessage(self.host, self.profile)

    def validateFrom(self, helo, origin):
        """
        Validate the address from which the message originates.
        @param helo: The argument to the HELO command and the client's IP
        address.
        @param origin: The address the message is from
        @return: origin or a Deferred whose callback will be
        passed origin.
        """
        return origin


class SmtpRealm(object):
    implements(portal.IRealm)

    def __init__(self, host):
        self.host = host

    def requestAvatar(self, avatarID, mind, *interfaces):
        log.debug("requestAvatar")
        profile = avatarID.decode("utf-8")
        if smtp.IMessageDelivery not in interfaces:
            raise NotImplementedError
        return smtp.IMessageDelivery, SatSmtpDelivery(self.host, profile), lambda: None


class SatProfileCredentialChecker(object):
    """
    This credential checker check against SàT's profile and associated jabber's password
    Check if the profile exists, and if the password is OK
    Return the profile as avatarId
    """

    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (
        credentials.IUsernamePassword,
        credentials.IUsernameHashedPassword,
    )

    def __init__(self, host):
        self.host = host

    def _cbPasswordMatch(self, matched, profile):
        if matched:
            return profile.encode("utf-8")
        else:
            return failure.Failure(cred_error.UnauthorizedLogin())

    def requestAvatarId(self, credentials):
        profiles = self.host.memory.getProfilesList()
        if not credentials.username in profiles:
            return defer.fail(cred_error.UnauthorizedLogin())
        d = self.host.memory.asyncGetParamA(
            "Password", "Connection", profile_key=credentials.username
        )
        d.addCallback(credentials.checkPassword)
        d.addCallback(self._cbPasswordMatch, credentials.username)
        return d


class SmtpServerFactory(smtp.SMTPFactory):
    def __init__(self, host):
        self.protocol = smtp.ESMTP
        self.host = host
        _portal = portal.Portal(SmtpRealm(self.host))
        _portal.registerChecker(SatProfileCredentialChecker(self.host))
        smtp.SMTPFactory.__init__(self, _portal)

    def startedConnecting(self, connector):
        log.debug(_("SMTP server connection started"))
        smtp.SMTPFactory.startedConnecting(self, connector)

    def clientConnectionLost(self, connector, reason):
        log.debug(_(u"SMTP server connection lost (reason: %s)"), reason)
        smtp.SMTPFactory.clientConnectionLost(self, connector, reason)

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        # add the challengers from imap4, more secure and complicated challengers are available
        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p
