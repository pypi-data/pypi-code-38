# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#

import logging

from ..actions import ACTION_STORE, ActionName
from ..ip_radix import Radix
from ..rules import RuleCallback
from ..sdk import events

LOGGER = logging.getLogger(__name__)


class IPBlacklistCB(RuleCallback):
    def __init__(self, *args, **kwargs):
        super(IPBlacklistCB, self).__init__(*args, **kwargs)
        self.networks = Radix(None)
        for blacklist in self.data["values"]:
            self.networks.insert(blacklist, '/' in blacklist)
        LOGGER.debug("Blacklisted IP networks: %s", self.networks)

    def pre(self, original, *args, **kwargs):
        request = self.storage.get_current_request()
        if request is None or not request.client_ip:
            return
        network = self.networks.match(request.client_ip)
        if network is not None:
            LOGGER.debug(
                "IP %s belongs to blacklisted network %s",
                request.client_ip,
                network,
            )
            self.record_observation("blacklisted", network, 1)
            return {
                "status": "raise",
                "data": network,
                "rule_name": self.rule_name,
            }

        # Handle security actions.
        action = ACTION_STORE.get_for_ip(request.client_ip)
        if not action:
            LOGGER.debug("IP %s is not blacklisted", request.client_ip)
            return
        events.track_action(
            action,
            {"ip_address": str(request.client_ip)},
            storage=self.storage,
        )
        if action.name == ActionName.BLOCK_IP:
            LOGGER.debug(
                "IP %s is blacklisted by action %s",
                request.client_ip,
                action.iden,
            )
            return {"status": "action_block", "action_id": action.iden}
        else:  # action.name == ActionName.REDIRECT_IP:
            LOGGER.debug(
                "IP %s is redirected to %r by action %s",
                request.client_ip,
                action.target_url,
                action.iden,
            )
            return {
                "status": "action_redirect",
                "action_id": action.iden,
                "target_url": action.target_url,
            }
