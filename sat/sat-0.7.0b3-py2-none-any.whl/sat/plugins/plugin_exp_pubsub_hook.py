#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Pubsub Hooks
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
from sat.memory import persistent
from twisted.words.protocols.jabber import jid
from twisted.internet import defer

log = getLogger(__name__)

NS_PUBSUB_HOOK = "PUBSUB_HOOK"

PLUGIN_INFO = {
    C.PI_NAME: "PubSub Hook",
    C.PI_IMPORT_NAME: NS_PUBSUB_HOOK,
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0060"],
    C.PI_MAIN: "PubsubHook",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Experimental plugin to launch on action on Pubsub notifications"""
    ),
}

#  python module
HOOK_TYPE_PYTHON = u"python"
# python file path
HOOK_TYPE_PYTHON_FILE = u"python_file"
# python code directly
HOOK_TYPE_PYTHON_CODE = u"python_code"
HOOK_TYPES = (HOOK_TYPE_PYTHON, HOOK_TYPE_PYTHON_FILE, HOOK_TYPE_PYTHON_CODE)


class PubsubHook(object):
    def __init__(self, host):
        log.info(_(u"PubSub Hook initialization"))
        self.host = host
        self.node_hooks = {}  # keep track of the number of hooks per node (for all profiles)
        host.bridge.addMethod(
            "psHookAdd", ".plugin", in_sign="ssssbs", out_sign="", method=self._addHook
        )
        host.bridge.addMethod(
            "psHookRemove",
            ".plugin",
            in_sign="sssss",
            out_sign="i",
            method=self._removeHook,
        )
        host.bridge.addMethod(
            "psHookList",
            ".plugin",
            in_sign="s",
            out_sign="aa{ss}",
            method=self._listHooks,
        )

    @defer.inlineCallbacks
    def profileConnected(self, client):
        hooks = client._hooks = persistent.PersistentBinaryDict(
            NS_PUBSUB_HOOK, client.profile
        )
        client._hooks_temporary = {}
        yield hooks.load()
        for node in hooks:
            self._installNodeManager(client, node)

    def profileDisconnected(self, client):
        for node in client._hooks:
            self._removeNodeManager(client, node)

    def _installNodeManager(self, client, node):
        if node in self.node_hooks:
            log.debug(_(u"node manager already set for {node}").format(node=node))
            self.node_hooks[node] += 1
        else:
            # first hook on this node
            self.host.plugins["XEP-0060"].addManagedNode(
                node, items_cb=self._itemsReceived
            )
            self.node_hooks[node] = 0
            log.info(_(u"node manager installed on {node}").format(node=node))

    def _removeNodeManager(self, client, node):
        try:
            self.node_hooks[node] -= 1
        except KeyError:
            log.error(_(u"trying to remove a {node} without hook").format(node=node))
        else:
            if self.node_hooks[node] == 0:
                del self.node_hooks[node]
                self.host.plugins["XEP-0060"].removeManagedNode(node, self._itemsReceived)
                log.debug(_(u"hook removed"))
            else:
                log.debug(_(u"node still needed for an other hook"))

    def installHook(self, client, service, node, hook_type, hook_arg, persistent):
        if hook_type not in HOOK_TYPES:
            raise exceptions.DataError(
                _(u"{hook_type} is not handled").format(hook_type=hook_type)
            )
        if hook_type != HOOK_TYPE_PYTHON_FILE:
            raise NotImplementedError(
                _(u"{hook_type} hook type not implemented yet").format(
                    hook_type=hook_type
                )
            )
        self._installNodeManager(client, node)
        hook_data = {"service": service, "type": hook_type, "arg": hook_arg}

        if persistent:
            hooks_list = client._hooks.setdefault(node, [])
            hooks_list.append(hook_data)
            client._hooks.force(node)
        else:
            hooks_list = client._hooks_temporary.setdefault(node, [])
            hooks_list.append(hook_data)

        log.info(
            _(u"{persistent} hook installed on {node} for {profile}").format(
                persistent=_(u"persistent") if persistent else _(u"temporary"),
                node=node,
                profile=client.profile,
            )
        )

    def _itemsReceived(self, client, itemsEvent):
        node = itemsEvent.nodeIdentifier
        for hooks in (client._hooks, client._hooks_temporary):
            if node not in hooks:
                continue
            hooks_list = hooks[node]
            for hook_data in hooks_list[:]:
                if hook_data["service"] != itemsEvent.sender.userhostJID():
                    continue
                try:
                    callback = hook_data["callback"]
                except KeyError:
                    # first time we get this hook, we create the callback
                    hook_type = hook_data["type"]
                    try:
                        if hook_type == HOOK_TYPE_PYTHON_FILE:
                            hook_globals = {}
                            execfile(hook_data["arg"], hook_globals)
                            callback = hook_globals["hook"]
                        else:
                            raise NotImplementedError(
                                _(u"{hook_type} hook type not implemented yet").format(
                                    hook_type=hook_type
                                )
                            )
                    except Exception as e:
                        log.warning(
                            _(
                                u"Can't load Pubsub hook at node {node}, it will be removed: {reason}"
                            ).format(node=node, reason=e)
                        )
                        hooks_list.remove(hook_data)
                        continue

                for item in itemsEvent.items:
                    try:
                        callback(self.host, client, item)
                    except Exception as e:
                        log.warning(
                            _(
                                u"Error while running Pubsub hook for node {node}: {msg}"
                            ).format(node=node, msg=e)
                        )

    def _addHook(self, service, node, hook_type, hook_arg, persistent, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service) if service else client.jid.userhostJID()
        return self.addHook(
            client,
            service,
            unicode(node),
            unicode(hook_type),
            unicode(hook_arg),
            persistent,
        )

    def addHook(self, client, service, node, hook_type, hook_arg, persistent):
        r"""Add a hook which will be triggered on a pubsub notification

        @param service(jid.JID): service of the node
        @param node(unicode): Pubsub node
        @param hook_type(unicode): type of the hook, one of:
            - HOOK_TYPE_PYTHON: a python module (must be in path)
                module must have a "hook" method which will be called
            - HOOK_TYPE_PYTHON_FILE: a python file
                file must have a "hook" method which will be called
            - HOOK_TYPE_PYTHON_CODE: direct python code
                /!\ Python hooks will be executed in SàT context,
                with host, client and item as arguments, it means that:
                    - they can do whatever they wants, so don't run untrusted hooks
                    - they MUST NOT BLOCK, they are run in Twisted async environment and blocking would block whole SàT process
                    - item are domish.Element
        @param hook_arg(unicode): argument of the hook, depending on the hook_type
            can be a module path, file path, python code
        """
        assert service is not None
        return self.installHook(client, service, node, hook_type, hook_arg, persistent)

    def _removeHook(self, service, node, hook_type, hook_arg, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service) if service else client.jid.userhostJID()
        return self.removeHook(client, service, node, hook_type or None, hook_arg or None)

    def removeHook(self, client, service, node, hook_type=None, hook_arg=None):
        """Remove a persistent or temporaty root

        @param service(jid.JID): service of the node
        @param node(unicode): Pubsub node
        @param hook_type(unicode, None): same as for [addHook]
            match all if None
        @param hook_arg(unicode, None): same as for [addHook]
            match all if None
        @return(int): number of hooks removed
        """
        removed = 0
        for hooks in (client._hooks, client._hooks_temporary):
            if node in hooks:
                for hook_data in hooks[node]:
                    if (
                        service != hook_data[u"service"]
                        or hook_type is not None
                        and hook_type != hook_data[u"type"]
                        or hook_arg is not None
                        and hook_arg != hook_data[u"arg"]
                    ):
                        continue
                    hooks[node].remove(hook_data)
                    removed += 1
                    if not hooks[node]:
                        #  no more hooks, we can remove the node
                        del hooks[node]
                        self._removeNodeManager(client, node)
                    else:
                        if hooks == client._hooks:
                            hooks.force(node)
        return removed

    def _listHooks(self, profile):
        hooks_list = self.listHooks(self.host.getClient(profile))
        for hook in hooks_list:
            hook[u"service"] = hook[u"service"].full()
            hook[u"persistent"] = C.boolConst(hook[u"persistent"])
        return hooks_list

    def listHooks(self, client):
        """return list of registered hooks"""
        hooks_list = []
        for hooks in (client._hooks, client._hooks_temporary):
            persistent = hooks is client._hooks
            for node, hooks_data in hooks.iteritems():
                for hook_data in hooks_data:
                    hooks_list.append(
                        {
                            u"service": hook_data[u"service"],
                            u"node": node,
                            u"type": hook_data[u"type"],
                            u"arg": hook_data[u"arg"],
                            u"persistent": persistent,
                        }
                    )
        return hooks_list
