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

from sat.core.i18n import _

from sat.core.log import getLogger

log = getLogger(__name__)

import os.path
import copy
from collections import namedtuple
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from uuid import uuid4
from twisted.python import failure
from twisted.internet import defer, reactor, error
from twisted.words.protocols.jabber import jid
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.memory.sqlite import SqliteStorage
from sat.memory.persistent import PersistentDict
from sat.memory.params import Params
from sat.memory.disco import Discovery
from sat.memory.crypto import BlockCipher
from sat.memory.crypto import PasswordHasher
from sat.tools import config as tools_config
import shortuuid
import mimetypes
import time


PresenceTuple = namedtuple("PresenceTuple", ("show", "priority", "statuses"))
MSG_NO_SESSION = "Session id doesn't exist or is finished"


class Sessions(object):
    """Sessions are data associated to key used for a temporary moment, with optional profile checking."""

    DEFAULT_TIMEOUT = 600

    def __init__(self, timeout=None, resettable_timeout=True):
        """
        @param timeout (int): nb of seconds before session destruction
        @param resettable_timeout (bool): if True, the timeout is reset on each access
        """
        self._sessions = dict()
        self.timeout = timeout or Sessions.DEFAULT_TIMEOUT
        self.resettable_timeout = resettable_timeout

    def newSession(self, session_data=None, session_id=None, profile=None):
        """Create a new session

        @param session_data: mutable data to use, default to a dict
        @param session_id (str): force the session_id to the given string
        @param profile: if set, the session is owned by the profile,
                        and profileGet must be used instead of __getitem__
        @return: session_id, session_data
        """
        if session_id is None:
            session_id = str(uuid4())
        elif session_id in self._sessions:
            raise exceptions.ConflictError(
                u"Session id {} is already used".format(session_id)
            )
        timer = reactor.callLater(self.timeout, self._purgeSession, session_id)
        if session_data is None:
            session_data = {}
        self._sessions[session_id] = (
            (timer, session_data) if profile is None else (timer, session_data, profile)
        )
        return session_id, session_data

    def _purgeSession(self, session_id):
        try:
            timer, session_data, profile = self._sessions[session_id]
        except ValueError:
            timer, session_data = self._sessions[session_id]
            profile = None
        try:
            timer.cancel()
        except error.AlreadyCalled:
            # if the session is time-outed, the timer has been called
            pass
        del self._sessions[session_id]
        log.debug(
            u"Session {} purged{}".format(
                session_id,
                u" (profile {})".format(profile) if profile is not None else u"",
            )
        )

    def __len__(self):
        return len(self._sessions)

    def __contains__(self, session_id):
        return session_id in self._sessions

    def profileGet(self, session_id, profile):
        try:
            timer, session_data, profile_set = self._sessions[session_id]
        except ValueError:
            raise exceptions.InternalError(
                "You need to use __getitem__ when profile is not set"
            )
        except KeyError:
            raise failure.Failure(KeyError(MSG_NO_SESSION))
        if profile_set != profile:
            raise exceptions.InternalError("current profile differ from set profile !")
        if self.resettable_timeout:
            timer.reset(self.timeout)
        return session_data

    def __getitem__(self, session_id):
        try:
            timer, session_data = self._sessions[session_id]
        except ValueError:
            raise exceptions.InternalError(
                "You need to use profileGet instead of __getitem__ when profile is set"
            )
        except KeyError:
            raise failure.Failure(KeyError(MSG_NO_SESSION))
        if self.resettable_timeout:
            timer.reset(self.timeout)
        return session_data

    def __setitem__(self, key, value):
        raise NotImplementedError("You need do use newSession to create a session")

    def __delitem__(self, session_id):
        """ delete the session data """
        self._purgeSession(session_id)

    def keys(self):
        return self._sessions.keys()

    def iterkeys(self):
        return self._sessions.iterkeys()


class ProfileSessions(Sessions):
    """ProfileSessions extends the Sessions class, but here the profile can be
    used as the key to retrieve data or delete a session (instead of session id).
    """

    def _profileGetAllIds(self, profile):
        """Return a list of the sessions ids that are associated to the given profile.

        @param profile: %(doc_profile)s
        @return: a list containing the sessions ids
        """
        ret = []
        for session_id in self._sessions.iterkeys():
            try:
                timer, session_data, profile_set = self._sessions[session_id]
            except ValueError:
                continue
            if profile == profile_set:
                ret.append(session_id)
        return ret

    def profileGetUnique(self, profile):
        """Return the data of the unique session that is associated to the given profile.

        @param profile: %(doc_profile)s
        @return:
            - mutable data (default: dict) of the unique session
            - None if no session is associated to the profile
            - raise an error if more than one session are found
        """
        ids = self._profileGetAllIds(profile)
        if len(ids) > 1:
            raise exceptions.InternalError(
                "profileGetUnique has been used but more than one session has been found!"
            )
        return (
            self.profileGet(ids[0], profile) if len(ids) == 1 else None
        )  # XXX: timeout might be reset

    def profileDelUnique(self, profile):
        """Delete the unique session that is associated to the given profile.

        @param profile: %(doc_profile)s
        @return: None, but raise an error if more than one session are found
        """
        ids = self._profileGetAllIds(profile)
        if len(ids) > 1:
            raise exceptions.InternalError(
                "profileDelUnique has been used but more than one session has been found!"
            )
        if len(ids) == 1:
            del self._sessions[ids[0]]


class PasswordSessions(ProfileSessions):

    # FIXME: temporary hack for the user personal key not to be lost. The session
    # must actually be purged and later, when the personal key is needed, the
    # profile password should be asked again in order to decrypt it.
    def __init__(self, timeout=None):
        ProfileSessions.__init__(self, timeout, resettable_timeout=False)

    def _purgeSession(self, session_id):
        log.debug(
            "FIXME: PasswordSessions should ask for the profile password after the session expired"
        )


# XXX: tmp update code, will be removed in the future
# When you remove this, please add the default value for
# 'local_dir' in sat.core.constants.Const.DEFAULT_CONFIG
def fixLocalDir(silent=True):
    """Retro-compatibility with the previous local_dir default value.

    @param silent (boolean): toggle logging output (must be True when called from sat.sh)
    """
    user_config = SafeConfigParser()
    try:
        user_config.read(C.CONFIG_FILES)
    except:
        pass  # file is readable but its structure if wrong
    try:
        current_value = user_config.get("DEFAULT", "local_dir")
    except (NoOptionError, NoSectionError):
        current_value = ""
    if current_value:
        return  # nothing to do
    old_default = "~/.sat"
    if os.path.isfile(os.path.expanduser(old_default) + "/" + C.SAVEFILE_DATABASE):
        if not silent:
            log.warning(
                _(
                    u"A database has been found in the default local_dir for previous versions (< 0.5)"
                )
            )
        tools_config.fixConfigOption("", "local_dir", old_default, silent)


