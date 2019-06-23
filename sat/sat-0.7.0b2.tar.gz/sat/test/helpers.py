#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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


## logging configuration for tests ##
from sat.core import log_config
log_config.satConfigure()

import logging
from sat.core.log import getLogger
getLogger().setLevel(logging.WARNING)  # put this to DEBUG when needed

from sat.core import exceptions
from sat.tools import config as tools_config
from constants import Const as C
from wokkel.xmppim import RosterItem
from wokkel.generic import parseXml
from sat.core.xmpp import SatRosterProtocol
from sat.memory.memory import Params, Memory
from twisted.trial.unittest import FailTest
from twisted.trial import unittest
from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID
from twisted.words.xish import domish
from xml.etree import cElementTree as etree
from collections import Counter
import re


def b2s(value):
    """Convert a bool to a unicode string used in bridge
    @param value: boolean value
    @return: unicode conversion, according to bridge convention

    """
    return  u"True" if value else u"False"


def muteLogging():
    """Temporarily set the logging level to CRITICAL to not pollute the output with expected errors."""
    logger = getLogger()
    logger.original_level = logger.getEffectiveLevel()
    logger.setLevel(logging.CRITICAL)


def unmuteLogging():
    """Restore the logging level after it has been temporarily disabled."""
    logger = getLogger()
    logger.setLevel(logger.original_level)


class DifferentArgsException(FailTest):
    pass


class DifferentXMLException(FailTest):
    pass


class DifferentListException(FailTest):
    pass


class FakeSAT(object):
    """Class to simulate a SAT instance"""

    def __init__(self):
        self.bridge = FakeBridge()
        self.memory = FakeMemory(self)
        self.trigger = FakeTriggerManager()
        self.profiles = {}
        self.reinit()

    def reinit(self):
        """This can be called by tests that check for sent and stored messages,
        uses FakeClient or get/set some other data that need to be cleaned"""
        for profile in self.profiles:
            self.profiles[profile].reinit()
        self.memory.reinit()
        self.stored_messages = []
        self.plugins = {}
        self.profiles = {}

    def delContact(self, to, profile_key):
        #TODO
        pass

    def registerCallback(self, callback, *args, **kwargs):
        pass

    def messageSend(self, to_s, msg, subject=None, mess_type='auto', extra={}, profile_key='@NONE@'):
        self.sendAndStoreMessage({"to": JID(to_s)})

    def _sendMessageToStream(self, mess_data, client):
        """Save the information to check later to whom messages have been sent.

        @param mess_data: message data dictionnary
        @param client: profile's client
        """
        client.xmlstream.send(mess_data['xml'])
        return mess_data

    def _storeMessage(self, mess_data, client):
        """Save the information to check later if entries have been added to the history.

        @param mess_data: message data dictionnary
        @param client: profile's client
        """
        self.stored_messages.append(mess_data["to"])
        return mess_data

    def sendMessageToBridge(self, mess_data, client):
        """Simulate the message being sent to the frontends.

        @param mess_data: message data dictionnary
        @param client: profile's client
        """
        return mess_data  # TODO

    def getProfileName(self, profile_key):
        """Get the profile name from the profile_key"""
        return profile_key

    def getClient(self, profile_key):
        """Convenient method to get client from profile key
        @return: client or None if it doesn't exist"""
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileKeyUnknown
        if profile not in self.profiles:
            self.profiles[profile] = FakeClient(self, profile)
        return self.profiles[profile]

    def getJidNStream(self, profile_key):
        """Convenient method to get jid and stream from profile key
        @return: tuple (jid, xmlstream) from profile, can be None"""
        return (C.PROFILE_DICT[profile_key], None)

    def isConnected(self, profile):
        return True

    def getSentMessages(self, profile_index):
        """Return all the sent messages (in the order they have been sent) and
        empty the list. Called by tests. FakeClient instances associated to each
        profile must have been previously initialized with the method
        FakeSAT.getClient.

        @param profile_index: index of the profile to consider (cf. C.PROFILE)
        @return: the sent messages for given profile, or None"""
        try:
            tmp = self.profiles[C.PROFILE[profile_index]].xmlstream.sent
            self.profiles[C.PROFILE[profile_index]].xmlstream.sent = []
            return tmp
        except IndexError:
            return None

    def getSentMessage(self, profile_index):
        """Pop and return the sent message in first position (works like a FIFO).
        Called by tests. FakeClient instances associated to each profile must have
        been previously initialized with the method FakeSAT.getClient.

        @param profile_index: index of the profile to consider (cf. C.PROFILE)
        @return: the sent message for given profile, or None"""
        try:
            return self.profiles[C.PROFILE[profile_index]].xmlstream.sent.pop(0)
        except IndexError:
            return None

    def getSentMessageXml(self, profile_index):
        """Pop and return the sent message in first position (works like a FIFO).
        Called by tests. FakeClient instances associated to each profile must have
        been previously initialized with the method FakeSAT.getClient.
        @return: XML representation of the sent message for given profile, or None"""
        entry = self.getSentMessage(profile_index)
        return entry.toXml() if entry else None

    def findFeaturesSet(self, features, identity=None, jid_=None, profile=C.PROF_KEY_NONE):
        """Call self.addFeature from your tests to change the return value.

        @return: a set of entities
        """
        client = self.getClient(profile)
        if jid_ is None:
            jid_ = JID(client.jid.host)
        try:
            if set(features).issubset(client.features[jid_]):
                return defer.succeed(set([jid_]))
        except (TypeError, AttributeError, KeyError):
            pass
        return defer.succeed(set())

    def addFeature(self, jid_, feature, profile_key):
        """Add a feature to an entity.

        To be called from your tests when needed.
        """
        client = self.getClient(profile_key)
        if not hasattr(client, 'features'):
            client.features = {}
        if jid_ not in client.features:
            client.features[jid_] = set()
        client.features[jid_].add(feature)


