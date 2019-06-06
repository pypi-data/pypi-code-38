#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from eth_utils import add_0x_prefix

from squid_py.did import did_to_id


class OceanConditions:
    """Ocean conditions class."""

    def __init__(self, keeper):
        self._keeper = keeper

    def lock_reward(self, agreement_id, amount, account):
        """
        Lock reward condition.

        :param agreement_id: id of the agreement, hex str
        :param amount: Amount of tokens, int
        :param account: Account
        :return: bool
        """
        self._keeper.dispenser.request_tokens(amount, account)
        self._keeper.token.token_approve(self._keeper.lock_reward_condition.address, amount,
                                         account)
        return self._keeper.lock_reward_condition.fulfill(
            agreement_id, self._keeper.escrow_reward_condition.address, amount, account
        )

    def grant_access(self, agreement_id, did, grantee_address, account):
        """
        Grant access condition.

        :param agreement_id: id of the agreement, hex str
        :param did: DID, str
        :param grantee_address: Address, hex str
        :param account: Account
        :return:
        """
        return self._keeper.access_secret_store_condition.fulfill(
            agreement_id, add_0x_prefix(did_to_id(did)), grantee_address, account
        )

    def release_reward(self, agreement_id, amount, account):
        """
        Release reward condition.

        :param agreement_id: id of the agreement, hex str
        :param amount: Amount of tokens, int
        :param account: Account
        :return:
        """
        agreement_values = self._keeper.agreement_manager.get_agreement(agreement_id)
        consumer, provider = self._keeper.escrow_access_secretstore_template.get_agreement_data(
            agreement_id)
        access_id, lock_id = agreement_values.condition_ids[:2]
        return self._keeper.escrow_reward_condition.fulfill(
            agreement_id,
            amount,
            provider,
            consumer,
            lock_id,
            access_id,
            account
        )

    def refund_reward(self, agreement_id, amount, account):
        """
        Refund reaward condition.

        :param agreement_id: id of the agreement, hex str
        :param amount: Amount of tokens, int
        :param account: Account
        :return:
        """
        return self.release_reward(agreement_id, amount, account)
