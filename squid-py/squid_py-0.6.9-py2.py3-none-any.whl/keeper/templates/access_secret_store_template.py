#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from squid_py.keeper import ContractBase
from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger('escrowAccessSecretStoreTemplate')


class EscrowAccessSecretStoreTemplate(ContractBase):
    """Class representing the EscrowAccessSecretStoreTemplate contract."""
    CONTRACT_NAME = 'EscrowAccessSecretStoreTemplate'
    AGREEMENT_CREATED_EVENT = 'AgreementCreated'

    def create_agreement(self, agreement_id, did, condition_ids, time_locks, time_outs,
                         consumer_address, account):
        """
        Create the service agreement. Return true if it is created successfully.

        :param agreement_id: id of the agreement, hex str
        :param did: DID, str
        :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
        :param time_locks: is a list of uint time lock values associated to each Condition, int
        :param time_outs: is a list of uint time out values associated to each Condition, int
        :param consumer_address: ethereum account address of consumer, hex str
        :param account: Account instance creating the agreement
        :return: bool
        """
        logger.info(
            f'Creating agreement {agreement_id} with did={did}, consumer={consumer_address}.')
        tx_hash = self.send_transaction(
            'createAgreement',
            (agreement_id,
             did,
             condition_ids,
             time_locks,
             time_outs,
             consumer_address),
            transact={'from': account.address,
                      'passphrase': account.password}
        )
        receipt = self.get_tx_receipt(tx_hash)
        return receipt and receipt.status == 1

    def get_condition_types(self):
        """

        :return:
        """
        return self.contract_concise.getConditionTypes()

    def get_agreement_data(self, agreement_id):
        """

        :param agreement_id: id of the agreement, hex str
        :return:
        """
        consumer, provider = self.contract_concise.getAgreementData(agreement_id)
        return consumer, provider

    def get_agreement_consumer(self, agreement_id):
        """

        :param agreement_id: id of the agreement, hex str
        :return:
        """
        data = self.get_agreement_data(agreement_id)
        return data[0] if data and len(data) > 1 else None

    def subscribe_agreement_created(self, agreement_id, timeout, callback, args, wait=False):
        """
        Subscribe to an agreement created.

        :param agreement_id: id of the agreement, hex str
        :param timeout:
        :param callback:
        :param args:
        :param wait: if true block the listener until get the event, bool
        :return:
        """
        logger.info(
            f'Subscribing {self.AGREEMENT_CREATED_EVENT} event with agreement id {agreement_id}.')
        return self.subscribe_to_event(
            self.AGREEMENT_CREATED_EVENT,
            timeout,
            {'_agreementId': Web3Provider.get_web3().toBytes(hexstr=agreement_id)},
            callback=callback,
            args=args,
            wait=wait
        )
