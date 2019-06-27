#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
# Copyright (C) 2011-2019 Jérôme Poisson <goffi@goffi.org>

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

# from sat.core.i18n import _, D_
from sat.core.log import getLogger

log = getLogger(__name__)


from sat_frontends.quick_frontend.constants import Const as C
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.tools import jid
from sat.tools.common import data_format

try:
    # FIXME: to be removed when an acceptable solution is here
    unicode("")  # XXX: unicode doesn't exist in pyjamas
except (
    TypeError,
    AttributeError,
):  # Error raised is not the same depending on pyjsbuild options
    unicode = str

ENTRY_CLS = None
COMMENTS_CLS = None


class Item(object):
    """Manage all (meta)data of an item"""

    def __init__(self, data):
        """
        @param data(dict): microblog data as return by bridge methods
            if data values are not defined, set default values
        """
        self.id = data["id"]
        self.title = data.get("title")
        self.title_rich = None
        self.title_xhtml = data.get("title_xhtml")
        self.tags = data.get('tags', [])
        self.content = data.get("content")
        self.content_rich = None
        self.content_xhtml = data.get("content_xhtml")
        self.author = data["author"]
        try:
            author_jid = data["author_jid"]
            self.author_jid = jid.JID(author_jid) if author_jid else None
        except KeyError:
            self.author_jid = None

        self.author_verified = data.get("author_jid_verified", False)

        try:
            self.updated = float(
                data["updated"]
            )  # XXX: int doesn't work here (pyjamas bug)
        except KeyError:
            self.updated = None

        try:
            self.published = float(
                data["published"]
            )  # XXX: int doesn't work here (pyjamas bug)
        except KeyError:
            self.published = None

        self.comments = data.get("comments")
        try:
            self.comments_service = jid.JID(data["comments_service"])
        except KeyError:
            self.comments_service = None
        self.comments_node = data.get("comments_node")

    # def loadComments(self):
    #     """Load all the comments"""
    #     index = str(main_entry.comments_count - main_entry.hidden_count)
    #     rsm = {'max': str(main_entry.hidden_count), 'index': index}
    #     self.host.bridge.call('getMblogComments', self.mblogsInsert, main_entry.comments_service, main_entry.comments_node, rsm)


class EntriesManager(object):
    """Class which manages list of (micro)blog entries"""

    def __init__(self, manager):
        """
        @param manager (EntriesManager, None): parent EntriesManager
            must be None for QuickBlog (and only for QuickBlog)
        """
        self.manager = manager
        if manager is None:
            self.blog = self
        else:
            self.blog = manager.blog
        self.entries = []
        self.edit_entry = None

    @property
    def level(self):
        """indicate how deep is this entry in the tree

        if level == -1, we have a QuickBlog
        if level == 0, we have a main item
        else we have a comment
        """
        level = -1
        manager = self.manager
        while manager is not None:
            level += 1
            manager = manager.manager
        return level

    def _addMBItems(self, items_tuple, service=None, node=None):
        """Add Microblog items to this panel
        update is NOT called after addition

        @param items_tuple(tuple): (items_data,items_metadata) tuple as returned by mbGet
        """
        items, metadata = items_tuple
        for item in items:
            self.addEntry(item, service=service, node=node, with_update=False)

    def _addMBItemsWithComments(self, items_tuple, service=None, node=None):
        """Add Microblog items to this panel
        update is NOT called after addition

        @param items_tuple(tuple): (items_data,items_metadata) tuple as returned by mbGet
        """
        items, metadata = items_tuple
        for item, comments in items:
            self.addEntry(item, comments, service=service, node=node, with_update=False)

    def addEntry(self, item=None, comments=None, service=None, node=None,
                 with_update=True, editable=False, edit_entry=False):
        """Add a microblog entry

        @param editable (bool): True if the entry can be modified
        @param item (dict, None): blog item data, or None for an empty entry
        @param comments (list, None): list of comments data if available
        @param service (jid.JID, None): service where the entry is coming from
        @param service (unicode, None): node hosting the entry
        @param with_update (bool): if True, udpate is called with the new entry
        @param edit_entry(bool): if True, will be in self.edit_entry instead of
            self.entries, so it can be managed separately (e.g. first or last
            entry regardless of sorting)
        """
        new_entry = ENTRY_CLS(self, item, comments, service=service, node=node)
        new_entry.setEditable(editable)
        if edit_entry:
            self.edit_entry = new_entry
        else:
            self.entries.append(new_entry)
        if with_update:
            self.update()
        return new_entry

    def update(self, entry=None):
        """Update the display with entries

        @param entry (Entry, None): if not None, must be the new entry.
            If None, all the items will be checked to update the display
        """
        # update is separated from addEntry to allow adding
        # several entries at once, and updating at the end
        raise NotImplementedError