class Memory(object):
    """This class manage all the persistent information"""

    def __init__(self, host):
        log.info(_("Memory manager init"))
        self.initialized = defer.Deferred()
        self.host = host
        self._entities_cache = {}  # XXX: keep presence/last resource/other data in cache
        #     /!\ an entity is not necessarily in roster
        #     main key is bare jid, value is a dict
        #     where main key is resource, or None for bare jid
        self._key_signals = set()  # key which need a signal to frontends when updated
        self.subscriptions = {}
        self.auth_sessions = PasswordSessions()  # remember the authenticated profiles
        self.disco = Discovery(host)
        fixLocalDir(False)  # XXX: tmp update code, will be removed in the future
        self.config = tools_config.parseMainConf()
        database_file = os.path.expanduser(
            os.path.join(self.getConfig("", "local_dir"), C.SAVEFILE_DATABASE)
        )
        self.storage = SqliteStorage(database_file, host.version)
        PersistentDict.storage = self.storage
        self.params = Params(host, self.storage)
        log.info(_("Loading default params template"))
        self.params.load_default_params()
        d = self.storage.initialized.addCallback(lambda ignore: self.load())
        self.memory_data = PersistentDict("memory")
        d.addCallback(lambda ignore: self.memory_data.load())
        d.addCallback(lambda ignore: self.disco.load())
        d.chainDeferred(self.initialized)

    ## Configuration ##

    def getConfig(self, section, name, default=None):
        """Get the main configuration option

        @param section: section of the config file (None or '' for DEFAULT)
        @param name: name of the option
        @param default: value to use if not found
        @return: str, list or dict
        """
        return tools_config.getConfig(self.config, section, name, default)

    def load_xml(self, filename):
        """Load parameters template from xml file

        @param filename (str): input file
        @return: bool: True in case of success
        """
        if not filename:
            return False
        filename = os.path.expanduser(filename)
        if os.path.exists(filename):
            try:
                self.params.load_xml(filename)
                log.debug(_(u"Parameters loaded from file: %s") % filename)
                return True
            except Exception as e:
                log.error(_(u"Can't load parameters from file: %s") % e)
        return False

    def save_xml(self, filename):
        """Save parameters template to xml file

        @param filename (str): output file
        @return: bool: True in case of success
        """
        if not filename:
            return False
        # TODO: need to encrypt files (at least passwords !) and set permissions
        filename = os.path.expanduser(filename)
        try:
            self.params.save_xml(filename)
            log.debug(_(u"Parameters saved to file: %s") % filename)
            return True
        except Exception as e:
            log.error(_(u"Can't save parameters to file: %s") % e)
        return False

    def load(self):
        """Load parameters and all memory things from db"""
        # parameters data
        return self.params.loadGenParams()

    def loadIndividualParams(self, profile):
        """Load individual parameters for a profile
        @param profile: %(doc_profile)s"""
        return self.params.loadIndParams(profile)

    ## Profiles/Sessions management ##

    def startSession(self, password, profile):
        """"Iniatialise session for a profile

        @param password(unicode): profile session password
            or empty string is no password is set
        @param profile: %(doc_profile)s
        @raise exceptions.ProfileUnknownError if profile doesn't exists
        @raise exceptions.PasswordError: the password does not match
        """
        profile = self.getProfileName(profile)

        def createSession(__):
            """Called once params are loaded."""
            self._entities_cache[profile] = {}
            log.info(u"[{}] Profile session started".format(profile))
            return False

        def backendInitialised(__):
            def doStartSession(__=None):
                if self.isSessionStarted(profile):
                    log.info("Session already started!")
                    return True
                try:
                    # if there is a value at this point in self._entities_cache,
                    # it is the loadIndividualParams Deferred, the session is starting
                    session_d = self._entities_cache[profile]
                except KeyError:
                    # else we do request the params
                    session_d = self._entities_cache[profile] = self.loadIndividualParams(
                        profile
                    )
                    session_d.addCallback(createSession)
                finally:
                    return session_d

            auth_d = self.profileAuthenticate(password, profile)
            auth_d.addCallback(doStartSession)
            return auth_d

        if self.host.initialised.called:
            return defer.succeed(None).addCallback(backendInitialised)
        else:
            return self.host.initialised.addCallback(backendInitialised)

    def stopSession(self, profile):
        """Delete a profile session

        @param profile: %(doc_profile)s
        """
        if self.host.isConnected(profile):
            log.debug(u"Disconnecting profile because of session stop")
            self.host.disconnect(profile)
        self.auth_sessions.profileDelUnique(profile)
        try:
            self._entities_cache[profile]
        except KeyError:
            log.warning(u"Profile was not in cache")

    def _isSessionStarted(self, profile_key):
        return self.isSessionStarted(self.getProfileName(profile_key))

    def isSessionStarted(self, profile):
        try:
            # XXX: if the value in self._entities_cache is a Deferred,
            #      the session is starting but not started yet
            return not isinstance(self._entities_cache[profile], defer.Deferred)
        except KeyError:
            return False

    def profileAuthenticate(self, password, profile):
        """Authenticate the profile.

        @param password (unicode): the SàT profile password
        @param profile: %(doc_profile)s
        @return (D): a deferred None in case of success, a failure otherwise.
        @raise exceptions.PasswordError: the password does not match
        """
        session_data = self.auth_sessions.profileGetUnique(profile)
        if not password and session_data:
            # XXX: this allows any frontend to connect with the empty password as soon as
            # the profile has been authenticated at least once before. It is OK as long as
            # submitting a form with empty passwords is restricted to local frontends.
            return defer.succeed(None)

        def check_result(result):
            if not result:
                log.warning(u"Authentication failure of profile {}".format(profile))
                raise failure.Failure(
                    exceptions.PasswordError(
                        u"The provided profile password doesn't match."
                    )
                )
            if (
                not session_data
            ):  # avoid to create two profile sessions when password if specified
                return self.newAuthSession(password, profile)

        d = self.asyncGetParamA(
            C.PROFILE_PASS_PATH[1], C.PROFILE_PASS_PATH[0], profile_key=profile
        )
        d.addCallback(lambda sat_cipher: PasswordHasher.verify(password, sat_cipher))
        return d.addCallback(check_result)

    def newAuthSession(self, key, profile):
        """Start a new session for the authenticated profile.

        The personal key is loaded encrypted from a PersistentDict before being decrypted.

        @param key: the key to decrypt the personal key
        @param profile: %(doc_profile)s
        @return: a deferred None value
        """

        def gotPersonalKey(personal_key):
            """Create the session for this profile and store the personal key"""
            self.auth_sessions.newSession(
                {C.MEMORY_CRYPTO_KEY: personal_key}, profile=profile
            )
            log.debug(u"auth session created for profile %s" % profile)

        d = PersistentDict(C.MEMORY_CRYPTO_NAMESPACE, profile).load()
        d.addCallback(lambda data: BlockCipher.decrypt(key, data[C.MEMORY_CRYPTO_KEY]))
        return d.addCallback(gotPersonalKey)

    def purgeProfileSession(self, profile):
        """Delete cache of data of profile
        @param profile: %(doc_profile)s"""
        log.info(_("[%s] Profile session purge" % profile))
        self.params.purgeProfile(profile)
        try:
            del self._entities_cache[profile]
        except KeyError:
            log.error(
                _(
                    u"Trying to purge roster status cache for a profile not in memory: [%s]"
                )
                % profile
            )

    def getProfilesList(self, clients=True, components=False):
        """retrieve profiles list

        @param clients(bool): if True return clients profiles
        @param components(bool): if True return components profiles
        @return (list[unicode]): selected profiles
        """
        if not clients and not components:
            log.warning(_(u"requesting no profiles at all"))
            return []
        profiles = self.storage.getProfilesList()
        if clients and components:
            return sorted(profiles)
        isComponent = self.storage.profileIsComponent
        if clients:
            p_filter = lambda p: not isComponent(p)
        else:
            p_filter = lambda p: isComponent(p)

        return sorted(p for p in profiles if p_filter(p))

    def getProfileName(self, profile_key, return_profile_keys=False):
        """Return name of profile from keyword

        @param profile_key: can be the profile name or a keyword (like @DEFAULT@)
        @param return_profile_keys: if True, return unmanaged profile keys (like "@ALL@"). This keys must be managed by the caller
        @return: requested profile name
        @raise exceptions.ProfileUnknownError if profile doesn't exists
        """
        return self.params.getProfileName(profile_key, return_profile_keys)

    def profileSetDefault(self, profile):
        """Set default profile

        @param profile: %(doc_profile)s
        """
        # we want to be sure that the profile exists
        profile = self.getProfileName(profile)

        self.memory_data["Profile_default"] = profile

    def createProfile(self, name, password, component=None):
        """Create a new profile

        @param name(unicode): profile name
        @param password(unicode): profile password
            Can be empty to disable password
        @param component(None, unicode): set to entry point if this is a component
        @return: Deferred
        @raise exceptions.NotFound: component is not a known plugin import name
        """
        if not name:
            raise ValueError(u"Empty profile name")
        if name[0] == "@":
            raise ValueError(u"A profile name can't start with a '@'")
        if "\n" in name:
            raise ValueError(u"A profile name can't contain line feed ('\\n')")

        if name in self._entities_cache:
            raise exceptions.ConflictError(u"A session for this profile exists")

        if component:
            if not component in self.host.plugins:
                raise exceptions.NotFound(
                    _(
                        u"Can't find component {component} entry point".format(
                            component=component
                        )
                    )
                )
            # FIXME: PLUGIN_INFO is not currently accessible after import, but type shoul be tested here
            #  if self.host.plugins[component].PLUGIN_INFO[u"type"] != C.PLUG_TYPE_ENTRY_POINT:
            #      raise ValueError(_(u"Plugin {component} is not an entry point !".format(
            #          component = component)))

        d = self.params.createProfile(name, component)

        def initPersonalKey(__):
            # be sure to call this after checking that the profile doesn't exist yet
            personal_key = BlockCipher.getRandomKey(
                base64=True
            )  # generated once for all and saved in a PersistentDict
            self.auth_sessions.newSession(
                {C.MEMORY_CRYPTO_KEY: personal_key}, profile=name
            )  # will be encrypted by setParam

        def startFakeSession(__):
            # avoid ProfileNotConnected exception in setParam
            self._entities_cache[name] = None
            self.params.loadIndParams(name)

        def stopFakeSession(__):
            del self._entities_cache[name]
            self.params.purgeProfile(name)

        d.addCallback(initPersonalKey)
        d.addCallback(startFakeSession)
        d.addCallback(
            lambda __: self.setParam(
                C.PROFILE_PASS_PATH[1], password, C.PROFILE_PASS_PATH[0], profile_key=name
            )
        )
        d.addCallback(stopFakeSession)
        d.addCallback(lambda __: self.auth_sessions.profileDelUnique(name))
        return d

    def asyncDeleteProfile(self, name, force=False):
        """Delete an existing profile

        @param name: Name of the profile
        @param force: force the deletion even if the profile is connected.
        To be used for direct calls only (not through the bridge).
        @return: a Deferred instance
        """

        def cleanMemory(__):
            self.auth_sessions.profileDelUnique(name)
            try:
                del self._entities_cache[name]
            except KeyError:
                pass

        d = self.params.asyncDeleteProfile(name, force)
        d.addCallback(cleanMemory)
        return d

    def isComponent(self, profile_name):
        """Tell if a profile is a component

        @param profile_name(unicode): name of the profile
        @return (bool): True if profile is a component
        @raise exceptions.NotFound: profile doesn't exist
        """
        return self.storage.profileIsComponent(profile_name)

    def getEntryPoint(self, profile_name):
        """Get a component entry point

        @param profile_name(unicode): name of the profile
        @return (bool): True if profile is a component
        @raise exceptions.NotFound: profile doesn't exist
        """
        return self.storage.getEntryPoint(profile_name)

    ## History ##

    def addToHistory(self, client, data):
        return self.storage.addToHistory(data, client.profile)

    def _historyGet(self, from_jid_s, to_jid_s, limit=C.HISTORY_LIMIT_NONE, between=True,
                    filters=None, profile=C.PROF_KEY_NONE):
        return self.historyGet(jid.JID(from_jid_s), jid.JID(to_jid_s), limit, between,
                               filters, profile)

    def historyGet(self, from_jid, to_jid, limit=C.HISTORY_LIMIT_NONE, between=True,
                   filters=None, profile=C.PROF_KEY_NONE):
        """Retrieve messages in history

        @param from_jid (JID): source JID (full, or bare for catchall)
        @param to_jid (JID): dest JID (full, or bare for catchall)
        @param limit (int): maximum number of messages to get:
            - 0 for no message (returns the empty list)
            - C.HISTORY_LIMIT_NONE or None for unlimited
            - C.HISTORY_LIMIT_DEFAULT to use the HISTORY_LIMIT parameter value
        @param between (bool): confound source and dest (ignore the direction)
        @param filters (dict[unicode, unicode]): pattern to filter the history results
            (see bridge API for details)
        @param profile (str): %(doc_profile)s
        @return (D(list)): list of message data as in [messageNew]
        """
        assert profile != C.PROF_KEY_NONE
        if limit == C.HISTORY_LIMIT_DEFAULT:
            limit = int(self.getParamA(C.HISTORY_LIMIT, "General", profile_key=profile))
        elif limit == C.HISTORY_LIMIT_NONE:
            limit = None
        if limit == 0:
            return defer.succeed([])
        return self.storage.historyGet(from_jid, to_jid, limit, between, filters, profile)

    ## Statuses ##

    def _getPresenceStatuses(self, profile_key):
        ret = self.getPresenceStatuses(profile_key)
        return {entity.full(): data for entity, data in ret.iteritems()}

    def getPresenceStatuses(self, profile_key):
        """Get all the presence statuses of a profile

        @param profile_key: %(doc_profile_key)s
        @return: presence data: key=entity JID, value=presence data for this entity
        """
        client = self.host.getClient(profile_key)
        profile_cache = self._getProfileCache(client)
        entities_presence = {}

        for entity_jid, entity_data in profile_cache.iteritems():
            for resource, resource_data in entity_data.iteritems():
                full_jid = copy.copy(entity_jid)
                full_jid.resource = resource
                try:
                    presence_data = self.getEntityDatum(full_jid, "presence", profile_key)
                except KeyError:
                    continue
                entities_presence.setdefault(entity_jid, {})[
                    resource or ""
                ] = presence_data

        return entities_presence

    def setPresenceStatus(self, entity_jid, show, priority, statuses, profile_key):
        """Change the presence status of an entity

        @param entity_jid: jid.JID of the entity
        @param show: show status
        @param priority: priority
        @param statuses: dictionary of statuses
        @param profile_key: %(doc_profile_key)s
        """
        presence_data = PresenceTuple(show, priority, statuses)
        self.updateEntityData(
            entity_jid, "presence", presence_data, profile_key=profile_key
        )
        if entity_jid.resource and show != C.PRESENCE_UNAVAILABLE:
            # If a resource is available, bare jid should not have presence information
            try:
                self.delEntityDatum(entity_jid.userhostJID(), "presence", profile_key)
            except (KeyError, exceptions.UnknownEntityError):
                pass

    ## Resources ##

    def _getAllResource(self, jid_s, profile_key):
        client = self.host.getClient(profile_key)
        jid_ = jid.JID(jid_s)
        return self.getAllResources(client, jid_)

    def getAllResources(self, client, entity_jid):
        """Return all resource from jid for which we have had data in this session

        @param entity_jid: bare jid of the entity
        return (list[unicode]): list of resources

        @raise exceptions.UnknownEntityError: if entity is not in cache
        @raise ValueError: entity_jid has a resource
        """
        # FIXME: is there a need to keep cache data for resources which are not connected anymore?
        if entity_jid.resource:
            raise ValueError(
                "getAllResources must be used with a bare jid (got {})".format(entity_jid)
            )
        profile_cache = self._getProfileCache(client)
        try:
            entity_data = profile_cache[entity_jid.userhostJID()]
        except KeyError:
            raise exceptions.UnknownEntityError(
                u"Entity {} not in cache".format(entity_jid)
            )
        resources = set(entity_data.keys())
        resources.discard(None)
        return resources

    def getAvailableResources(self, client, entity_jid):
        """Return available resource for entity_jid

        This method differs from getAllResources by returning only available resources
        @param entity_jid: bare jid of the entit
        return (list[unicode]): list of available resources

        @raise exceptions.UnknownEntityError: if entity is not in cache
        """
        available = []
        for resource in self.getAllResources(client, entity_jid):
            full_jid = copy.copy(entity_jid)
            full_jid.resource = resource
            try:
                presence_data = self.getEntityDatum(full_jid, "presence", client.profile)
            except KeyError:
                log.debug(u"Can't get presence data for {}".format(full_jid))
            else:
                if presence_data.show != C.PRESENCE_UNAVAILABLE:
                    available.append(resource)
        return available

    def _getMainResource(self, jid_s, profile_key):
        client = self.host.getClient(profile_key)
        jid_ = jid.JID(jid_s)
        return self.getMainResource(client, jid_) or ""

    def getMainResource(self, client, entity_jid):
        """Return the main resource used by an entity

        @param entity_jid: bare entity jid
        @return (unicode): main resource or None
        """
        if entity_jid.resource:
            raise ValueError(
                "getMainResource must be used with a bare jid (got {})".format(entity_jid)
            )
        try:
            if self.host.plugins["XEP-0045"].isJoinedRoom(client, entity_jid):
                return None  # MUC rooms have no main resource
        except KeyError:  # plugin not found
            pass
        try:
            resources = self.getAllResources(client, entity_jid)
        except exceptions.UnknownEntityError:
            log.warning(u"Entity is not in cache, we can't find any resource")
            return None
        priority_resources = []
        for resource in resources:
            full_jid = copy.copy(entity_jid)
            full_jid.resource = resource
            try:
                presence_data = self.getEntityDatum(full_jid, "presence", client.profile)
            except KeyError:
                log.debug(u"No presence information for {}".format(full_jid))
                continue
            priority_resources.append((resource, presence_data.priority))
        try:
            return max(priority_resources, key=lambda res_tuple: res_tuple[1])[0]
        except ValueError:
            log.warning(u"No resource found at all for {}".format(entity_jid))
            return None

    ## Entities data ##

    def _getProfileCache(self, client):
        """Check profile validity and return its cache

        @param client: SatXMPPClient
        @return (dict): profile cache
        """
        return self._entities_cache[client.profile]

    def setSignalOnUpdate(self, key, signal=True):
        """Set a signal flag on the key

        When the key will be updated, a signal will be sent to frontends
        @param key: key to signal
        @param signal(boolean): if True, do the signal
        """
        if signal:
            self._key_signals.add(key)
        else:
            self._key_signals.discard(key)

    def getAllEntitiesIter(self, client, with_bare=False):
        """Return an iterator of full jids of all entities in cache

        @param with_bare: if True, include bare jids
        @return (list[unicode]): list of jids
        """
        profile_cache = self._getProfileCache(client)
        # we construct a list of all known full jids (bare jid of entities x resources)
        for bare_jid, entity_data in profile_cache.iteritems():
            for resource in entity_data.iterkeys():
                if resource is None:
                    continue
                full_jid = copy.copy(bare_jid)
                full_jid.resource = resource
                yield full_jid

    def updateEntityData(
        self, entity_jid, key, value, silent=False, profile_key=C.PROF_KEY_NONE
    ):
        """Set a misc data for an entity

        If key was registered with setSignalOnUpdate, a signal will be sent to frontends
        @param entity_jid: JID of the entity, C.ENTITY_ALL_RESOURCES for all resources of all entities,
                           C.ENTITY_ALL for all entities (all resources + bare jids)
        @param key: key to set (eg: "type")
        @param value: value for this key (eg: "chatroom")
        @param silent(bool): if True, doesn't send signal to frontend, even if there is a signal flag (see setSignalOnUpdate)
        @param profile_key: %(doc_profile_key)s
        """
        client = self.host.getClient(profile_key)
        profile_cache = self._getProfileCache(client)
        if entity_jid in (C.ENTITY_ALL_RESOURCES, C.ENTITY_ALL):
            entities = self.getAllEntitiesIter(client, entity_jid == C.ENTITY_ALL)
        else:
            entities = (entity_jid,)

        for jid_ in entities:
            entity_data = profile_cache.setdefault(jid_.userhostJID(), {}).setdefault(
                jid_.resource, {}
            )

            entity_data[key] = value
            if key in self._key_signals and not silent:
                if not isinstance(value, basestring):
                    log.error(
                        u"Setting a non string value ({}) for a key ({}) which has a signal flag".format(
                            value, key
                        )
                    )
                else:
                    self.host.bridge.entityDataUpdated(
                        jid_.full(), key, value, self.getProfileName(profile_key)
                    )

    def delEntityDatum(self, entity_jid, key, profile_key):
        """Delete a data for an entity

        @param entity_jid: JID of the entity, C.ENTITY_ALL_RESOURCES for all resources of all entities,
                           C.ENTITY_ALL for all entities (all resources + bare jids)
        @param key: key to delete (eg: "type")
        @param profile_key: %(doc_profile_key)s

        @raise exceptions.UnknownEntityError: if entity is not in cache
        @raise KeyError: key is not in cache
        """
        client = self.host.getClient(profile_key)
        profile_cache = self._getProfileCache(client)
        if entity_jid in (C.ENTITY_ALL_RESOURCES, C.ENTITY_ALL):
            entities = self.getAllEntitiesIter(client, entity_jid == C.ENTITY_ALL)
        else:
            entities = (entity_jid,)

        for jid_ in entities:
            try:
                entity_data = profile_cache[jid_.userhostJID()][jid_.resource]
            except KeyError:
                raise exceptions.UnknownEntityError(
                    u"Entity {} not in cache".format(jid_)
                )
            try:
                del entity_data[key]
            except KeyError as e:
                if entity_jid in (C.ENTITY_ALL_RESOURCES, C.ENTITY_ALL):
                    continue  # we ignore KeyError when deleting keys from several entities
                else:
                    raise e

    def _getEntitiesData(self, entities_jids, keys_list, profile_key):
        ret = self.getEntitiesData(
            [jid.JID(jid_) for jid_ in entities_jids], keys_list, profile_key
        )
        return {jid_.full(): data for jid_, data in ret.iteritems()}

    def getEntitiesData(self, entities_jids, keys_list=None, profile_key=C.PROF_KEY_NONE):
        """Get a list of cached values for several entities at once

        @param entities_jids: jids of the entities, or empty list for all entities in cache
        @param keys_list (iterable,None): list of keys to get, None for everything
        @param profile_key: %(doc_profile_key)s
        @return: dict withs values for each key in keys_list.
                 if there is no value of a given key, resulting dict will
                 have nothing with that key nether
                 if an entity doesn't exist in cache, it will not appear
                 in resulting dict

        @raise exceptions.UnknownEntityError: if entity is not in cache
        """

        def fillEntityData(entity_cache_data):
            entity_data = {}
            if keys_list is None:
                entity_data = entity_cache_data
            else:
                for key in keys_list:
                    try:
                        entity_data[key] = entity_cache_data[key]
                    except KeyError:
                        continue
            return entity_data

        client = self.host.getClient(profile_key)
        profile_cache = self._getProfileCache(client)
        ret_data = {}
        if entities_jids:
            for entity in entities_jids:
                try:
                    entity_cache_data = profile_cache[entity.userhostJID()][
                        entity.resource
                    ]
                except KeyError:
                    continue
                ret_data[entity.full()] = fillEntityData(entity_cache_data, keys_list)
        else:
            for bare_jid, data in profile_cache.iteritems():
                for resource, entity_cache_data in data.iteritems():
                    full_jid = copy.copy(bare_jid)
                    full_jid.resource = resource
                    ret_data[full_jid] = fillEntityData(entity_cache_data)

        return ret_data

    def getEntityData(self, entity_jid, keys_list=None, profile_key=C.PROF_KEY_NONE):
        """Get a list of cached values for entity

        @param entity_jid: JID of the entity
        @param keys_list (iterable,None): list of keys to get, None for everything
        @param profile_key: %(doc_profile_key)s
        @return: dict withs values for each key in keys_list.
                 if there is no value of a given key, resulting dict will
                 have nothing with that key nether

        @raise exceptions.UnknownEntityError: if entity is not in cache
        """
        client = self.host.getClient(profile_key)
        profile_cache = self._getProfileCache(client)
        try:
            entity_data = profile_cache[entity_jid.userhostJID()][entity_jid.resource]
        except KeyError:
            raise exceptions.UnknownEntityError(
                u"Entity {} not in cache (was requesting {})".format(
                    entity_jid, keys_list
                )
            )
        if keys_list is None:
            return entity_data

        return {key: entity_data[key] for key in keys_list if key in entity_data}

    def getEntityDatum(self, entity_jid, key, profile_key):
        """Get a datum from entity

        @param entity_jid: JID of the entity
        @param keys: key to get
        @param profile_key: %(doc_profile_key)s
        @return: requested value

        @raise exceptions.UnknownEntityError: if entity is not in cache
        @raise KeyError: if there is no value for this key and this entity
        """
        return self.getEntityData(entity_jid, (key,), profile_key)[key]

    def delEntityCache(
        self, entity_jid, delete_all_resources=True, profile_key=C.PROF_KEY_NONE
    ):
        """Remove all cached data for entity

        @param entity_jid: JID of the entity to delete
        @param delete_all_resources: if True also delete all known resources from cache (a bare jid must be given in this case)
        @param profile_key: %(doc_profile_key)s

        @raise exceptions.UnknownEntityError: if entity is not in cache
        """
        client = self.host.getClient(profile_key)
        profile_cache = self._getProfileCache(client)

        if delete_all_resources:
            if entity_jid.resource:
                raise ValueError(_("Need a bare jid to delete all resources"))
            try:
                del profile_cache[entity_jid]
            except KeyError:
                raise exceptions.UnknownEntityError(
                    u"Entity {} not in cache".format(entity_jid)
                )
        else:
            try:
                del profile_cache[entity_jid.userhostJID()][entity_jid.resource]
            except KeyError:
                raise exceptions.UnknownEntityError(
                    u"Entity {} not in cache".format(entity_jid)
                )

    ## Encryption ##

    def encryptValue(self, value, profile):
        """Encrypt a value for the given profile. The personal key must be loaded
        already in the profile session, that should be the case if the profile is
        already authenticated.

        @param value (str): the value to encrypt
        @param profile (str): %(doc_profile)s
        @return: the deferred encrypted value
        """
        try:
            personal_key = self.auth_sessions.profileGetUnique(profile)[
                C.MEMORY_CRYPTO_KEY
            ]
        except TypeError:
            raise exceptions.InternalError(
                _("Trying to encrypt a value for %s while the personal key is undefined!")
                % profile
            )
        return BlockCipher.encrypt(personal_key, value)

    def decryptValue(self, value, profile):
        """Decrypt a value for the given profile. The personal key must be loaded
        already in the profile session, that should be the case if the profile is
        already authenticated.

        @param value (str): the value to decrypt
        @param profile (str): %(doc_profile)s
        @return: the deferred decrypted value
        """
        try:
            personal_key = self.auth_sessions.profileGetUnique(profile)[
                C.MEMORY_CRYPTO_KEY
            ]
        except TypeError:
            raise exceptions.InternalError(
                _("Trying to decrypt a value for %s while the personal key is undefined!")
                % profile
            )
        return BlockCipher.decrypt(personal_key, value)

    def encryptPersonalData(self, data_key, data_value, crypto_key, profile):
        """Re-encrypt a personal data (saved to a PersistentDict).

        @param data_key: key for the individual PersistentDict instance
        @param data_value: the value to be encrypted
        @param crypto_key: the key to encrypt the value
        @param profile: %(profile_doc)s
        @return: a deferred None value
        """

        def gotIndMemory(data):
            d = BlockCipher.encrypt(crypto_key, data_value)

            def cb(cipher):
                data[data_key] = cipher
                return data.force(data_key)

            return d.addCallback(cb)

        def done(__):
            log.debug(
                _(u"Personal data (%(ns)s, %(key)s) has been successfuly encrypted")
                % {"ns": C.MEMORY_CRYPTO_NAMESPACE, "key": data_key}
            )

        d = PersistentDict(C.MEMORY_CRYPTO_NAMESPACE, profile).load()
        return d.addCallback(gotIndMemory).addCallback(done)

    ## Subscription requests ##

    def addWaitingSub(self, type_, entity_jid, profile_key):
        """Called when a subcription request is received"""
        profile = self.getProfileName(profile_key)
        assert profile
        if profile not in self.subscriptions:
            self.subscriptions[profile] = {}
        self.subscriptions[profile][entity_jid] = type_

    def delWaitingSub(self, entity_jid, profile_key):
        """Called when a subcription request is finished"""
        profile = self.getProfileName(profile_key)
        assert profile
        if profile in self.subscriptions and entity_jid in self.subscriptions[profile]:
            del self.subscriptions[profile][entity_jid]

    def getWaitingSub(self, profile_key):
        """Called to get a list of currently waiting subscription requests"""
        profile = self.getProfileName(profile_key)
        if not profile:
            log.error(_("Asking waiting subscriptions for a non-existant profile"))
            return {}
        if profile not in self.subscriptions:
            return {}

        return self.subscriptions[profile]

    ## Parameters ##

    def getStringParamA(self, name, category, attr="value", profile_key=C.PROF_KEY_NONE):
        return self.params.getStringParamA(name, category, attr, profile_key)

    def getParamA(self, name, category, attr="value", profile_key=C.PROF_KEY_NONE):
        return self.params.getParamA(name, category, attr, profile_key=profile_key)

    def asyncGetParamA(
        self,
        name,
        category,
        attr="value",
        security_limit=C.NO_SECURITY_LIMIT,
        profile_key=C.PROF_KEY_NONE,
    ):
        return self.params.asyncGetParamA(
            name, category, attr, security_limit, profile_key
        )

    def asyncGetParamsValuesFromCategory(
        self, category, security_limit=C.NO_SECURITY_LIMIT, profile_key=C.PROF_KEY_NONE
    ):
        return self.params.asyncGetParamsValuesFromCategory(
            category, security_limit, profile_key
        )

    def asyncGetStringParamA(
        self,
        name,
        category,
        attr="value",
        security_limit=C.NO_SECURITY_LIMIT,
        profile_key=C.PROF_KEY_NONE,
    ):
        return self.params.asyncGetStringParamA(
            name, category, attr, security_limit, profile_key
        )

    def getParamsUI(
        self, security_limit=C.NO_SECURITY_LIMIT, app="", profile_key=C.PROF_KEY_NONE
    ):
        return self.params.getParamsUI(security_limit, app, profile_key)

    def getParamsCategories(self):
        return self.params.getParamsCategories()

    def setParam(
        self,
        name,
        value,
        category,
        security_limit=C.NO_SECURITY_LIMIT,
        profile_key=C.PROF_KEY_NONE,
    ):
        return self.params.setParam(name, value, category, security_limit, profile_key)

    def updateParams(self, xml):
        return self.params.updateParams(xml)

    def paramsRegisterApp(self, xml, security_limit=C.NO_SECURITY_LIMIT, app=""):
        return self.params.paramsRegisterApp(xml, security_limit, app)

    def setDefault(self, name, category, callback, errback=None):
        return self.params.setDefault(name, category, callback, errback)

    ## Files ##

    def checkFilePermission(self, file_data, peer_jid, perms_to_check):
        """check that an entity has the right permission on a file

        @param file_data(dict): data of one file, as returned by getFiles
        @param peer_jid(jid.JID): entity trying to access the file
        @param perms_to_check(tuple[unicode]): permissions to check
            tuple of C.ACCESS_PERM_*
        @param check_parents(bool): if True, also check all parents until root node
        @raise exceptions.PermissionError: peer_jid doesn't have all permission
            in perms_to_check for file_data
        @raise exceptions.InternalError: perms_to_check is invalid
        """
        if peer_jid is None and perms_to_check is None:
            return
        peer_jid = peer_jid.userhostJID()
        if peer_jid == file_data["owner"]:
            # the owner has all rights
            return
        if not C.ACCESS_PERMS.issuperset(perms_to_check):
            raise exceptions.InternalError(_(u"invalid permission"))

        for perm in perms_to_check:
            # we check each perm and raise PermissionError as soon as one condition is not valid
            # we must never return here, we only return after the loop if nothing was blocking the access
            try:
                perm_data = file_data[u"access"][perm]
                perm_type = perm_data[u"type"]
            except KeyError:
                raise exceptions.PermissionError()
            if perm_type == C.ACCESS_TYPE_PUBLIC:
                continue
            elif perm_type == C.ACCESS_TYPE_WHITELIST:
                try:
                    jids = perm_data[u"jids"]
                except KeyError:
                    raise exceptions.PermissionError()
                if peer_jid.full() in jids:
                    continue
                else:
                    raise exceptions.PermissionError()
            else:
                raise exceptions.InternalError(
                    _(u"unknown access type: {type}").format(type=perm_type)
                )

    @defer.inlineCallbacks
    def checkPermissionToRoot(self, client, file_data, peer_jid, perms_to_check):
        """do checkFilePermission on file_data and all its parents until root"""
        current = file_data
        while True:
            self.checkFilePermission(current, peer_jid, perms_to_check)
            parent = current[u"parent"]
            if not parent:
                break
            files_data = yield self.getFile(
                self, client, peer_jid=None, file_id=parent, perms_to_check=None
            )
            try:
                current = files_data[0]
            except IndexError:
                raise exceptions.DataError(u"Missing parent")

    @defer.inlineCallbacks
    def _getParentDir(
        self, client, path, parent, namespace, owner, peer_jid, perms_to_check
    ):
        """Retrieve parent node from a path, or last existing directory

        each directory of the path will be retrieved, until the last existing one
        @return (tuple[unicode, list[unicode])): parent, remaining path elements:
            - parent is the id of the last retrieved directory (or u'' for root)
            - remaining path elements are the directories which have not been retrieved
              (i.e. which don't exist)
        """
        # if path is set, we have to retrieve parent directory of the file(s) from it
        if parent is not None:
            raise exceptions.ConflictError(
                _(u"You can't use path and parent at the same time")
            )
        path_elts = filter(None, path.split(u"/"))
        if {u"..", u"."}.intersection(path_elts):
            raise ValueError(_(u'".." or "." can\'t be used in path'))

        # we retrieve all directories from path until we get the parent container
        # non existing directories will be created
        parent = u""
        for idx, path_elt in enumerate(path_elts):
            directories = yield self.storage.getFiles(
                client,
                parent=parent,
                type_=C.FILE_TYPE_DIRECTORY,
                name=path_elt,
                namespace=namespace,
                owner=owner,
            )
            if not directories:
                defer.returnValue((parent, path_elts[idx:]))
                # from this point, directories don't exist anymore, we have to create them
            elif len(directories) > 1:
                raise exceptions.InternalError(
                    _(u"Several directories found, this should not happen")
                )
            else:
                directory = directories[0]
                self.checkFilePermission(directory, peer_jid, perms_to_check)
                parent = directory[u"id"]
        defer.returnValue((parent, []))

    @defer.inlineCallbacks
    def getFiles(
        self, client, peer_jid, file_id=None, version=None, parent=None, path=None,
        type_=None, file_hash=None, hash_algo=None, name=None, namespace=None,
        mime_type=None, owner=None, access=None, projection=None, unique=False,
        perms_to_check=(C.ACCESS_PERM_READ,)):
        """Retrieve files with with given filters

        @param peer_jid(jid.JID, None): jid trying to access the file
            needed to check permission.
            Use None to ignore permission (perms_to_check must be None too)
        @param file_id(unicode, None): id of the file
            None to ignore
        @param version(unicode, None): version of the file
            None to ignore
            empty string to look for current version
        @param parent(unicode, None): id of the directory containing the files
            None to ignore
            empty string to look for root files/directories
        @param path(unicode, None): path to the directory containing the files
        @param type_(unicode, None): type of file filter, can be one of C.FILE_TYPE_*
        @param file_hash(unicode, None): hash of the file to retrieve
        @param hash_algo(unicode, None): algorithm use for file_hash
        @param name(unicode, None): name of the file to retrieve
        @param namespace(unicode, None): namespace of the files to retrieve
        @param mime_type(unicode, None): filter on this mime type
        @param owner(jid.JID, None): if not None, only get files from this owner
        @param access(dict, None): get file with given access (see [setFile])
        @param projection(list[unicode], None): name of columns to retrieve
            None to retrieve all
        @param unique(bool): if True will remove duplicates
        @param perms_to_check(tuple[unicode],None): permission to check
            must be a tuple of C.ACCESS_PERM_* or None
            if None, permission will no be checked (peer_jid must be None too in this case)
        other params are the same as for [setFile]
        @return (list[dict]): files corresponding to filters
        @raise exceptions.NotFound: parent directory not found (when path is specified)
        @raise exceptions.PermissionError: peer_jid can't use perms_to_check for one of
                                           the file
            on the path
        """
        if peer_jid is None and perms_to_check or perms_to_check is None and peer_jid:
            raise exceptions.InternalError(
                u"if you want to disable permission check, both peer_jid and "
                u"perms_to_check must be None"
            )
        if owner is not None:
            owner = owner.userhostJID()
        if path is not None:
            # permission are checked by _getParentDir
            parent, remaining_path_elts = yield self._getParentDir(
                client, path, parent, namespace, owner, peer_jid, perms_to_check
            )
            if remaining_path_elts:
                # if we have remaining path elements,
                # the parent directory is not found
                raise failure.Failure(exceptions.NotFound())
        if parent and peer_jid:
            # if parent is given directly and permission check is requested,
            # we need to check all the parents
            parent_data = yield self.storage.getFiles(client, file_id=parent)
            try:
                parent_data = parent_data[0]
            except IndexError:
                raise exceptions.DataError(u"mising parent")
            yield self.checkPermissionToRoot(
                client, parent_data, peer_jid, perms_to_check
            )

        files = yield self.storage.getFiles(
            client,
            file_id=file_id,
            version=version,
            parent=parent,
            type_=type_,
            file_hash=file_hash,
            hash_algo=hash_algo,
            name=name,
            namespace=namespace,
            mime_type=mime_type,
            owner=owner,
            access=access,
            projection=projection,
            unique=unique,
        )

        if peer_jid:
            # if permission are checked, we must remove all file that user can't access
            to_remove = []
            for file_data in files:
                try:
                    self.checkFilePermission(file_data, peer_jid, perms_to_check)
                except exceptions.PermissionError:
                    to_remove.append(file_data)
            for file_data in to_remove:
                files.remove(file_data)
        defer.returnValue(files)

    @defer.inlineCallbacks
    def setFile(
            self, client, name, file_id=None, version=u"", parent=None, path=None,
            type_=C.FILE_TYPE_FILE, file_hash=None, hash_algo=None, size=None,
            namespace=None, mime_type=None, created=None, modified=None, owner=None,
            access=None, extra=None, peer_jid=None, perms_to_check=(C.ACCESS_PERM_WRITE,)
            ):
        """Set a file metadata

        @param name(unicode): basename of the file
        @param file_id(unicode): unique id of the file
        @param version(unicode): version of this file
            empty string for current version or when there is no versioning
        @param parent(unicode, None): id of the directory containing the files
        @param path(unicode, None): virtual path of the file in the namespace
            if set, parent must be None. All intermediate directories will be created
            if needed, using current access.
        @param file_hash(unicode): unique hash of the payload
        @param hash_algo(unicode): algorithm used for hashing the file (usually sha-256)
        @param size(int): size in bytes
        @param namespace(unicode, None): identifier (human readable is better) to group
                                         files
            For instance, namespace could be used to group files in a specific photo album
        @param mime_type(unicode): MIME type of the file, or None if not known/guessed
        @param created(int): UNIX time of creation
        @param modified(int,None): UNIX time of last modification, or None to use
                                   created date
        @param owner(jid.JID, None): jid of the owner of the file (mainly useful for
                                     component)
            will be used to check permission (only bare jid is used, don't use with MUC).
            Use None to ignore permission (perms_to_check must be None too)
        @param access(dict, None): serialisable dictionary with access rules.
            None (or empty dict) to use private access, i.e. allow only profile's jid to
            access the file
            key can be on on C.ACCESS_PERM_*,
            then a sub dictionary with a type key is used (one of C.ACCESS_TYPE_*).
            According to type, extra keys can be used:
                - C.ACCESS_TYPE_PUBLIC: the permission is granted for everybody
                - C.ACCESS_TYPE_WHITELIST: the permission is granted for jids (as unicode)
                  in the 'jids' key
            will be encoded to json in database
        @param extra(dict, None): serialisable dictionary of any extra data
            will be encoded to json in database
        @param perms_to_check(tuple[unicode],None): permission to check
            must be a tuple of C.ACCESS_PERM_* or None
            if None, permission will no be checked (peer_jid must be None too in this
            case)
        @param profile(unicode): profile owning the file
        """
        if "/" in name:
            raise ValueError('name must not contain a slash ("/")')
        if file_id is None:
            file_id = shortuuid.uuid()
        if (
            file_hash is not None
            and hash_algo is None
            or hash_algo is not None
            and file_hash is None
        ):
            raise ValueError("file_hash and hash_algo must be set at the same time")
        if mime_type is None:
            mime_type, file_encoding = mimetypes.guess_type(name)
        if created is None:
            created = time.time()
        if namespace is not None:
            namespace = namespace.strip() or None
        if type_ == C.FILE_TYPE_DIRECTORY:
            if any(version, file_hash, size, mime_type):
                raise ValueError(
                    u"version, file_hash, size and mime_type can't be set for a directory"
                )
        if owner is not None:
            owner = owner.userhostJID()

        if path is not None:
            # _getParentDir will check permissions if peer_jid is set, so we use owner
            parent, remaining_path_elts = yield self._getParentDir(
                client, path, parent, namespace, owner, owner, perms_to_check
            )
            # if remaining directories don't exist, we have to create them
            for new_dir in remaining_path_elts:
                new_dir_id = shortuuid.uuid()
                yield self.storage.setFile(
                    client,
                    name=new_dir,
                    file_id=new_dir_id,
                    version=u"",
                    parent=parent,
                    type_=C.FILE_TYPE_DIRECTORY,
                    namespace=namespace,
                    created=time.time(),
                    owner=owner,
                    access=access,
                    extra={},
                )
                parent = new_dir_id
        elif parent is None:
            parent = u""

        yield self.storage.setFile(
            client,
            file_id=file_id,
            version=version,
            parent=parent,
            type_=type_,
            file_hash=file_hash,
            hash_algo=hash_algo,
            name=name,
            size=size,
            namespace=namespace,
            mime_type=mime_type,
            created=created,
            modified=modified,
            owner=owner,
            access=access,
            extra=extra,
        )

    def fileUpdate(self, file_id, column, update_cb):
        """Update a file column taking care of race condition

        access is NOT checked in this method, it must be checked beforehand
        @param file_id(unicode): id of the file to update
        @param column(unicode): one of "access" or "extra"
        @param update_cb(callable): method to update the value of the colum
            the method will take older value as argument, and must update it in place
            Note that the callable must be thread-safe
        """
        return self.storage.fileUpdate(file_id, column, update_cb)

    @defer.inlineCallbacks
    def _deleteFile(self, client, peer_jid, recursive, files_path, file_data):
        """Internal method to delete files/directories recursively

        @param peer_jid(jid.JID): entity requesting the deletion (must be owner of files
            to delete)
        @param recursive(boolean): True if recursive deletion is needed
        @param files_path(unicode): path of the directory containing the actual files
        @param file_data(dict): data of the file to delete
        """
        if file_data[u'owner'] != peer_jid:
            raise exceptions.PermissionError(
                u"file {file_name} can't be deleted, {peer_jid} is not the owner"
                .format(file_name=file_data[u'name'], peer_jid=peer_jid.full()))
        if file_data[u'type'] == C.FILE_TYPE_DIRECTORY:
            sub_files = yield self.getFiles(client, peer_jid, parent=file_data[u'id'])
            if sub_files and not recursive:
                raise exceptions.DataError(_(u"Can't delete directory, it is not empty"))
            # we first delete the sub-files
            for sub_file_data in sub_files:
                yield self._deleteFile(client, peer_jid, recursive, sub_file_data)
            # then the directory itself
            yield self.storage.fileDelete(file_data[u'id'])
        elif file_data[u'type'] == C.FILE_TYPE_FILE:
            log.info(_(u"deleting file {name} with hash {file_hash}").format(
                name=file_data[u'name'], file_hash=file_data[u'file_hash']))
            yield self.storage.fileDelete(file_data[u'id'])
            references = yield self.getFiles(
                client, peer_jid, file_hash=file_data[u'file_hash'])
            if references:
                log.debug(u"there are still references to the file, we keep it")
            else:
                file_path = os.path.join(files_path, file_data[u'file_hash'])
                log.info(_(u"no reference left to {file_path}, deleting").format(
                    file_path=file_path))
                os.unlink(file_path)
        else:
            raise exceptions.InternalError(u'Unexpected file type: {file_type}'
                .format(file_type=file_data[u'type']))

    @defer.inlineCallbacks
    def fileDelete(self, client, peer_jid, file_id, recursive=False):
        """Delete a single file or a directory and all its sub-files

        @param file_id(unicode): id of the file to delete
        @param peer_jid(jid.JID): entity requesting the deletion,
            must be owner of all files to delete
        @param recursive(boolean): must be True to delete a directory and all sub-files
        """
        # FIXME: we only allow owner of file to delete files for now, but WRITE access
        #        should be checked too
        files_data = yield self.getFiles(client, peer_jid, file_id)
        if not files_data:
            raise exceptions.NotFound(u"Can't find the file with id {file_id}".format(
                file_id=file_id))
        file_data = files_data[0]
        if file_data[u"type"] != C.FILE_TYPE_DIRECTORY and recursive:
            raise ValueError(u"recursive can only be set for directories")
        files_path = self.host.getLocalPath(None, C.FILES_DIR, profile=False)
        yield self._deleteFile(client, peer_jid, recursive, files_path, file_data)

    ## Misc ##

    def isEntityAvailable(self, client, entity_jid):
        """Tell from the presence information if the given entity is available.

        @param entity_jid (JID): the entity to check (if bare jid is used, all resources are tested)
        @return (bool): True if entity is available
        """
        if not entity_jid.resource:
            return bool(
                self.getAvailableResources(client, entity_jid)
            )  # is any resource is available, entity is available
        try:
            presence_data = self.getEntityDatum(entity_jid, "presence", client.profile)
        except KeyError:
            log.debug(u"No presence information for {}".format(entity_jid))
            return False
        return presence_data.show != C.PRESENCE_UNAVAILABLE
