#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing imap server
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
from twisted.internet import protocol, defer
from twisted.cred import portal, checkers, credentials
from twisted.cred import error as cred_error
from twisted.mail import imap4
from twisted.python import failure
from email.parser import Parser
import os
from cStringIO import StringIO
from twisted.internet import reactor

from zope.interface import implements

PLUGIN_INFO = {
    C.PI_NAME: "IMAP server Plugin",
    C.PI_IMPORT_NAME: "IMAP",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["Maildir"],
    C.PI_MAIN: "IMAP_server",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Create an Imap server that you can use to read your "normal" type messages"""
    ),
}


class IMAP_server(object):
    # TODO: connect profile on mailbox request, once password is accepted

    params = """
    <params>
    <general>
    <category name="Mail Server">
        <param name="IMAP Port" value="10143" type="int" constraint="1;65535" />
    </category>
    </general>
    </params>
    """

    def __init__(self, host):
        log.info(_("Plugin Imap Server initialization"))
        self.host = host

        # parameters
        host.memory.updateParams(self.params)

        port = int(self.host.memory.getParamA("IMAP Port", "Mail Server"))
        log.info(_("Launching IMAP server on port %d") % port)

        self.server_factory = ImapServerFactory(self.host)
        reactor.listenTCP(port, self.server_factory)


class Message(object):
    implements(imap4.IMessage)

    def __init__(self, uid, flags, mess_fp):
        log.debug("Message Init")
        self.uid = uid
        self.flags = flags
        self.mess_fp = mess_fp
        self.message = Parser().parse(mess_fp)

    def getUID(self):
        """Retrieve the unique identifier associated with this message.
        """
        log.debug("getUID (message)")
        return self.uid

    def getFlags(self):
        """Retrieve the flags associated with this message.
        @return: The flags, represented as strings.
        """
        log.debug("getFlags")
        return self.flags

    def getInternalDate(self):
        """Retrieve the date internally associated with this message.
        @return: An RFC822-formatted date string.
        """
        log.debug("getInternalDate")
        return self.message["Date"]

    def getHeaders(self, negate, *names):
        """Retrieve a group of message headers.
        @param names: The names of the headers to retrieve or omit.
        @param negate: If True, indicates that the headers listed in names
        should be omitted from the return value, rather than included.
        @return: A mapping of header field names to header field values
        """
        log.debug(u"getHeaders %s - %s" % (negate, names))
        final_dict = {}
        to_check = [name.lower() for name in names]
        for header in self.message.keys():
            if (negate and not header.lower() in to_check) or (
                not negate and header.lower() in to_check
            ):
                final_dict[header] = self.message[header]
        return final_dict

    def getBodyFile(self):
        """Retrieve a file object containing only the body of this message.
        """
        log.debug("getBodyFile")
        return StringIO(self.message.get_payload())

    def getSize(self):
        """Retrieve the total size, in octets, of this message.
        """
        log.debug("getSize")
        self.mess_fp.seek(0, os.SEEK_END)
        return self.mess_fp.tell()

    def isMultipart(self):
        """Indicate whether this message has subparts.
        """
        log.debug("isMultipart")
        return False

    def getSubPart(self, part):
        """Retrieve a MIME sub-message
        @param part: The number of the part to retrieve, indexed from 0.
        @return: The specified sub-part.
        """
        log.debug("getSubPart")
        return TypeError


class SatMailbox(object):
    implements(imap4.IMailbox)

    def __init__(self, host, name, profile):
        self.host = host
        self.listeners = set()
        log.debug(u"Mailbox init (%s)" % name)
        if name != "INBOX":
            raise imap4.MailboxException("Only INBOX is managed for the moment")
        self.mailbox = self.host.plugins["Maildir"].accessMessageBox(
            name, self.messageNew, profile
        )

    def messageNew(self):
        """Called when a new message is in the mailbox"""
        log.debug("messageNew signal received")
        nb_messages = self.getMessageCount()
        for listener in self.listeners:
            listener.newMessages(nb_messages, None)

    def getUIDValidity(self):
        """Return the unique validity identifier for this mailbox.
        """
        log.debug("getUIDValidity")
        return 0

    def getUIDNext(self):
        """Return the likely UID for the next message added to this mailbox.
        """
        log.debug("getUIDNext")
        return self.mailbox.getNextUid()

    def getUID(self, message):
        """Return the UID of a message in the mailbox
        @param message: The message sequence number
        @return: The UID of the message.
        """
        log.debug(u"getUID (%i)" % message)
        # return self.mailbox.getUid(message-1) #XXX: it seems that this method get uid and not message sequence number
        return message

    def getMessageCount(self):
        """Return the number of messages in this mailbox.
        """
        log.debug("getMessageCount")
        ret = self.mailbox.getMessageCount()
        log.debug("count = %i" % ret)
        return ret

    def getRecentCount(self):
        """Return the number of messages with the 'Recent' flag.
        """
        log.debug("getRecentCount")
        return len(self.mailbox.getMessageIdsWithFlag("\\Recent"))

    def getUnseenCount(self):
        """Return the number of messages with the 'Unseen' flag.
        """
        log.debug("getUnseenCount")
        return self.getMessageCount() - len(self.mailbox.getMessageIdsWithFlag("\\SEEN"))

    def isWriteable(self):
        """Get the read/write status of the mailbox.
        @return: A true value if write permission is allowed, a false value otherwise.
        """
        log.debug("isWriteable")
        return True

    def destroy(self):
        """Called before this mailbox is deleted, permanently.
        """
        log.debug("destroy")

    def requestStatus(self, names):
        """Return status information about this mailbox.
        @param names: The status names to return information regarding.
        The possible values for each name are: MESSAGES, RECENT, UIDNEXT,
        UIDVALIDITY, UNSEEN.
        @return: A dictionary containing status information about the
        requested names is returned.  If the process of looking this
        information up would be costly, a deferred whose callback will
        eventually be passed this dictionary is returned instead.
        """
        log.debug("requestStatus")
        return imap4.statusRequestHelper(self, names)

    def addListener(self, listener):
        """Add a mailbox change listener

        @type listener: Any object which implements C{IMailboxListener}
        @param listener: An object to add to the set of those which will
        be notified when the contents of this mailbox change.
        """
        log.debug(u"addListener %s" % listener)
        self.listeners.add(listener)

    def removeListener(self, listener):
        """Remove a mailbox change listener

        @type listener: Any object previously added to and not removed from
        this mailbox as a listener.
        @param listener: The object to remove from the set of listeners.

        @raise ValueError: Raised when the given object is not a listener for
        this mailbox.
        """
        log.debug("removeListener")
        if listener in self.listeners:
            self.listeners.remove(listener)
        else:
            raise imap4.MailboxException("Trying to remove an unknown listener")

    def addMessage(self, message, flags=(), date=None):
        """Add the given message to this mailbox.
        @param message: The RFC822 formatted message
        @param flags: The flags to associate with this message
        @param date: If specified, the date to associate with this
        @return: A deferred whose callback is invoked with the message
        id if the message is added successfully and whose errback is
        invoked otherwise.
        """
        log.debug("addMessage")
        raise imap4.MailboxException("Client message addition not implemented yet")

    def expunge(self):
        """Remove all messages flagged \\Deleted.
        @return: The list of message sequence numbers which were deleted,
        or a Deferred whose callback will be invoked with such a list.
        """
        log.debug("expunge")
        self.mailbox.removeDeleted()

    def fetch(self, messages, uid):
        """Retrieve one or more messages.
        @param messages: The identifiers of messages to retrieve information
        about
        @param uid: If true, the IDs specified in the query are UIDs;
        """
        log.debug(u"fetch (%s, %s)" % (messages, uid))
        if uid:
            messages.last = self.mailbox.getMaxUid()
            messages.getnext = self.mailbox.getNextExistingUid
            for mess_uid in messages:
                if mess_uid is None:
                    log.debug("stopping iteration")
                    raise StopIteration
                try:
                    yield (
                        mess_uid,
                        Message(
                            mess_uid,
                            self.mailbox.getFlagsUid(mess_uid),
                            self.mailbox.getMessageUid(mess_uid),
                        ),
                    )
                except IndexError:
                    continue
        else:
            messages.last = self.getMessageCount()
            for mess_idx in messages:
                if mess_idx > self.getMessageCount():
                    raise StopIteration
                yield (
                    mess_idx,
                    Message(
                        mess_idx,
                        self.mailbox.getFlags(mess_idx),
                        self.mailbox.getMessage(mess_idx - 1),
                    ),
                )

    def store(self, messages, flags, mode, uid):
        """Set the flags of one or more messages.
        @param messages: The identifiers of the messages to set the flags of.
        @param flags: The flags to set, unset, or add.
        @param mode: If mode is -1, these flags should be removed from the
        specified messages.  If mode is 1, these flags should be added to
        the specified messages.  If mode is 0, all existing flags should be
        cleared and these flags should be added.
        @param uid: If true, the IDs specified in the query are UIDs;
        otherwise they are message sequence IDs.
        @return: A dict mapping message sequence numbers to sequences of str
        representing the flags set on the message after this operation has
        been performed, or a Deferred whose callback will be invoked with
        such a dict.
        """
        log.debug("store")

        flags = [flag.upper() for flag in flags]

        def updateFlags(getF, setF):
            ret = {}
            for mess_id in messages:
                if (uid and mess_id is None) or (
                    not uid and mess_id > self.getMessageCount()
                ):
                    break
                _flags = set(getF(mess_id) if mode else [])
                if mode == -1:
                    _flags.difference_update(set(flags))
                else:
                    _flags.update(set(flags))
                new_flags = list(_flags)
                setF(mess_id, new_flags)
                ret[mess_id] = tuple(new_flags)
            return ret

        if uid:
            messages.last = self.mailbox.getMaxUid()
            messages.getnext = self.mailbox.getNextExistingUid
            ret = updateFlags(self.mailbox.getFlagsUid, self.mailbox.setFlagsUid)
            for listener in self.listeners:
                listener.flagsChanged(ret)
            return ret

        else:
            messages.last = self.getMessageCount()
            ret = updateFlags(self.mailbox.getFlags, self.mailbox.setFlags)
            newFlags = {}
            for idx in ret:
                # we have to convert idx to uid for the listeners
                newFlags[self.mailbox.getUid(idx)] = ret[idx]
            for listener in self.listeners:
                listener.flagsChanged(newFlags)
            return ret

    def getFlags(self):
        """Return the flags defined in this mailbox
        Flags with the \\ prefix are reserved for use as system flags.
        @return: A list of the flags that can be set on messages in this mailbox.
        """
        log.debug("getFlags")
        return [
            "\\SEEN",
            "\\ANSWERED",
            "\\FLAGGED",
            "\\DELETED",
            "\\DRAFT",
        ]  # TODO: add '\\RECENT'

    def getHierarchicalDelimiter(self):
        """Get the character which delimits namespaces for in this mailbox.
        """
        log.debug("getHierarchicalDelimiter")
        return "."


class ImapSatAccount(imap4.MemoryAccount):
    # implements(imap4.IAccount)

    def __init__(self, host, profile):
        log.debug("ImapAccount init")
        self.host = host
        self.profile = profile
        imap4.MemoryAccount.__init__(self, profile)
        self.addMailbox("Inbox")  # We only manage Inbox for the moment
        log.debug("INBOX added")

    def _emptyMailbox(self, name, id):
        return SatMailbox(self.host, name, self.profile)


class ImapRealm(object):
    implements(portal.IRealm)

    def __init__(self, host):
        self.host = host

    def requestAvatar(self, avatarID, mind, *interfaces):
        log.debug("requestAvatar")
        profile = avatarID.decode("utf-8")
        if imap4.IAccount not in interfaces:
            raise NotImplementedError
        return imap4.IAccount, ImapSatAccount(self.host, profile), lambda: None


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
        d.addCallback(lambda password: credentials.checkPassword(password))
        d.addCallback(self._cbPasswordMatch, credentials.username)
        return d


class ImapServerFactory(protocol.ServerFactory):
    protocol = imap4.IMAP4Server

    def __init__(self, host):
        self.host = host

    def startedConnecting(self, connector):
        log.debug(_("IMAP server connection started"))

    def clientConnectionLost(self, connector, reason):
        log.debug(_(u"IMAP server connection lost (reason: %s)"), reason)

    def buildProtocol(self, addr):
        log.debug("Building protocol")
        prot = protocol.ServerFactory.buildProtocol(self, addr)
        prot.portal = portal.Portal(ImapRealm(self.host))
        prot.portal.registerChecker(SatProfileCredentialChecker(self.host))
        return prot
