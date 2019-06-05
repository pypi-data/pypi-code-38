#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from squid_py.keeper import ContractBase, utils
from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger('escrowAccessSecretStoreTemplate')


class ConditionBase(ContractBase):
    """Base class for all the Condition contract objects."""
    FULFILLED_EVENT = 'Fulfilled'

    def generate_id(self, agreement_id, types, values):
        """
        Generate id for the condition.

        :param agreement_id: id of the agreement, hex str
        :param types: list of types
        :param values: list of values
        :return: id, str
        """
        values_hash = utils.generate_multi_value_hash(types, values)
        return utils.generate_multi_value_hash(
            ['bytes32', 'address', 'bytes32'],
            [agreement_id, self.address, values_hash]
        )

    def _fulfill(self, *args, **kwargs):
        """
        Fulfill the condition.

        :param args:
        :param kwargs:
        :return: true if the condition was successfully fulfilled, bool
        """
        tx_hash = self.send_transaction('fulfill', args, **kwargs)
        receipt = self.get_tx_receipt(tx_hash)
        return receipt.status == 1

    def abort_by_timeout(self, condition_id):
        """

        :param condition_id: id of the condition, str
        :return:
        """
        tx_hash = self.contract_concise.abortByTimeOut(condition_id)
        receipt = self.get_tx_receipt(tx_hash)
        return receipt.status == 1

    def _hash_values(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.contract_concise.hashValues(*args, **kwargs)

    def subscribe_condition_fulfilled(self, agreement_id, timeout, callback, args,
                                      timeout_callback=None, wait=False):
        """
        Subscribe to the condition fullfilled event.

        :param agreement_id: id of the agreement, hex str
        :param timeout:
        :param callback:
        :param args:
        :param timeout_callback:
        :param wait: if true block the listener until get the event, bool
        :return:
        """
        logger.info(
            f'Subscribing {self.FULFILLED_EVENT} event with agreement id {agreement_id}.')
        return self.subscribe_to_event(
            self.FULFILLED_EVENT,
            timeout,
            {'_agreementId': Web3Provider.get_web3().toBytes(hexstr=agreement_id)},
            callback=callback,
            timeout_callback=timeout_callback,
            args=args,
            wait=wait
        )
