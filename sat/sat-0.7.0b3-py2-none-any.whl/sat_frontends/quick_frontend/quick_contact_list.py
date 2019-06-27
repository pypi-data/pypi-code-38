#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
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

"""Contact List handling multi profiles at once,
    should replace quick_contact_list module in the future"""

from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from sat_frontends.quick_frontend.quick_widgets import QuickWidget
from sat_frontends.quick_frontend.constants import Const as C
from sat_frontends.tools import jid
from collections import OrderedDict


try:
    # FIXME: to be removed when an acceptable solution is here
    unicode("")  # XXX: unicode doesn't exist in pyjamas
except (TypeError, AttributeError):  # Error raised is not the same depending on
    # pyjsbuild options
    # XXX: pyjamas' max doesn't support key argument, so we implement it ourself
    pyjamas_max = max

    def max(iterable, key):
        iter_cpy = list(iterable)
        iter_cpy.sort(key=key)
        return pyjamas_max(iter_cpy)

    # next doesn't exist in pyjamas
    def next(iterable, *args):
        try:
            return iterable.next()
        except StopIteration as e:
            if args:
                return args[0]
            raise e


handler = None


class ProfileContactList(object):
    """Contact list data for a single profile"""

    def __init__(self, profile):
        self.host = handler.host
        self.profile = profile
        # contain all jids in roster or not,
        # bare jids as keys, resources are used in data
        # XXX: we don't mutualise cache, as values may differ
        # for different profiles (e.g. directed presence)
        self._cache = {}

        # special entities (groupchat, gateways, etc)
        # may be bare or full jid
        self._specials = set()

        # group data contain jids in groups and misc frontend data
        # None key is used for jids with no group
        self._groups = {}  # groups to group data map

        # contacts in roster (bare jids)
        self._roster = set()

        # selected entities, full jid
        self._selected = set()

        # options
        self.show_disconnected = False
        self.show_empty_groups = True
        self.show_resources = False
        self.show_status = False
        # do we show entities with notifications?
        # if True, entities will be show even if they normally would not
        # (e.g. not in contact list) if they have notifications attached
        self.show_entities_with_notifs = True

        self.host.bridge.asyncGetParamA(
            C.SHOW_EMPTY_GROUPS,
            "General",
            profile_key=profile,
            callback=self._showEmptyGroups,
        )

        self.host.bridge.asyncGetParamA(
            C.SHOW_OFFLINE_CONTACTS,
            "General",
            profile_key=profile,
            callback=self._showOfflineContacts,
        )

        # FIXME: workaround for a pyjamas issue: calling hash on a class method always
        #        return a different value if that method is defined directly within the
        #        class (with the "def" keyword)
        self.presenceListener = self.onPresenceUpdate
        self.host.addListener("presence", self.presenceListener, [self.profile])
        self.nickListener = self.onNickUpdate
        self.host.addListener("nick", self.nickListener, [self.profile])
        self.notifListener = self.onNotification
        self.host.addListener("notification", self.notifListener, [self.profile])
        # notifListener only update the entity, so we can re-use it
        self.host.addListener("notificationsClear", self.notifListener, [self.profile])

    @property
    def whoami(self):
        return self.host.profiles[self.profile].whoami

    def _showEmptyGroups(self, show_str):
        # Called only by __init__
        # self.update is not wanted here, as it is done by
        # handler when all profiles are ready
        self.showEmptyGroups(C.bool(show_str))

    def _showOfflineContacts(self, show_str):
        # same comments as for _showEmptyGroups
        self.showOfflineContacts(C.bool(show_str))

    def __contains__(self, entity):
        """Check if entity is in contact list

        An entity can be in contact list even if not in roster
        @param entity (jid.JID): jid of the entity (resource is not ignored,
            use bare jid if needed)
        """
        if entity.resource:
            try:
                return entity.resource in self.getCache(entity.bare, C.CONTACT_RESOURCES)
            except exceptions.NotFound:
                return False
        return entity in self._cache

    @property
    def roster(self):
        """Return all the bare JIDs of the roster entities.

        @return (set[jid.JID])
        """
        return self._roster

    @property
    def roster_connected(self):
        """Return all the bare JIDs of the roster entities that are connected.

        @return (set[jid.JID])
        """
        return set(
            [
                entity
                for entity in self._roster
                if self.getCache(entity, C.PRESENCE_SHOW) is not None
            ]
        )

    @property
    def roster_entities_by_group(self):
        """Return a dictionary binding the roster groups to their entities bare JIDs.

        This also includes the empty group (None key).
        @return (dict[unicode,set(jid.JID)])
        """
        return {group: self._groups[group]["jids"] for group in self._groups}

    @property
    def roster_groups_by_entities(self):
        """Return a dictionary binding the entities bare JIDs to their roster groups

        @return (dict[jid.JID, set(unicode)])
        """
        result = {}
        for group, data in self._groups.iteritems():
            for entity in data["jids"]:
                result.setdefault(entity, set()).add(group)
        return result

    @property
    def selected(self):
        """Return contacts currently selected

        @return (set): set of selected entities
        """
        return self._selected

    @property
    def all_iter(self):
        """return all know entities in cache as an iterator of tuples

        entities are not sorted
        """
        return self._cache.iteritems()

    @property
    def items(self):
        """Return item representation for all visible entities in cache

        entities are not sorted
        key: bare jid, value: data
        """
        return {
            jid_: cache
            for jid_, cache in self._cache.iteritems()
            if self.entityVisible(jid_)
        }

    def getItem(self, entity):
        """Return item representation of requested entity

        @param entity(jid.JID): bare jid of entity
        @raise (KeyError): entity is unknown
        """
        return self._cache[entity]

    def _gotContacts(self, contacts):
        """Add contacts and notice parent that contacts are filled

        Called during initial contact list filling
        @param contacts(tuple): all contacts
        """
        for contact in contacts:
            self.host.newContactHandler(*contact, profile=self.profile)
        handler._contactsFilled(self.profile)

    def _fill(self):
        """Get all contacts from backend

        Contacts will be cleared before refilling them
        """
        self.clearContacts(keep_cache=True)
        self.host.bridge.getContacts(self.profile, callback=self._gotContacts)

    def fill(self):
        handler.fill(self.profile)

    def getCache(self, entity, name=None, bare_default=True, create_if_not_found=False):
        """Return a cache value for a contact

        @param entity(jid.JID): entity of the contact from who we want data
            (resource is used if given)
            if a resource specific information is requested:
                - if no resource is given (bare jid), the main resource is used,
                    according to priority
                - if resource is given, it is used
        @param name(unicode): name the data to get, or None to get everything
        @param bare_default(bool, None): if True and entity is a full jid,
            the value of bare jid will be returned if not value is found for
            the requested resource.
            If False, None is returned if no value is found for the requested resource.
            If None, bare_default will be set to False if entity is in a room, True else
        @param create_if_not_found(bool): if True, create contact if it's not found
            in cache
        @return: full cache if no name is given, or value of "name", or None
        @raise NotFound: entity not found in cache
        """
        # FIXME: resource handling need to be reworked
        # FIXME: bare_default work for requesting full jid to get bare jid,
        #        but not the other way
        #        e.g.: if we have set an avatar for user@server.tld/resource
        #        and we request user@server.tld
        #        we won't get the avatar set in the resource
        try:
            cache = self._cache[entity.bare]
        except KeyError:
            if create_if_not_found:
                self.setContact(entity)
                cache = self._cache[entity.bare]
            else:
                raise exceptions.NotFound

        if name is None:
            # full cache is requested
            return cache

        if name in ("status", C.PRESENCE_STATUSES, C.PRESENCE_PRIORITY, C.PRESENCE_SHOW):
            # these data are related to the resource
            if not entity.resource:
                main_resource = cache[C.CONTACT_MAIN_RESOURCE]
                if main_resource is None:
                    # we ignore presence info if we don't have any resource in cache
                    # FIXME: to be checked
                    return
                cache = cache[C.CONTACT_RESOURCES].setdefault(main_resource, {})
            else:
                cache = cache[C.CONTACT_RESOURCES].setdefault(entity.resource, {})

            if name == "status":  # XXX: we get the first status for 'status' key
                # TODO: manage main language for statuses
                return cache[C.PRESENCE_STATUSES].get(C.PRESENCE_STATUSES_DEFAULT, "")

        elif entity.resource:
            try:
                return cache[C.CONTACT_RESOURCES][entity.resource][name]
            except KeyError:
                if bare_default is None:
                    bare_default = not self.isRoom(entity.bare)
                if not bare_default:
                    return None

        try:
            return cache[name]
        except KeyError:
            return None

    def setCache(self, entity, name, value):
        """Set or update value for one data in cache

        @param entity(JID): entity to update
        @param name(unicode): value to set or update
        """
        self.setContact(entity, attributes={name: value})

    def getFullJid(self, entity):
        """Get full jid from a bare jid

        @param entity(jid.JID): must be a bare jid
        @return (jid.JID): bare jid + main resource
        @raise ValueError: the entity is not bare
        """
        if entity.resource:
            raise ValueError(u"getFullJid must be used with a bare jid")
        main_resource = self.getCache(entity, C.CONTACT_MAIN_RESOURCE)
        return jid.JID(u"{}/{}".format(entity, main_resource))

    def setGroupData(self, group, name, value):
        """Register a data for a group

        @param group: a valid (existing) group name
        @param name: name of the data (can't be "jids")
        @param value: value to set
        """
        assert name != "jids"
        self._groups[group][name] = value

    def getGroupData(self, group, name=None):
        """Return value associated to group data

        @param group: a valid (existing) group name
        @param name: name of the data or None to get the whole dict
        @return: registered value
        """
        if name is None:
            return self._groups[group]
        return self._groups[group][name]

    def isRoom(self, entity):
        """Helper method to know if entity is a MUC room

        @param entity(jid.JID): jid of the entity
            hint: use bare jid here, as room can't be full jid with MUC
        @return (bool): True if entity is a room
        """
        assert entity.resource is None  # FIXME: this may change when MIX will be handled
        return self.isSpecial(entity, C.CONTACT_SPECIAL_GROUP)

    def isSpecial(self, entity, special_type):
        """Tell if an entity is of a specialy _type

        @param entity(jid.JID): jid of the special entity
            if the jid is full, will be added to special extras
        @param special_type: one of special type (e.g. C.CONTACT_SPECIAL_GROUP)
        @return (bool): True if entity is from this special type
        """
        return self.getCache(entity, C.CONTACT_SPECIAL) == special_type

    def setSpecial(self, entity, special_type):
        """Set special flag on an entity

        @param entity(jid.JID): jid of the special entity
            if the jid is full, will be added to special extras
        @param special_type: one of special type (e.g. C.CONTACT_SPECIAL_GROUP)
            or None to remove special flag
        """
        assert special_type in C.CONTACT_SPECIAL_ALLOWED + (None,)
        self.setCache(entity, C.CONTACT_SPECIAL, special_type)

    def getSpecials(self, special_type=None, bare=False):
        """Return all the bare JIDs of the special roster entities of with given type.

        @param special_type(unicode, None): if not None, filter by special type
            (e.g. C.CONTACT_SPECIAL_GROUP)
        @param bare(bool): return only bare jids if True
        @return (iter[jid.JID]): found special entities
        """
        for entity in self._specials:
            if bare and entity.resource:
                continue
            if (
                special_type is not None
                and self.getCache(entity, C.CONTACT_SPECIAL) != special_type
            ):
                continue
            yield entity

    def disconnect(self):
        # for now we just clear contacts on disconnect
        self.clearContacts()

    def clearContacts(self, keep_cache=False):
        """Clear all the contact list

        @param keep_cache: if True, don't reset the cache
        """
        self.select(None)
        if not keep_cache:
            self._cache.clear()
        self._groups.clear()
        self._specials.clear()
        self._roster.clear()
        self.update()

    def setContact(self, entity, groups=None, attributes=None, in_roster=False):
        """Add a contact to the list if it doesn't exist, else update it.

        This method can be called with groups=None for the purpose of updating
        the contact's attributes (e.g. nickname). In that case, the groups
        attribute must not be set to the default group but ignored. If not,
        you may move your contact from its actual group(s) to the default one.

        None value for 'groups' has a different meaning than [None]
        which is for the default group.

        @param entity (jid.JID): entity to add or replace
            if entity is a full jid, attributes will be cached in for the full jid only
        @param groups (list): list of groups or None to ignore the groups membership.
        @param attributes (dict): attibutes of the added jid or to update
            if attribute value is None, it will be removed
        @param in_roster (bool): True if contact is from roster
        """
        if attributes is None:
            attributes = {}

        entity_bare = entity.bare
        # we check if the entity is visible before changing anything
        # this way we know if we need to do an UPDATE_ADD, UPDATE_MODIFY
        # or an UPDATE_DELETE
        was_visible = self.entityVisible(entity_bare)

        if in_roster:
            self._roster.add(entity_bare)

        cache = self._cache.setdefault(
            entity_bare,
            {
                C.CONTACT_RESOURCES: {},
                C.CONTACT_MAIN_RESOURCE: None,
                C.CONTACT_SELECTED: set(),
            },
        )

        # we don't want forbidden data in attributes
        assert not C.CONTACT_DATA_FORBIDDEN.intersection(attributes)

        # we set groups and fill self._groups accordingly
        if groups is not None:
            if not groups:
                groups = [None]  # [None] is the default group
            if C.CONTACT_GROUPS in cache:
                # XXX: don't use set(cache[C.CONTACT_GROUPS]).difference(groups) because
                #      it won't work in Pyjamas if None is in cache[C.CONTACT_GROUPS]
                for group in [
                    group for group in cache[C.CONTACT_GROUPS] if group not in groups
                ]:
                    self._groups[group]["jids"].remove(entity_bare)
            cache[C.CONTACT_GROUPS] = groups
            for group in groups:
                self._groups.setdefault(group, {}).setdefault("jids", set()).add(
                    entity_bare
                )

        # special entities management
        if C.CONTACT_SPECIAL in attributes:
            if attributes[C.CONTACT_SPECIAL] is None:
                del attributes[C.CONTACT_SPECIAL]
                self._specials.remove(entity)
            else:
                self._specials.add(entity)
                cache[C.CONTACT_MAIN_RESOURCE] = None

        # now the attributes we keep in cache
        # XXX: if entity is a full jid, we store the value for the resource only
        cache_attr = (
            cache[C.CONTACT_RESOURCES].setdefault(entity.resource, {})
            if entity.resource
            else cache
        )
        for attribute, value in attributes.iteritems():
            if value is None:
                # XXX: pyjamas hack: we need to use pop instead of del
                try:
                    cache_attr[attribute].pop(value)
                except KeyError:
                    pass
            else:
                if attribute == "nick" and self.isSpecial(
                    entity, C.CONTACT_SPECIAL_GROUP
                ):
                    # we don't want to keep nick for MUC rooms
                    # FIXME: this is here as plugin XEP-0054 can link resource's nick
                    #        with bare jid which in the case of MUC
                    #        set the nick for the whole MUC
                    #        resulting in bad name displayed in some frontends
                    continue
                cache_attr[attribute] = value

        # we can update the display if needed
        if self.entityVisible(entity_bare):
            # if the contact was not visible, we need to add a widget
            # else we just update id
            update_type = C.UPDATE_MODIFY if was_visible else C.UPDATE_ADD
            self.update([entity], update_type, self.profile)
        elif was_visible:
            # the entity was visible and is not anymore, we remove it
            self.update([entity], C.UPDATE_DELETE, self.profile)

    def entityVisible(self, entity, check_resource=False):
        """Tell if the contact should be showed or hidden.

        @param entity (jid.JID): jid of the contact
        @param check_resource (bool): True if resource must be significant
        @return (bool): True if that contact should be showed in the list
        """
        try:
            show = self.getCache(entity, C.PRESENCE_SHOW)
        except exceptions.NotFound:
            return False

        if check_resource:
            selected = self._selected
        else:
            selected = {selected.bare for selected in self._selected}
        return (
            (show is not None and show != C.PRESENCE_UNAVAILABLE)
            or self.show_disconnected
            or entity in selected
            or (
                self.show_entities_with_notifs
                and next(self.host.getNotifs(entity.bare, profile=self.profile), None)
            )
            or entity.resource is None and self.isRoom(entity.bare)
        )

    def anyEntityVisible(self, entities, check_resources=False):
        """Tell if in a list of entities, at least one should be shown

        @param entities (list[jid.JID]): list of jids
        @param check_resources (bool): True if resources must be significant
        @return (bool): True if a least one entity need to be shown
        """
        # FIXME: looks inefficient, really needed?
        for entity in entities:
            if self.entityVisible(entity, check_resources):
                return True
        return False

    def isEntityInGroup(self, entity, group):
        """Tell if an entity is in a roster group

        @param entity(jid.JID): jid of the entity
        @param group(unicode): group to check
        @return (bool): True if the entity is in the group
        """
        return entity in self.getGroupData(group, "jids")

    def removeContact(self, entity):
        """remove a contact from the list

        @param entity(jid.JID): jid of the entity to remove (bare jid is used)
        """
        entity_bare = entity.bare
        was_visible = self.entityVisible(entity_bare)
        try:
            groups = self._cache[entity_bare].get(C.CONTACT_GROUPS, set())
        except KeyError:
            log.error(_(u"Trying to delete an unknow entity [{}]").format(entity))
        try:
            self._roster.remove(entity_bare)
        except KeyError:
            pass
        del self._cache[entity_bare]
        for group in groups:
            self._groups[group]["jids"].remove(entity_bare)
            if not self._groups[group]["jids"]:
                # FIXME: we use pop because of pyjamas:
                #        http://wiki.goffi.org/wiki/Issues_with_Pyjamas/en
                self._groups.pop(group)
        for iterable in (self._selected, self._specials):
            to_remove = set()
            for set_entity in iterable:
                if set_entity.bare == entity.bare:
                    to_remove.add(set_entity)
            iterable.difference_update(to_remove)
        if was_visible:
            self.update([entity], C.UPDATE_DELETE, self.profile)

    def onPresenceUpdate(self, entity, show, priority, statuses, profile):
        """Update entity's presence status

        @param entity(jid.JID): entity updated
        @param show: availability
        @parap priority: resource's priority
        @param statuses: dict of statuses
        @param profile: %(doc_profile)s
        """
        # FIXME: cache modification should be done with setContact
        #        the resources/presence handling logic should be moved there
        was_visible = self.entityVisible(entity.bare)
        cache = self.getCache(entity, create_if_not_found=True)
        if show == C.PRESENCE_UNAVAILABLE:
            if not entity.resource:
                cache[C.CONTACT_RESOURCES].clear()
                cache[C.CONTACT_MAIN_RESOURCE] = None
            else:
                try:
                    del cache[C.CONTACT_RESOURCES][entity.resource]
                except KeyError:
                    log.error(
                        u"Presence unavailable received "
                        u"for an unknown resource [{}]".format(entity)
                    )
                if not cache[C.CONTACT_RESOURCES]:
                    cache[C.CONTACT_MAIN_RESOURCE] = None
        else:
            if not entity.resource:
                log.warning(
                    _(
                        u"received presence from entity "
                        u"without resource: {}".format(entity)
                    )
                )
            resources_data = cache[C.CONTACT_RESOURCES]
            resource_data = resources_data.setdefault(entity.resource, {})
            resource_data[C.PRESENCE_SHOW] = show
            resource_data[C.PRESENCE_PRIORITY] = int(priority)
            resource_data[C.PRESENCE_STATUSES] = statuses

            if entity.bare not in self._specials:
                # we may have resources with no priority
                # (when a cached value is added for a not connected resource)
                priority_resource = max(
                    resources_data,
                    key=lambda res: resources_data[res].get(
                        C.PRESENCE_PRIORITY, -2 ** 32
                    ),
                )
                cache[C.CONTACT_MAIN_RESOURCE] = priority_resource
        if self.entityVisible(entity.bare):
            update_type = C.UPDATE_MODIFY if was_visible else C.UPDATE_ADD
            self.update([entity], update_type, self.profile)
        elif was_visible:
            self.update([entity], C.UPDATE_DELETE, self.profile)

    def onNickUpdate(self, entity, new_nick, profile):
        """Update entity's nick

        @param entity(jid.JID): entity updated
        @param new_nick(unicode): new nick of the entity
        @param profile: %(doc_profile)s
        """
        assert profile == self.profile
        self.setCache(entity, "nick", new_nick)

    def onNotification(self, entity, notif, profile):
        """Update entity with notification

        @param entity(jid.JID): entity updated
        @param notif(dict): notification data
        @param profile: %(doc_profile)s
        """
        assert profile == self.profile
        if entity is not None and self.entityVisible(entity):
            self.update([entity], C.UPDATE_MODIFY, profile)

    def unselect(self, entity):
        """Unselect an entity

         @param entity(jid.JID): entity to unselect
        """
        try:
            cache = self._cache[entity.bare]
        except:
            log.error(u"Try to unselect an entity not in cache")
        else:
            try:
                cache[C.CONTACT_SELECTED].remove(entity.resource)
            except KeyError:
                log.error(u"Try to unselect a not selected entity")
            else:
                self._selected.remove(entity)
                self.update([entity], C.UPDATE_SELECTION)

    def select(self, entity):
        """Select an entity

        @param entity(jid.JID, None): entity to select (resource is significant)
            None to unselect all entities
        """
        if entity is None:
            self._selected.clear()
            for cache in self._cache.itervalues():
                cache[C.CONTACT_SELECTED].clear()
            self.update(type_=C.UPDATE_SELECTION, profile=self.profile)
        else:
            log.debug(u"select %s" % entity)
            try:
                cache = self._cache[entity.bare]
            except:
                log.error(u"Try to select an entity not in cache")
            else:
                cache[C.CONTACT_SELECTED].add(entity.resource)
                self._selected.add(entity)
                self.update([entity], C.UPDATE_SELECTION, profile=self.profile)

    def showOfflineContacts(self, show):
        """Tell if offline contacts should be shown

        @param show(bool): True if offline contacts should be shown
        """
        assert isinstance(show, bool)
        if self.show_disconnected == show:
            return
        self.show_disconnected = show
        self.update(type_=C.UPDATE_STRUCTURE, profile=self.profile)

    def showEmptyGroups(self, show):
        assert isinstance(show, bool)
        if self.show_empty_groups == show:
            return
        self.show_empty_groups = show
        self.update(type_=C.UPDATE_STRUCTURE, profile=self.profile)

    def showResources(self, show):
        assert isinstance(show, bool)
        if self.show_resources == show:
            return
        self.show_resources = show
        self.update(type_=C.UPDATE_STRUCTURE, profile=self.profile)

    def plug(self):
        handler.addProfile(self.profile)

    def unplug(self):
        handler.removeProfile(self.profile)

    def update(self, entities=None, type_=None, profile=None):
        handler.update(entities, type_, profile)


