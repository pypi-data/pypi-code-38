
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from squid_py.keeper import Keeper
from squid_py.keeper.utils import process_tx_receipt

logger = logging.getLogger(__name__)


def fulfill_lock_reward_condition(event, agreement_id, price, consumer_account):
    """
    Fulfill the lock reward condition.

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param price: Asset price, int
    :param consumer_account: Account instance of the consumer
    """
    logger.debug(f"about to lock reward after event {event}.")
    keeper = Keeper.get_instance()
    tx_hash = None
    try:
        keeper.token.token_approve(keeper.lock_reward_condition.address, price, consumer_account)
        tx_hash = keeper.lock_reward_condition.fulfill(
            agreement_id, keeper.escrow_reward_condition.address, price, consumer_account
        )
        process_tx_receipt(
            tx_hash,
            keeper.lock_reward_condition.FULFILLED_EVENT,
            'LockRewardCondition.Fulfilled'
        )
    except Exception as e:
        logger.debug(f'error locking reward: {e}')
        if not tx_hash:
            raise e


fulfillLockRewardCondition = fulfill_lock_reward_condition
