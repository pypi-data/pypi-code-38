"""
    Keeper Contract Base

    All keeper contract inherit from this base class
"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from web3.utils.threads import Timeout

from squid_py.keeper.web3.contract import SquidContractFunction
from squid_py.keeper.web3_provider import Web3Provider

logger = logging.getLogger('keeper')


class ContractBase(object):
    """Base class for all contract objects."""
    CONTRACT_NAME = None

    def __init__(self, contract_name, dependencies=None):

        assert contract_name, 'param contract_name is required and must ' \
                              'match a valid keeper contract.'
        self.name = contract_name

        if not dependencies or 'ContractHandler' not in dependencies:
            dependencies = dict()
            from squid_py.keeper.contract_handler import ContractHandler
            dependencies['ContractHandler'] = ContractHandler

        self.contract_concise = dependencies['ContractHandler'].get_concise_contract(contract_name)
        self.contract = dependencies['ContractHandler'].get(contract_name)
        self.version = dependencies['ContractHandler'].get_contract_version(contract_name)

    @classmethod
    def get_instance(cls, dependencies=None):
        """
        Return an instance for a contract name.

        :param dependencies:
        :return: Contract base instance
        """
        assert cls is not ContractBase, 'ContractBase is not meant to be used directly.'
        assert cls.CONTRACT_NAME, 'CONTRACT_NAME must be set to a valid keeper contract name.'
        return cls(cls.CONTRACT_NAME, dependencies)

    @property
    def _contract_concise(self):
        return self.contract_concise

    @property
    def _contract(self):
        return self.contract

    @property
    def address(self):
        """Return the ethereum address of the solidity contract deployed
        in current keeper network.
        """
        return self._contract.address

    @property
    def events(self):
        """Expose the underlying contract's events.

        :return:
        """
        return self.contract.events

    @staticmethod
    def to_checksum_address(address):
        """
        Validate the address provided.

        :param address: Address, hex str
        :return: address, hex str
        """
        return Web3Provider.get_web3().toChecksumAddress(address)

    @staticmethod
    def get_tx_receipt(tx_hash):
        """
        Get the receipt of a tx.

        :param tx_hash: hash of the transaction
        :return: Tx receipt
        """
        try:
            Web3Provider.get_web3().eth.waitForTransactionReceipt(tx_hash, timeout=20)
        except Timeout:
            logger.info('Waiting for transaction receipt timed out.')
            return
        return Web3Provider.get_web3().eth.getTransactionReceipt(tx_hash)

    def subscribe_to_event(self, event_name, timeout, event_filter, callback=None,
                           timeout_callback=None, args=None, wait=False):
        """
        Create a listener for the event choose.

        :param event_name: name of the event to subscribe, str
        :param timeout:
        :param event_filter:
        :param callback:
        :param timeout_callback:
        :param args:
        :param wait: if true block the listener until get the event, bool
        :return:
        """
        from squid_py.keeper.event_listener import EventListener
        return EventListener(
            self.CONTRACT_NAME,
            event_name,
            args,
            filters=event_filter
        ).listen_once(
            callback,
            timeout_callback=timeout_callback,
            timeout=timeout,
            blocking=wait
        )

    def send_transaction(self, fn_name, fn_args, transact=None):
        """Calls a smart contract function using either `personal_sendTransaction` (if
        passphrase is available) or `ether_sendTransaction`.

        :param fn_name: str the smart contract function name
        :param fn_args: tuple arguments to pass to function above
        :param transact: dict arguments for the transaction such as from, gas, etc.
        :return:
        """
        contract_fn = getattr(self.contract.functions, fn_name)(*fn_args)
        contract_function = SquidContractFunction(
            contract_fn
        )
        return contract_function.transact(transact)

    def __str__(self):
        return f'{self.name} at {self.address}'