class QuickContactListHandler(object):
    def __init__(self, host):
        super(QuickContactListHandler, self).__init__()
        self.host = host
        global handler
        if handler is not None:
            raise exceptions.InternalError(
                u"QuickContactListHandler must be instanciated only once"
            )
        handler = self
        self._clist = {}  # key: profile, value: ProfileContactList
        self._widgets = set()
        self._update_locked = False  # se to True to ignore updates

    def __getitem__(self, profile):
        """Return ProfileContactList instance for the requested profile"""
        return self._clist[profile]

    def __contains__(self, entity):
        """Check if entity is in contact list

        @param entity (jid.JID): jid of the entity (resource is not ignored,
            use bare jid if needed)
        """
        for contact_list in self._clist.itervalues():
            if entity in contact_list:
                return True
        return False

    @property
    def roster(self):
        """Return all the bare JIDs of the roster entities.

        @return (set[jid.JID])
        """
        entities = set()
        for contact_list in self._clist.itervalues():
            entities.update(contact_list.roster)
        return entities

    @property
    def roster_connected(self):
        """Return all the bare JIDs of the roster entities that are connected.

        @return (set[jid.JID])
        """
        entities = set()
        for contact_list in self._clist.itervalues():
            entities.update(contact_list.roster_connected)
        return entities

    @property
    def roster_entities_by_group(self):
        """Return a dictionary binding the roster groups to their entities bare
        JIDs. This also includes the empty group (None key).

        @return (dict[unicode,set(jid.JID)])
        """
        groups = {}
        for contact_list in self._clist.itervalues():
            groups.update(contact_list.roster_entities_by_group)
        return groups

    @property
    def roster_groups_by_entities(self):
        """Return a dictionary binding the entities bare JIDs to their roster
        groups.

        @return (dict[jid.JID, set(unicode)])
        """
        entities = {}
        for contact_list in self._clist.itervalues():
            entities.update(contact_list.roster_groups_by_entities)
        return entities

    @property
    def selected(self):
        """Return contacts currently selected

        @return (set): set of selected entities
        """
        entities = set()
        for contact_list in self._clist.itervalues():
            entities.update(contact_list.selected)
        return entities

    @property
    def all_iter(self):
        """Return item representation for all entities in cache

        items are unordered
        """
        for profile, contact_list in self._clist.iteritems():
            for bare_jid, cache in contact_list.all_iter:
                data = cache.copy()
                data[C.CONTACT_PROFILE] = profile
                yield bare_jid, data

    @property
    def items(self):
        """Return item representation for visible entities in cache

        items are unordered
        key: bare jid, value: data
        """
        items = {}
        for profile, contact_list in self._clist.iteritems():
            for bare_jid, cache in contact_list.items.iteritems():
                data = cache.copy()
                items[bare_jid] = data
                data[C.CONTACT_PROFILE] = profile
        return items

    @property
    def items_sorted(self):
        """Return item representation for visible entities in cache

        items are ordered using self.items_sort
        key: bare jid, value: data
        """
        return self.items_sort(self.items)

    def items_sort(self, items):
        """sort items

       @param items(dict): items to sort (will be emptied !)
       @return (OrderedDict): sorted items
       """
        ordered_items = OrderedDict()
        bare_jids = sorted(items.keys())
        for jid_ in bare_jids:
            ordered_items[jid_] = items.pop(jid_)
        return ordered_items

    def register(self, widget):
        """Register a QuickContactList widget

        This method should only be used in QuickContactList
        """
        self._widgets.add(widget)

    def unregister(self, widget):
        """Unregister a QuickContactList widget

        This method should only be used in QuickContactList
        """
        self._widgets.remove(widget)

    def addProfiles(self, profiles):
        """Add a contact list for plugged profiles

        @param profile(iterable[unicode]): plugged profiles
        """
        for profile in profiles:
            if profile not in self._clist:
                self._clist[profile] = ProfileContactList(profile)
        return [self._clist[profile] for profile in profiles]

    def addProfile(self, profile):
        return self.addProfiles([profile])[0]

    def removeProfiles(self, profiles):
        """Remove given unplugged profiles from contact list

        @param profile(iterable[unicode]): unplugged profiles
        """
        for profile in profiles:
            del self._clist[profile]

    def removeProfile(self, profile):
        self.removeProfiles([profile])

    def getSpecialExtras(self, special_type=None):
        """Return special extras with given type

        If special_type is None, return all special extras.

        @param special_type(unicode, None): one of special type
            (e.g. C.CONTACT_SPECIAL_GROUP)
            None to return all special extras.
        @return (set[jid.JID])
        """
        entities = set()
        for contact_list in self._clist.itervalues():
            entities.update(contact_list.getSpecialExtras(special_type))
        return entities

    def _contactsFilled(self, profile):
        self._to_fill.remove(profile)
        if not self._to_fill:
            del self._to_fill
            # we need a full update when all contacts are filled
            self.update()

    def fill(self, profile=None):
        """Get all contacts from backend, and fill the widget

        Contacts will be cleared before refilling them
        @param profile(unicode, None): profile to fill
            None to fill all profiles
        """
        try:
            to_fill = self._to_fill
        except AttributeError:
            to_fill = self._to_fill = set()

        # we check if profiles have already been filled
        # to void filling them several times
        filled = to_fill.copy()

        if profile is not None:
            assert profile in self._clist
            to_fill.add(profile)
        else:
            to_fill.update(self._clist.keys())

        remaining = to_fill.difference(filled)
        if remaining != to_fill:
            log.debug(
                u"Not re-filling already filled contact list(s) for {}".format(
                    u", ".join(to_fill.intersection(filled))
                )
            )
        for profile in remaining:
            self._clist[profile]._fill()

    def clearContacts(self, keep_cache=False):
        """Clear all the contact list

        @param keep_cache: if True, don't reset the cache
        """
        for contact_list in self._clist.itervalues():
            contact_list.clearContacts(keep_cache)
        # we need a full update
        self.update()

    def select(self, entity):
        for contact_list in self._clist.itervalues():
            contact_list.select(entity)

    def unselect(self, entity):
        for contact_list in self._clist.itervalues():
            contact_list.select(entity)

    def lockUpdate(self, locked=True, do_update=True):
        """Forbid contact list updates

        Used mainly while profiles are plugged, as many updates can occurs, causing
        an impact on performances
        @param locked(bool): updates are forbidden if True
        @param do_update(bool): if True, a full update is done after unlocking
            if set to False, widget state can be inconsistent, be sure to know
            what youa re doing!
        """
        log.debug(
            u"Contact lists updates are now {}".format(
                u"LOCKED" if locked else u"UNLOCKED"
            )
        )
        self._update_locked = locked
        if not locked and do_update:
            self.update()

    def update(self, entities=None, type_=None, profile=None):
        if not self._update_locked:
            for widget in self._widgets:
                widget.update(entities, type_, profile)


