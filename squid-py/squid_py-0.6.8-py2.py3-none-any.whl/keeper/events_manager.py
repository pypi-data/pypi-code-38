#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from squid_py.keeper.multi_event_listener import MultiEventListener
from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger(__name__)


class EventsManager:
    """Manage the main keeper events listeners necessary for processing service agreements."""
    _instance = None

    def __init__(self, keeper):
        self._keeper = keeper

        self.agreement_listener = MultiEventListener(
            self._keeper.escrow_access_secretstore_template.CONTRACT_NAME,
            self._keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT
        )
        self.lock_cond_listener = MultiEventListener(
            self._keeper.lock_reward_condition.CONTRACT_NAME,
            self._keeper.lock_reward_condition.FULFILLED_EVENT
        )
        self.access_cond_listener = MultiEventListener(
            self._keeper.access_secret_store_condition.CONTRACT_NAME,
            self._keeper.access_secret_store_condition.FULFILLED_EVENT
        )
        self.reward_cond_listener = MultiEventListener(
            self._keeper.escrow_reward_condition.CONTRACT_NAME,
            self._keeper.escrow_reward_condition.FULFILLED_EVENT
        )

    @staticmethod
    def get_instance(keeper):
        if not EventsManager._instance:
            EventsManager._instance = EventsManager(keeper)

        return EventsManager._instance

    def start_all_listeners(self):
        self.agreement_listener.start_watching()
        self.lock_cond_listener.start_watching()
        self.access_cond_listener.start_watching()
        self.reward_cond_listener.start_watching()

    def stop_all_listeners(self):
        self.agreement_listener.stop_watching()
        self.lock_cond_listener.stop_watching()
        self.access_cond_listener.stop_watching()
        self.reward_cond_listener.stop_watching()

    def watch_agreement_created_event(self, agreement_id, callback, timeout_callback,
                                      args, timeout, start_time=None):
        self.agreement_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )

    def watch_lock_reward_event(self, agreement_id, callback, timeout_callback,
                                args, timeout, start_time=None):
        self.lock_cond_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )

    def watch_access_event(self, agreement_id, callback, timeout_callback,
                           args, timeout, start_time=None):
        self.access_cond_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )

    def watch_reward_event(self, agreement_id, callback, timeout_callback,
                           args, timeout, start_time=None):
        self.reward_cond_listener.add_event_filter(
            '_agreementId',
            Web3Provider.get_web3().toBytes(hexstr=agreement_id),
            callback,
            timeout_callback,
            args,
            timeout,
            start_time
        )
