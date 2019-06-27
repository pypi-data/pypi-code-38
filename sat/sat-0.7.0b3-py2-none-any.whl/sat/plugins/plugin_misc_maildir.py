#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing Maildir type mail boxes
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

from sat.core.i18n import D_, _
from sat.core.constants import Const as C
from sat.core.log import getLogger
log = getLogger(__name__)
import warnings
warnings.filterwarnings('ignore', 'the MimeWriter', DeprecationWarning, 'twisted')  # FIXME: to be removed, see http://twistedmatrix.com/trac/ticket/4038
from twisted.mail import maildir
import email.message
import email.utils
import os
from sat.core.exceptions import ProfileUnknownError
from sat.memory.persistent import PersistentBinaryDict


PLUGIN_INFO = {
    C.PI_NAME: "Maildir Plugin",
    C.PI_IMPORT_NAME: "Maildir",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "MaildirBox",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Intercept "normal" type messages, and put them in a Maildir type box""")
}

MAILDIR_PATH = "Maildir"
CATEGORY = D_("Mail Server")
NAME = D_('Block "normal" messages propagation')
# FIXME: (very) old and (very) experimental code, need a big cleaning/review or to be deprecated


class MaildirError(Exception):
    pass


class MaildirBox(object):
    params = """
    <params>
    <individual>
    <category name='{category_name}' label='{category_label}'>
        <param name='{name}' label='{label}' value="false" type="bool" security="4" />
    </category>
    </individual>
    </params>
    """.format(category_name=CATEGORY,
               category_label=_(CATEGORY),
               name=NAME,
               label=_(NAME),
              )

    def __init__(self, host):
        log.info(_("Plugin Maildir initialization"))
        self.host = host
        host.memory.updateParams(self.params)

        self.__observed = {}
        self.data = {}  # list of profile spectific data. key = profile, value = PersistentBinaryDict where key=mailbox name,
                     # and value is a dictionnary with the following value
                     #    - cur_idx: value of the current unique integer increment (UID)
                     #    - message_id (as returned by MaildirMailbox): a tuple of (UID, [flag1, flag2, ...])
        self.__mailboxes = {}  # key: profile, value: {boxname: MailboxUser instance}

        #the triggers
        host.trigger.add("MessageReceived", self.messageReceivedTrigger)

    def profileConnected(self, client):
        """Called on client connection, create profile data"""
        profile = client.profile
        self.data[profile] = PersistentBinaryDict("plugin_maildir", profile)
        self.__mailboxes[profile] = {}

        def dataLoaded(ignore):
            if not self.data[profile]:
                #the mailbox is new, we initiate the data
                self.data[profile]["INBOX"] = {"cur_idx": 0}
        self.data[profile].load().addCallback(dataLoaded)

    def profileDisconnected(self, client):
        """Called on profile disconnection, free profile's resources"""
        profile = client.profile
        del self.__mailboxes[profile]
        del self.data[profile]

    def messageReceivedTrigger(self, client, message, post_treat):
        """This trigger catch normal message and put the in the Maildir box.
        If the message is not of "normal" type, do nothing
        @param message: message xmlstrem
        @return: False if it's a normal message, True else"""
        profile = client.profile
        for e in message.elements(C.NS_CLIENT, 'body'):
            mess_type = message.getAttribute('type', 'normal')
            if mess_type != 'normal':
                return True
            self.accessMessageBox("INBOX", profile_key=profile).addMessage(message)
            return not self.host.memory.getParamA(NAME, CATEGORY, profile_key=profile)
        return True

    def accessMessageBox(self, boxname, observer=None, profile_key=C.PROF_KEY_NONE):
        """Create and return a MailboxUser instance
        @param boxname: name of the box
        @param observer: method to call when a NewMessage arrive"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            raise ProfileUnknownError(profile_key)
        if boxname not in self.__mailboxes[profile]:
            self.__mailboxes[profile][boxname] = MailboxUser(self, boxname, observer, profile=profile)
        else:
            if observer:
                self.addObserver(observer, profile, boxname)
        return self.__mailboxes[profile][boxname]

    def _getProfilePath(self, profile):
        """Return a unique path for profile's mailbox
        The path must be unique, usable as a dir name, and bijectional"""
        return profile.replace('/', '_').replace('..', '_')  # FIXME: this is too naive to work well, must be improved

    def _removeBoxAccess(self, boxname, mailboxUser, profile):
        """Remove a reference to a box
        @param name: name of the box
        @param mailboxUser: MailboxUser instance"""
        if boxname not in self.__mailboxes:
            err_msg = _("Trying to remove an mailboxUser not referenced")
            log.error(_(u"INTERNAL ERROR: ") + err_msg)
            raise MaildirError(err_msg)
        assert self.__mailboxes[profile][boxname] == mailboxUser
        del self.__mailboxes[profile][boxname]

    def _checkBoxReference(self, boxname, profile):
        """Check if there is a reference on a box, and return it
        @param boxname: name of the box to check
        @return: MailboxUser instance or None"""
        if profile in self.__mailboxes:
            if boxname in self.__mailboxes[profile]:
                return self.__mailboxes[profile][boxname]

    def __getBoxData(self, boxname, profile):
        """Return the date of a box"""
        try:
            return self.data[profile][boxname]  # the boxname MUST exist in the data
        except KeyError:
            err_msg = _("Boxname doesn't exist in internal data")
            log.error(_(u"INTERNAL ERROR: ") + err_msg)
            raise MaildirError(err_msg)

    def getUid(self, boxname, message_id, profile):
        """Return an unique integer, always ascending, for a message
        This is mainly needed for the IMAP protocol
        @param boxname: name of the box where the message is
        @param message_id: unique id of the message as given by MaildirMailbox
        @return: Integer UID"""
        box_data = self.__getBoxData(boxname, profile)
        if message_id in box_data:
            ret = box_data[message_id][0]
        else:
            box_data['cur_idx'] += 1
            box_data[message_id] = [box_data['cur_idx'], []]
            ret = box_data[message_id]
            self.data[profile].force(boxname)
        return ret

    def getNextUid(self, boxname, profile):
        """Return next unique integer that will generated
        This is mainly needed for the IMAP protocol
        @param boxname: name of the box where the message is
        @return: Integer UID"""
        box_data = self.__getBoxData(boxname, profile)
        return box_data['cur_idx'] + 1

    def getNextExistingUid(self, boxname, uid, profile):
        """Give the next uid of existing message
        @param boxname: name of the box where the message is
        @param uid: uid to start from
        @return: uid or None if the is no more message"""
        box_data = self.__getBoxData(boxname, profile)
        idx = uid + 1
        while self.getIdFromUid(boxname, idx, profile) is None:  # TODO: this is highly inefficient because getIdfromUid is inefficient, fix this
            idx += 1
            if idx > box_data['cur_idx']:
                return None
        return idx

    def getMaxUid(self, boxname, profile):
        """Give the max existing uid
        @param boxname: name of the box where the message is
        @return: uid"""
        box_data = self.__getBoxData(boxname, profile)
        return box_data['cur_idx']

    def getIdFromUid(self, boxname, message_uid, profile):
        """Return the message unique id from it's integer UID
        @param boxname: name of the box where the message is
        @param message_uid: unique integer identifier
        @return: unique id of the message as given by MaildirMailbox or None if not found"""
        box_data = self.__getBoxData(boxname, profile)
        for message_id in box_data.keys():  # TODO: this is highly inefficient on big mailbox, must be replaced in the future
            if message_id == 'cur_idx':
                continue
            if box_data[message_id][0] == message_uid:
                return message_id
        return None

    def getFlags(self, boxname, mess_id, profile):
        """Return the messages flags
        @param boxname: name of the box where the message is
        @param message_idx: message id as given by MaildirMailbox
        @return: list of strings"""
        box_data = self.__getBoxData(boxname, profile)
        if mess_id not in box_data:
            raise MaildirError("Trying to get flags from an unexisting message")
        return box_data[mess_id][1]

    def setFlags(self, boxname, mess_id, flags, profile):
        """Change the flags of the message
        @param boxname: name of the box where the message is
        @param message_idx: message id as given by MaildirMailbox
        @param flags: list of strings
        """
        box_data = self.__getBoxData(boxname, profile)
        assert(type(flags) == list)
        flags = [flag.upper() for flag in flags]  # we store every flag UPPERCASE
        if mess_id not in box_data:
            raise MaildirError("Trying to set flags for an unexisting message")
        box_data[mess_id][1] = flags
        self.data[profile].force(boxname)

    def getMessageIdsWithFlag(self, boxname, flag, profile):
        """Return ids of messages where a flag is set
        @param boxname: name of the box where the message is
        @param flag: flag to check
        @return: list of id (as given by MaildirMailbox)"""
        box_data = self.__getBoxData(boxname, profile)
        assert(isinstance(flag, basestring))
        flag = flag.upper()
        result = []
        for key in box_data:
            if key == 'cur_idx':
                continue
            if flag in box_data[key][1]:
                result.append(key)
        return result

    def purgeDeleted(self, boxname, profile):
        """Remove data for messages with flag "\\Deleted"
        @param boxname: name of the box where the message is
        """
        box_data = self.__getBoxData(boxname, profile)
        for mess_id in self.getMessageIdsWithFlag(boxname, "\\Deleted", profile):
            del(box_data[mess_id])
        self.data[profile].force(boxname)

    def cleanTable(self, boxname, existant_id, profile):
        """Remove mails which no longuer exist from the table
        @param boxname: name of the box to clean
        @param existant_id: list of id which actually exist"""
        box_data = self.__getBoxData(boxname, profile)
        to_remove = []
        for key in box_data:
            if key not in existant_id and key != "cur_idx":
                to_remove.append(key)
        for key in to_remove:
            del box_data[key]

    def addObserver(self, callback, profile, boxname, signal="NEW_MESSAGE"):
        """Add an observer for maildir box changes
        @param callback: method to call when the the box is updated
        @param boxname: name of the box to observe
        @param signal: which signal is observed by the caller"""
        if (profile, boxname) not in self.__observed:
            self.__observed[(profile, boxname)] = {}
        if signal not in self.__observed[(profile, boxname)]:
            self.__observed[(profile, boxname)][signal] = set()
        self.__observed[(profile, boxname)][signal].add(callback)

    def removeObserver(self, callback, profile, boxname, signal="NEW_MESSAGE"):
        """Remove an observer of maildir box changes
        @param callback: method to remove from obervers
        @param boxname: name of the box which was observed
        @param signal: which signal was observed by the caller"""
        if (profile, boxname) not in self.__observed:
            err_msg = _(u"Trying to remove an observer for an inexistant mailbox")
            log.error(_(u"INTERNAL ERROR: ") + err_msg)
            raise MaildirError(err_msg)
        if signal not in self.__observed[(profile, boxname)]:
            err_msg = _(u"Trying to remove an inexistant observer, no observer for this signal")
            log.error(_(u"INTERNAL ERROR: ") + err_msg)
            raise MaildirError(err_msg)
        if not callback in self.__observed[(profile, boxname)][signal]:
            err_msg = _(u"Trying to remove an inexistant observer")
            log.error(_(u"INTERNAL ERROR: ") + err_msg)
            raise MaildirError(err_msg)
        self.__observed[(profile, boxname)][signal].remove(callback)

    def emitSignal(self, profile, boxname, signal_name):
        """Emit the signal to observer"""
        log.debug(u'emitSignal %s %s %s' % (profile, boxname, signal_name))
        try:
            for observer_cb in self.__observed[(profile, boxname)][signal_name]:
                observer_cb()
        except KeyError:
            pass


class MailboxUser(object):
    """This class is used to access a mailbox"""

    def xmppMessage2mail(self, message):
        """Convert the XMPP's XML message to a basic rfc2822 message
        @param xml: domish.Element of the message
        @return: string email"""
        mail = email.message.Message()
        mail['MIME-Version'] = "1.0"
        mail['Content-Type'] = "text/plain; charset=UTF-8; format=flowed"
        mail['Content-Transfer-Encoding'] = "8bit"
        mail['From'] = message['from'].encode('utf-8')
        mail['To'] = message['to'].encode('utf-8')
        mail['Date'] = email.utils.formatdate().encode('utf-8')
        #TODO: save thread id
        for e in message.elements():
            if e.name == "body":
                mail.set_payload(e.children[0].encode('utf-8'))
            elif e.name == "subject":
                mail['Subject'] = e.children[0].encode('utf-8')
        return mail.as_string()

    def __init__(self, _maildir, name, observer=None, profile=C.PROF_KEY_NONE):
        """@param _maildir: the main MaildirBox instance
           @param name: name of the mailbox
           @param profile: real profile (ie not a profile_key)
           THIS OBJECT MUST NOT BE USED DIRECTLY: use MaildirBox.accessMessageBox instead"""
        if _maildir._checkBoxReference(name, profile):
            log.error(u"INTERNAL ERROR: MailboxUser MUST NOT be instancied directly")
            raise MaildirError('double MailboxUser instanciation')
        if name != "INBOX":
            raise NotImplementedError
        self.name = name
        self.profile = profile
        self.maildir = _maildir
        profile_path = self.maildir._getProfilePath(profile)
        full_profile_path = os.path.join(self.maildir.host.memory.getConfig('', 'local_dir'), 'maildir', profile_path)
        if not os.path.exists(full_profile_path):
            os.makedirs(full_profile_path, 0700)
        mailbox_path = os.path.join(full_profile_path, MAILDIR_PATH)
        self.mailbox_path = mailbox_path
        self.mailbox = maildir.MaildirMailbox(mailbox_path)
        self.observer = observer
        self.__uid_table_update()

        if observer:
            log.debug(u"adding observer for %s (%s)" % (name, profile))
            self.maildir.addObserver(observer, profile, name, "NEW_MESSAGE")

    def __uid_table_update(self):
        existant_id = []
        for mess_idx in range(self.getMessageCount()):
            #we update the uid table
            existant_id.append(self.getId(mess_idx))
            self.getUid(mess_idx)
        self.maildir.cleanTable(self.name, existant_id, profile=self.profile)

    def __del__(self):
        if self.observer:
            log.debug(u"removing observer for %s" % self.name)
            self._maildir.removeObserver(self.observer, self.name, "NEW_MESSAGE")
        self.maildir._removeBoxAccess(self.name, self, profile=self.profile)

    def addMessage(self, message):
        """Add a message to the box
        @param message: XMPP XML message"""
        self.mailbox.appendMessage(self.xmppMessage2mail(message)).addCallback(self.emitSignal, "NEW_MESSAGE")

    def emitSignal(self, ignore, signal):
        """Emit the signal to the observers"""
        if signal == "NEW_MESSAGE":
            self.getUid(self.getMessageCount() - 1)  # XXX: we make an uid for the last message added
        self.maildir.emitSignal(self.profile, self.name, signal)

    def getId(self, mess_idx):
        """Return the Unique ID of the message
        @mess_idx: message index"""
        return self.mailbox.getUidl(mess_idx)

    def getUid(self, mess_idx):
        """Return a unique interger id for the message, always ascending"""
        mess_id = self.getId(mess_idx)
        return self.maildir.getUid(self.name, mess_id, profile=self.profile)

    def getNextUid(self):
        return self.maildir.getNextUid(self.name, profile=self.profile)

    def getNextExistingUid(self, uid):
        return self.maildir.getNextExistingUid(self.name, uid, profile=self.profile)

    def getMaxUid(self):
        return self.maildir.getMaxUid(self.name, profile=self.profile)

    def getMessageCount(self):
        """Return number of mails present in this box"""
        return len(self.mailbox.list)

    def getMessageIdx(self, mess_idx):
        """Return the full message
        @mess_idx: message index"""
        return self.mailbox.getMessage(mess_idx)

    def getIdxFromUid(self, mess_uid):
        """Return the message index from the uid
        @param mess_uid: message unique identifier
        @return: message index, as managed by MaildirMailbox"""
        for mess_idx in range(self.getMessageCount()):
            if self.getUid(mess_idx) == mess_uid:
                return mess_idx
        raise IndexError

    def getIdxFromId(self, mess_id):
        """Return the message index from the unique index
        @param mess_id: message unique index as given by MaildirMailbox
        @return: message sequence index"""
        for mess_idx in range(self.getMessageCount()):
            if self.mailbox.getUidl(mess_idx) == mess_id:
                return mess_idx
        raise IndexError

    def getMessage(self, mess_idx):
        """Return the full message
        @param mess_idx: message index"""
        return self.mailbox.getMessage(mess_idx)

    def getMessageUid(self, mess_uid):
        """Return the full message
        @param mess_idx: message unique identifier"""
        return self.mailbox.getMessage(self.getIdxFromUid(mess_uid))

    def getFlags(self, mess_idx):
        """Return the flags of the message
        @param mess_idx: message index
        @return: list of strings"""
        id = self.getId(mess_idx)
        return self.maildir.getFlags(self.name, id, profile=self.profile)

    def getFlagsUid(self, mess_uid):
        """Return the flags of the message
        @param mess_uid: message unique identifier
        @return: list of strings"""
        id = self.maildir.getIdFromUid(self.name, mess_uid, profile=self.profile)
        return self.maildir.getFlags(self.name, id, profile=self.profile)

    def setFlags(self, mess_idx, flags):
        """Change the flags of the message
        @param mess_idx: message index
        @param flags: list of strings
        """
        id = self.getId(mess_idx)
        self.maildir.setFlags(self.name, id, flags, profile=self.profile)

    def setFlagsUid(self, mess_uid, flags):
        """Change the flags of the message
        @param mess_uid: message unique identifier
        @param flags: list of strings
        """
        id = self.maildir.getIdFromUid(self.name, mess_uid, profile=self.profile)
        return self.maildir.setFlags(self.name, id, flags, profile=self.profile)

    def getMessageIdsWithFlag(self, flag):
        """Return ids of messages where a flag is set
        @param flag: flag to check
        @return: list of id (as given by MaildirMailbox)"""
        return self.maildir.getMessageIdsWithFlag(self.name, flag, profile=self.profile)

    def removeDeleted(self):
        """Actually delete message flagged "\\Deleted"
        Also purge the internal data of these messages
        """
        for mess_id in self.getMessageIdsWithFlag("\\Deleted"):
            print ("Deleting %s" % mess_id)
            self.mailbox.deleteMessage(self.getIdxFromId(mess_id))
        self.mailbox = maildir.MaildirMailbox(self.mailbox_path)  # We need to reparse the dir to have coherent indexing
        self.maildir.purgeDeleted(self.name, profile=self.profile)

    def emptyTrash(self):
        """Delete everything in the .Trash dir"""
        pass #TODO