class QuickContactList(QuickWidget):
    """This class manage the visual representation of contacts"""

    SINGLE = False
    PROFILES_MULTIPLE = True
    # Can be linked to no profile (e.g. at the early frontend start)
    PROFILES_ALLOW_NONE = True

    def __init__(self, host, profiles):
        super(QuickContactList, self).__init__(host, None, profiles)

        # options
        # for next values, None means use indivual value per profile
        # True or False mean override these values for all profiles
        self.show_disconnected = None  # TODO
        self.show_empty_groups = None  # TODO
        self.show_resources = None  # TODO
        self.show_status = None  # TODO

    def postInit(self):
        """Method to be called by frontend after widget is initialised"""
        handler.register(self)

    @property
    def all_iter(self):
        return handler.all_iter

    @property
    def items(self):
        return handler.items

    @property
    def items_sorted(self):
        return handler.items_sorted

    def update(self, entities=None, type_=None, profile=None):
        """Update the display when something changed

        @param entities(iterable[jid.JID], None): updated entities,
            None to update the whole contact list
        @param type_(unicode, None): update type, may be:
            - C.UPDATE_DELETE: entity deleted
            - C.UPDATE_MODIFY: entity updated
            - C.UPDATE_ADD: entity added
            - C.UPDATE_SELECTION: selection modified
            or None for undefined update
            Note that events correspond to addition, modification and deletion
            of items on the whole contact list. If the contact is visible or not
            has no influence on the type_.
        @param profile(unicode, None): profile concerned with the update
            None if all profiles need to be updated
        """
        raise NotImplementedError

    def onDelete(self):
        QuickWidget.onDelete(self)
        handler.unregister(self)