class Entry(EntriesManager):
    """Graphical representation of an Item
    This class must be overriden by frontends"""

    def __init__(
        self, manager, item_data=None, comments_data=None, service=None, node=None
    ):
        """
        @param blog(QuickBlog): the parent QuickBlog
        @param manager(EntriesManager): the parent EntriesManager
        @param item_data(dict, None): dict containing the blog item data, or None for an empty entry
        @param comments_data(list, None): list of comments data
        """
        assert manager is not None
        EntriesManager.__init__(self, manager)
        self.service = service
        self.node = node
        self.editable = False
        self.reset(item_data)
        self.blog.id2entries[self.item.id] = self
        if self.item.comments:
            node_tuple = (self.item.comments_service, self.item.comments_node)
            self.blog.node2entries.setdefault(node_tuple, []).append(self)

    def reset(self, item_data):
        """Reset the entry with given data

        used during init (it's a set and not a reset then)
        or later (e.g. message sent, or cancellation of an edition
        @param idem_data(dict, None): data as in __init__
        """
        if item_data is None:
            self.new = True
            item_data = {
                "id": None,
                # TODO: find a best author value
                "author": self.blog.host.whoami.node,
            }
        else:
            self.new = False
        self.item = Item(item_data)
        self.author_jid = self.blog.host.whoami.bare if self.new else self.item.author_jid
        if self.author_jid is None and self.service and self.service.node:
            self.author_jid = self.service
        self.mode = (
            C.ENTRY_MODE_TEXT if self.item.content_xhtml is None else C.ENTRY_MODE_XHTML
        )

    def refresh(self):
        """Refresh the display when data have been modified"""
        pass

    def setEditable(self, editable=True):
        """tell if the entry can be edited or not

        @param editable(bool): True if the entry can be edited
        """
        # XXX: we don't use @property as property setter doesn't play well with pyjamas
        raise NotImplementedError

    def addComments(self, comments_data):
        """Add comments to this entry by calling addEntry repeatidly

        @param comments_data(tuple): data as returned by mbGetFromMany*RTResults
        """
        # TODO: manage seperator between comments of coming from different services/nodes
        for data in comments_data:
            service, node, failure, comments, metadata = data
            for comment in comments:
                if not failure:
                    self.addEntry(comment, service=jid.JID(service), node=node)
                else:
                    log.warning("getting comment failed: {}".format(failure))
        self.update()

    def send(self):
        """Send entry according to parent QuickBlog configuration and current level"""

        # keys to keep other than content*, title* and tag*
        # FIXME: see how to avoid comments node hijacking (someone could bind his post to another post's comments node)
        keys_to_keep = ("id", "comments", "author", "author_jid", "published")

        mb_data = {}
        for key in keys_to_keep:
            value = getattr(self.item, key)
            if value is not None:
                mb_data[key] = unicode(value)

        for prefix in ("content", "title"):
            for suffix in ("", "_rich", "_xhtml"):
                name = "{}{}".format(prefix, suffix)
                value = getattr(self.item, name)
                if value is not None:
                    mb_data[name] = value

        mb_data['tags'] = self.item.tags

        if self.blog.new_message_target not in (C.PUBLIC, C.GROUP):
            raise NotImplementedError

        if self.level == 0:
            mb_data["allow_comments"] = True

        if self.blog.new_message_target == C.GROUP:
            mb_data['groups'] = list(self.blog.targets)

        self.blog.host.bridge.mbSend(
            unicode(self.service or ""),
            self.node or "",
            data_format.serialise(mb_data),
            profile=self.blog.profile,
        )

    def delete(self):
        """Remove this Entry from parent manager

        This doesn't delete any entry in PubSub, just locally
        all children entries will be recursively removed too
        """
        # XXX: named delete and not remove to avoid conflict with pyjamas
        log.debug(u"deleting entry {}".format("EDIT ENTRY" if self.new else self.item.id))
        for child in self.entries:
            child.delete()
        try:
            self.manager.entries.remove(self)
        except ValueError:
            if self != self.manager.edit_entry:
                log.error(u"Internal Error: entry not found in manager")
            else:
                self.manager.edit_entry = None
        if not self.new:
            # we must remove references to self
            # in QuickBlog's dictionary
            del self.blog.id2entries[self.item.id]
            if self.item.comments:
                comments_tuple = (self.item.comments_service, self.item.comments_node)
                other_entries = self.blog.node2entries[comments_tuple].remove(self)
                if not other_entries:
                    del self.blog.node2entries[comments_tuple]

    def retract(self):
        """Retract this item from microblog node

        if there is a comments node, it will be purged too
        """
        # TODO: manage several comments nodes case.
        if self.item.comments:
            self.blog.host.bridge.psNodeDelete(
                unicode(self.item.comments_service) or "",
                self.item.comments_node,
                profile=self.blog.profile,
            )
        self.blog.host.bridge.mbRetract(
            unicode(self.service or ""),
            self.node or "",
            self.item.id,
            profile=self.blog.profile,
        )


