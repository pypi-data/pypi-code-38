"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os

from eth_utils import big_endian_to_int

from squid_py.config_provider import ConfigProvider
from squid_py.keeper.agreements.agreement_manager import AgreementStoreManager
from squid_py.keeper.conditions.access import AccessSecretStoreCondition
from squid_py.keeper.conditions.condition_manager import ConditionStoreManager
from squid_py.keeper.conditions.escrow_reward import EscrowRewardCondition
from squid_py.keeper.conditions.hash_lock import HashLockCondition
from squid_py.keeper.conditions.lock_reward import LockRewardCondition
from squid_py.keeper.conditions.sign import SignCondition
from squid_py.keeper.didregistry import DIDRegistry
from squid_py.keeper.dispenser import Dispenser
from squid_py.keeper.templates.access_secret_store_template import EscrowAccessSecretStoreTemplate
from squid_py.keeper.templates.template_manager import TemplateStoreManager
from squid_py.keeper.token import Token
from squid_py.keeper.web3.signature import SignatureFix
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.utils.utilities import split_signature


class Keeper(object):
    """The Keeper class aggregates all contracts in the Ocean Protocol node."""

    DEFAULT_NETWORK_NAME = 'development'
    _network_name_map = {
        1: 'Main',
        2: 'Morden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan',
        77: 'POA_Sokol',
        99: 'POA_Core',
        8995: 'nile',
        8996: 'spree',
        2199: 'duero'
    }

    def __init__(self, artifacts_path=None):
        self.network_name = Keeper.get_network_name(Keeper.get_network_id())
        if not artifacts_path:
            artifacts_path = ConfigProvider.get_config().keeper_path
        self.artifacts_path = artifacts_path
        self.accounts = Web3Provider.get_web3().eth.accounts

        self.dispenser = Dispenser.get_instance()
        self.token = Token.get_instance()
        self.did_registry = DIDRegistry.get_instance()
        self.template_manager = TemplateStoreManager.get_instance()
        self.escrow_access_secretstore_template = EscrowAccessSecretStoreTemplate.get_instance()
        self.agreement_manager = AgreementStoreManager.get_instance()
        self.condition_manager = ConditionStoreManager.get_instance()
        self.sign_condition = SignCondition.get_instance()
        self.lock_reward_condition = LockRewardCondition.get_instance()
        self.escrow_reward_condition = EscrowRewardCondition.get_instance()
        self.access_secret_store_condition = AccessSecretStoreCondition.get_instance()
        self.hash_lock_condition = HashLockCondition.get_instance()

    @staticmethod
    def get_instance():
        """Return the Keeper instance (singleton)."""
        return Keeper()

    @staticmethod
    def get_network_name(network_id):
        """
        Return the keeper network name based on the current ethereum network id.
        Return `development` for every network id that is not mapped.

        :param network_id: Network id, int
        :return: Network name, str
        """
        if os.environ.get('KEEPER_NETWORK_NAME'):
            logging.debug('keeper network name overridden by an environment variable: {}'.format(
                os.environ.get('KEEPER_NETWORK_NAME')))
            return os.environ.get('KEEPER_NETWORK_NAME')

        return Keeper._network_name_map.get(network_id, Keeper.DEFAULT_NETWORK_NAME)

    @staticmethod
    def get_network_id():
        """
        Return the ethereum network id calling the `web3.version.network` method.

        :return: Network id, int
        """
        return int(Web3Provider.get_web3().version.network)

    @staticmethod
    def sign_hash(msg_hash, account):
        """

        :param msg_hash:
        :param account: Account
        :return: signature
        """
        return Web3Provider.get_web3().personal.sign(
            msg_hash, account.address, account.password
        )

    @staticmethod
    def ec_recover(message, signed_message):
        w3 = Web3Provider.get_web3()
        v, r, s = split_signature(w3, w3.toBytes(hexstr=signed_message))
        signature_object = SignatureFix(vrs=(v, big_endian_to_int(r), big_endian_to_int(s)))
        return Web3Provider.get_web3().personal.ecRecover(
            message,
            signature_object.to_hex_v_hacked())

    @staticmethod
    def unlock_account(account):
        """
        Unlock the account.

        :param account: Account
        :return:
        """
        return Web3Provider.get_web3().personal.unlockAccount(account.address, account.password)

    @staticmethod
    def get_ether_balance(address):
        """
        Get balance of an ethereum address.

        :param address: address, bytes32
        :return: balance, int
        """
        return Web3Provider.get_web3().eth.getBalance(address, block_identifier='latest')

    def get_condition_name_by_address(self, address):
        """Return the condition name for a given address."""
        if self.lock_reward_condition.address == address:
            return 'lockReward'
        elif self.access_secret_store_condition.address == address:
            return 'accessSecretStore'
        elif self.escrow_reward_condition.address == address:
            return 'escrowReward'
        else:
            logging.error(f'The current address {address} is not a condition address')