class FakeBridge(object):
    """Class to simulate and test bridge calls"""

    def __init__(self):
        self.expected_calls = {}

    def expectCall(self, name, *check_args, **check_kwargs):
        if hasattr(self, name):  # queue this new call as one already exists
            self.expected_calls.setdefault(name, [])
            self.expected_calls[name].append((check_args, check_kwargs))
            return

        def checkCall(*args, **kwargs):
            if args != check_args or kwargs != check_kwargs:
                print "\n\n--------------------"
                print "Args are not equals:"
                print "args\n----\n%s (sent)\n%s (wanted)" % (args, check_args)
                print "kwargs\n------\n%s (sent)\n%s (wanted)" % (kwargs, check_kwargs)
                print "--------------------\n\n"
                raise DifferentArgsException
            delattr(self, name)

            if name in self.expected_calls:  # register the next call
                args, kwargs = self.expected_calls[name].pop(0)
                if len(self.expected_calls[name]) == 0:
                    del self.expected_calls[name]
                self.expectCall(name, *args, **kwargs)

        setattr(self, name, checkCall)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc=None):
        pass

    def addSignal(self, name, int_suffix, signature):
        pass

    def addTestCallback(self, name, method):
        """This can be used to register callbacks for bridge methods AND signals.
        Contrary to expectCall, this will not check if the method or signal is
        called/sent with the correct arguments, it will instead run the callback
        of your choice."""
        setattr(self, name, method)


class FakeParams(Params):
    """Class to simulate and test params object. The methods of Params that could
    not be run (for example those using the storage attribute must be overwritten
    by a naive simulation of what they should do."""

    def __init__(self, host, storage):
        Params.__init__(self, host, storage)
        self.params = {}  # naive simulation of values storage

    def setParam(self, name, value, category, security_limit=-1, profile_key='@NONE@'):
        profile = self.getProfileName(profile_key)
        self.params.setdefault(profile, {})
        self.params[profile_key][(category, name)] = value

    def getParamA(self, name, category, attr="value", profile_key='@NONE@'):
        profile = self.getProfileName(profile_key)
        return self.params[profile][(category, name)]

    def getProfileName(self, profile_key, return_profile_keys=False):
        if profile_key == '@DEFAULT@':
            return C.PROFILE[0]
        elif profile_key == '@NONE@':
            raise exceptions.ProfileNotSetError
        else:
            return profile_key

    def loadIndParams(self, profile, cache=None):
        self.params[profile] = {}
        return defer.succeed(None)


class FakeMemory(Memory):
    """Class to simulate and test memory object"""

    def __init__(self, host):
        # do not call Memory.__init__, we just want to call the methods that are
        # manipulating basic stuff, the others should be overwritten when needed
        self.host = host
        self.params = FakeParams(host, None)
        self.config = tools_config.parseMainConf()
        self.reinit()

    def reinit(self):
        """Tests that manipulate params, entities, features should
        re-initialise the memory first to not fake the result."""
        self.params.load_default_params()
        self.params.params.clear()
        self.params.frontends_cache = []
        self.entities_data = {}

    def getProfileName(self, profile_key, return_profile_keys=False):
        return self.params.getProfileName(profile_key, return_profile_keys)

    def addToHistory(self, from_jid, to_jid, message, _type='chat', extra=None, timestamp=None, profile="@NONE@"):
        pass

    def addContact(self, contact_jid, attributes, groups, profile_key='@DEFAULT@'):
        pass

    def setPresenceStatus(self, contact_jid, show, priority, statuses, profile_key='@DEFAULT@'):
        pass

    def addWaitingSub(self, type_, contact_jid, profile_key):
        pass

    def delWaitingSub(self, contact_jid, profile_key):
        pass

    def updateEntityData(self, entity_jid, key, value, silent=False, profile_key="@NONE@"):
        self.entities_data.setdefault(entity_jid, {})
        self.entities_data[entity_jid][key] = value

    def getEntityData(self, entity_jid, keys, profile_key):
        result = {}
        for key in keys:
            result[key] = self.entities_data[entity_jid][key]
        return result