class QuickBlog(EntriesManager, quick_widgets.QuickWidget):
    def __init__(self, host, targets, profiles=None):
        """Panel used to show microblog

        @param targets (tuple(unicode)): contact groups displayed in this panel.
            If empty, show all microblogs from all contacts. targets is also used
            to know where to send new messages.
        """
        EntriesManager.__init__(self, None)
        self.id2entries = {}  # used to find an entry with it's item id
        # must be kept up-to-date by Entry
        self.node2entries = {}  # same as above, values are lists in case of
        # two entries link to the same comments node
        if not targets:
            targets = ()  # XXX: we use empty tuple instead of None to workaround a pyjamas bug
            quick_widgets.QuickWidget.__init__(self, host, targets, C.PROF_KEY_NONE)
            self._targets_type = C.ALL
        else:
            assert isinstance(targets[0], basestring)
            quick_widgets.QuickWidget.__init__(self, host, targets[0], C.PROF_KEY_NONE)
            for target in targets[1:]:
                assert isinstance(target, basestring)
                self.addTarget(target)
            self._targets_type = C.GROUP

    @property
    def new_message_target(self):
        if self._targets_type == C.ALL:
            return C.PUBLIC
        elif self._targets_type == C.GROUP:
            return C.GROUP
        else:
            raise ValueError("Unkown targets type")

    def __str__(self):
        return u"Blog Widget [target: {}, profile: {}]".format(
            ", ".join(self.targets), self.profile
        )

    def _getResultsCb(self, data, rt_session):
        remaining, results = data
        log.debug(
            "Got {got_len} results, {rem_len} remaining".format(
                got_len=len(results), rem_len=remaining
            )
        )
        for result in results:
            service, node, failure, items_data, metadata = result
            for item_data in items_data:
                item_data[0] = data_format.deserialise(item_data[0])
                for item_metadata in item_data[1]:
                    item_metadata[3] = [data_format.deserialise(i) for i in item_metadata[3]]
            if not failure:
                self._addMBItemsWithComments((items_data, metadata),
                                             service=jid.JID(service))

        self.update()
        if remaining:
            self._getResults(rt_session)

    def _getResultsEb(self, failure):
        log.warning("microblog getFromMany error: {}".format(failure))

    def _getResults(self, rt_session):
        """Manage results from mbGetFromMany RT Session

        @param rt_session(str): session id as returned by mbGetFromMany
        """
        self.host.bridge.mbGetFromManyWithCommentsRTResult(
            rt_session,
            profile=self.profile,
            callback=lambda data: self._getResultsCb(data, rt_session),
            errback=self._getResultsEb,
        )

    def getAll(self):
        """Get all (micro)blogs from self.targets"""

        def gotSession(rt_session):
            self._getResults(rt_session)

        if self._targets_type in (C.ALL, C.GROUP):
            targets = tuple(self.targets) if self._targets_type is C.GROUP else ()
            self.host.bridge.mbGetFromManyWithComments(
                self._targets_type,
                targets,
                10,
                10,
                {},
                {"subscribe": C.BOOL_TRUE},
                profile=self.profile,
                callback=gotSession,
            )
            own_pep = self.host.whoami.bare
            self.host.bridge.mbGetFromManyWithComments(
                C.JID,
                (unicode(own_pep),),
                10,
                10,
                {},
                {},
                profile=self.profile,
                callback=gotSession,
            )
        else:
            raise NotImplementedError(
                u"{} target type is not managed".format(self._targets_type)
            )

    def isJidAccepted(self, jid_):
        """Tell if a jid is actepted and must be shown in this panel

        @param jid_(jid.JID): jid to check
        @return: True if the jid is accepted
        """
        if self._targets_type == C.ALL:
            return True
        assert self._targets_type is C.GROUP  # we don't manage other types for now
        for group in self.targets:
            if self.host.contact_lists[self.profile].isEntityInGroup(jid_, group):
                return True
        return False

    def addEntryIfAccepted(self, service, node, mb_data, groups, profile):
        """add entry to this panel if it's acceptable

        This method check if the entry is new or an update,
        if it below to a know node, or if it acceptable anyway
        @param service(jid.JID): jid of the emitting pubsub service
        @param node(unicode): node identifier
        @param mb_data: microblog data
        @param groups(list[unicode], None): groups which can receive this entry
            None to accept everything
        @param profile: %(doc_profile)s
        """
        try:
            entry = self.id2entries[mb_data["id"]]
        except KeyError:
            # The entry is new
            try:
                parent_entries = self.node2entries[(service, node)]
            except:
                # The node is unknown,
                # we need to check that we can accept the entry
                if (
                    self.isJidAccepted(service)
                    or (
                        groups is None
                        and service == self.host.profiles[self.profile].whoami.bare
                    )
                    or (groups and groups.intersection(self.targets))
                ):
                    self.addEntry(mb_data, service=service, node=node)
            else:
                # the entry is a comment in a known node
                for parent_entry in parent_entries:
                    parent_entry.addEntry(mb_data, service=service, node=node)
        else:
            # The entry exist, it's an update
            entry.reset(mb_data)
            entry.refresh()

    def deleteEntryIfPresent(self, service, node, item_id, profile):
        """Delete and entry if present in this QuickBlog

        @param sender(jid.JID): jid of the entry sender
        @param mb_data: microblog data
        @param service(jid.JID): sending service
        @param node(unicode): hosting node
        """
        try:
            entry = self.id2entries[item_id]
        except KeyError:
            pass
        else:
            entry.delete()


def registerClass(type_, cls):
    global ENTRY_CLS, COMMENTS_CLS
    if type_ == "ENTRY":
        ENTRY_CLS = cls
    elif type == "COMMENT":
        COMMENTS_CLS = cls
    else:
        raise ValueError("type_ should be ENTRY or COMMENT")
    if COMMENTS_CLS is None:
        COMMENTS_CLS = ENTRY_CLS
