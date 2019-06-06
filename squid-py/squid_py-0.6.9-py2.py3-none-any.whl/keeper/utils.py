"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from web3.utils.threads import Timeout

from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger(__name__)


def generate_multi_value_hash(types, values):
    """
    Return the hash of the given list of values.
    This is equivalent to packing and hashing values in a solidity smart contract
    hence the use of `soliditySha3`.

    :param types: list of solidity types expressed as strings
    :param values: list of values matching the `types` list
    :return: bytes
    """
    assert len(types) == len(values)
    return Web3Provider.get_web3().soliditySha3(
        types,
        values
    )


def process_tx_receipt(tx_hash, event, event_name):
    """
    Wait until the tx receipt is processed.

    :param tx_hash: hash of the transaction
    :param event: AttributeDict with the event data.
    :param event_name: name of the event to subscribe, str
    :return:
    """
    web3 = Web3Provider.get_web3()
    try:
        web3.eth.waitForTransactionReceipt(tx_hash, timeout=20)
    except Timeout:
        logger.info(f'Waiting for {event_name} transaction receipt timed out. '
                    f'Cannot verify receipt and event.')
        return

    receipt = web3.eth.getTransactionReceipt(tx_hash)
    event = event().processReceipt(receipt)
    if event:
        logger.info(f'Success: got {event_name} event after fulfilling condition.')
        logger.debug(
            f'Success: got {event_name} event after fulfilling condition. {receipt}, ::: {event}')
    else:
        logger.debug(f'Something is not right, cannot find the {event_name} event after calling the'
                     f' fulfillment condition. This is the transaction receipt {receipt}')

    if receipt and receipt.status == 0:
        logger.warning(
            f'Transaction failed: tx_hash {tx_hash}, tx event {event_name}, receipt {receipt}')