class FakeTriggerManager(object):

    def add(self, point_name, callback, priority=0):
        pass

    def point(self, point_name, *args, **kwargs):
        """We always return true to continue the action"""
        return True


class FakeRosterProtocol(SatRosterProtocol):
    """This class is used by FakeClient (one instance per profile)"""

    def __init__(self, host, parent):
        SatRosterProtocol.__init__(self, host)
        self.parent = parent
        self._jids = {}
        self.addItem(parent.jid.userhostJID())

    def addItem(self, jid, *args, **kwargs):
        if not args and not kwargs:
            # defaults values setted for the tests only
            kwargs["subscriptionTo"] = True
            kwargs["subscriptionFrom"] = True
        roster_item = RosterItem(jid, *args, **kwargs)
        attrs = {'to': b2s(roster_item.subscriptionTo), 'from': b2s(roster_item.subscriptionFrom), 'ask': b2s(roster_item.pendingOut)}
        if roster_item.name:
            attrs['name'] = roster_item.name
        self.host.bridge.expectCall("newContact", jid.full(), attrs, roster_item.groups, self.parent.profile)
        self._jids[jid] = roster_item
        self._registerItem(roster_item)


class FakeXmlStream(object):
    """This class is used by FakeClient (one instance per profile)"""

    def __init__(self):
        self.sent = []

    def send(self, obj):
        """Save the sent messages to compare them later.

        @param obj (domish.Element, str or unicode): message to send
        """
        if not isinstance(obj, domish.Element):
            assert(isinstance(obj, str) or isinstance(obj, unicode))
            obj = parseXml(obj)

        if obj.name == 'iq':
            # IQ request expects an answer, return the request itself so
            # you can check if it has been well built by your plugin.
            self.iqDeferreds[obj['id']].callback(obj)

        self.sent.append(obj)
        return defer.succeed(None)

    def addObserver(self, *argv):
        pass


class FakeClient(object):
    """Tests involving more than one profile need one instance of this class per profile"""

    def __init__(self, host, profile=None):
        self.host = host
        self.profile = profile if profile else C.PROFILE[0]
        self.jid = C.PROFILE_DICT[self.profile]
        self.roster = FakeRosterProtocol(host, self)
        self.xmlstream = FakeXmlStream()

    def reinit(self):
        self.xmlstream = FakeXmlStream()

    def send(self, obj):
        return self.xmlstream.send(obj)


class SatTestCase(unittest.TestCase):

    def assertEqualXML(self, xml, expected, ignore_blank=False):
        def equalElt(got_elt, exp_elt):
            if ignore_blank:
                for elt in got_elt, exp_elt:
                    for attr in ('text', 'tail'):
                        value = getattr(elt, attr)
                        try:
                            value = value.strip() or None
                        except AttributeError:
                            value = None
                        setattr(elt, attr, value)
            if (got_elt.tag != exp_elt.tag):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "tag: got [%s] expected: [%s]" % (got_elt.tag, exp_elt.tag)
                return False
            if (got_elt.attrib != exp_elt.attrib):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "attribs: got %s expected %s" % (got_elt.attrib, exp_elt.attrib)
                return False
            if (got_elt.tail != exp_elt.tail or got_elt.text != exp_elt.text):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "text: got [%s] expected: [%s]" % (got_elt.text, exp_elt.text)
                print "tail: got [%s] expected: [%s]" % (got_elt.tail, exp_elt.tail)
                return False
            if (len(got_elt) != len(exp_elt)):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "children len: got %d expected: %d" % (len(got_elt), len(exp_elt))
                return False
            for idx, child in enumerate(got_elt):
                if not equalElt(child, exp_elt[idx]):
                    return False
            return True

        def remove_blank(xml):
            lines = [line.strip() for line in re.sub(r'[ \t\r\f\v]+', ' ', xml).split('\n')]
            return '\n'.join([line for line in lines if line])

        xml_elt = etree.fromstring(remove_blank(xml) if ignore_blank else xml)
        expected_elt = etree.fromstring(remove_blank(expected) if ignore_blank else expected)

        if not equalElt(xml_elt, expected_elt):
            print "---"
            print "XML are not equals:"
            print "got:\n-\n%s\n-\n\n" % etree.tostring(xml_elt, encoding='utf-8')
            print "was expecting:\n-\n%s\n-\n\n" % etree.tostring(expected_elt, encoding='utf-8')
            print "---"
            raise DifferentXMLException

    def assertEqualUnsortedList(self, a, b, msg):
        counter_a = Counter(a)
        counter_b = Counter(b)
        if counter_a != counter_b:
            print "---"
            print "Unsorted lists are not equals:"
            print "got          : %s" % counter_a
            print "was expecting: %s" % counter_b
            if msg:
                print msg
            print "---"
            raise DifferentListException
