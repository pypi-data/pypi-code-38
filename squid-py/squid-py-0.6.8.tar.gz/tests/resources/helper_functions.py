#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import os
import pathlib

from examples import ExampleConfig
from squid_py import ConfigProvider
from squid_py.accounts.account import Account
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.ddo.ddo import DDO
from squid_py.ddo.metadata import Metadata
from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.ocean.ocean import Ocean
from squid_py.secret_store.secret_store_provider import SecretStoreProvider
from squid_py.utils.utilities import prepare_prefixed_hash
from tests.resources.mocks.brizo_mock import BrizoMock
from tests.resources.mocks.secret_store_mock import SecretStoreMock

PUBLISHER_INDEX = 1
CONSUMER_INDEX = 0


def get_resource_path(dir_name, file_name):
    base = os.path.realpath(__file__).split(os.path.sep)[1:-1]
    if dir_name:
        return pathlib.Path(os.path.join(os.path.sep, *base, dir_name, file_name))
    else:
        return pathlib.Path(os.path.join(os.path.sep, *base, file_name))


def init_ocn_tokens(ocn, account, amount=100):
    ocn.accounts.request_tokens(account, amount)
    Keeper.get_instance().token.token_approve(
        Keeper.get_instance().dispenser.address,
        amount,
        account
    )


def make_ocean_instance(account_index):
    ocn = Ocean(ExampleConfig.get_config())
    account = ocn.accounts.list()[account_index]
    if account_index == 0:
        account.password = ExampleConfig.get_config().get('keeper-contracts', 'parity.password')
    else:
        account.password = ExampleConfig.get_config().get('keeper-contracts', 'parity.password1')

    return ocn


def get_publisher_account(config):
    address = os.getenv('PARITY_ADDRESS')
    if address:
        pswrd = os.getenv('PARITY_PASSWORD')
        return Account(Web3Provider.get_web3().toChecksumAddress(address), pswrd)

    acc = get_account_from_config(config, 'parity.address', 'parity.password')
    if acc is None:
        acc = Account(Keeper.get_instance().accounts[0])
    return acc


def get_consumer_account(config):
    address = os.getenv('PARITY_ADDRESS1')
    if address:
        pswrd = os.getenv('PARITY_PASSWORD1')
        return Account(Web3Provider.get_web3().toChecksumAddress(address), pswrd)

    acc = get_account_from_config(config, 'parity.address1', 'parity.password1')
    if acc is None:
        acc = Account(Keeper.get_instance().accounts[1])
    return acc


def get_publisher_ocean_instance(init_tokens=True, use_ss_mock=True, use_brizo_mock=True):
    ocn = make_ocean_instance(PUBLISHER_INDEX)
    account = get_publisher_account(ConfigProvider.get_config())
    if account.address in ocn.accounts.accounts_addresses:
        ocn.main_account = account
    else:
        ocn.main_account = ocn.accounts.list()[0]

    if init_tokens:
        init_ocn_tokens(ocn, ocn.main_account)
    if use_ss_mock:
        SecretStoreProvider.set_secret_store_class(SecretStoreMock)
    if use_brizo_mock:
        BrizoProvider.set_brizo_class(BrizoMock)

    return ocn


def get_consumer_ocean_instance(init_tokens=True, use_ss_mock=True, use_brizo_mock=True):
    ocn = make_ocean_instance(CONSUMER_INDEX)
    account = get_consumer_account(ConfigProvider.get_config())
    if account.address in ocn.accounts.accounts_addresses:
        ocn.main_account = account
    else:
        ocn.main_account = ocn.accounts.list()[1]

    if init_tokens:
        init_ocn_tokens(ocn, ocn.main_account)
    if use_ss_mock:
        SecretStoreProvider.set_secret_store_class(SecretStoreMock)
    if use_brizo_mock:
        BrizoProvider.set_brizo_class(BrizoMock)

    return ocn


def get_account_from_config(config, config_account_key, config_account_password_key):
    address = None
    if config.has_option('keeper-contracts', config_account_key):
        address = config.get('keeper-contracts', config_account_key)
        address = Web3Provider.get_web3().toChecksumAddress(address) if address else None

    if not (address and address in Keeper.get_instance().accounts):
        return None

    password = None
    if address and config.has_option('keeper-contracts', config_account_password_key):
        password = config.get('keeper-contracts', config_account_password_key)

    return Account(address, password)


def get_ddo_sample():
    return DDO(json_filename=get_resource_path('ddo', 'ddo_sa_sample.json'))


def get_registered_ddo(ocean_instance, account):
    ddo = ocean_instance.assets.create(Metadata.get_example(), account)
    return ddo


def log_event(event_name):
    def _process_event(event):
        print(f'Received event {event_name}: {event}')

    return _process_event


def verify_signature(_address, _agreement_hash, _signature, expected_match):
    w3 = Web3Provider.get_web3()
    prefixed_hash = prepare_prefixed_hash(_agreement_hash)
    recovered_address0 = w3.eth.account.recoverHash(prefixed_hash, signature=_signature)
    recovered_address1 = w3.eth.account.recoverHash(_agreement_hash, signature=_signature)
    print('original address: ', _address)
    print('w3.eth.account.recoverHash(prefixed_hash, signature=signature)  => ',
          recovered_address0)
    print('w3.eth.account.recoverHash(agreement_hash, signature=signature) => ',
          recovered_address1)
    assert _address == (recovered_address0, recovered_address1)[expected_match], \
        'Could not verify signature using address {}'.format(_address)


def get_metadata():
    path = get_resource_path('ddo', 'valid_metadata.json')
    assert path.exists(), f"{path} does not exist!"
    with open(path, 'r') as file_handle:
        metadata = file_handle.read()
    return json.loads(metadata)
