"""Test ocean class."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

import pytest
from web3 import Web3

from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.brizo.brizo import Brizo
from squid_py.ddo.ddo import DDO
from squid_py.ddo.metadata import Metadata
from squid_py.did import DID
from squid_py.exceptions import OceanDIDNotFound
from squid_py.keeper import Keeper
from tests.resources.helper_functions import get_resource_path, log_event, verify_signature
from tests.resources.mocks.brizo_mock import BrizoMock
from tests.resources.tiers import e2e_test


@e2e_test
def test_ocean_instance(publisher_ocean_instance):
    assert publisher_ocean_instance.tokens
    assert publisher_ocean_instance.agreements
    assert publisher_ocean_instance.assets
    assert publisher_ocean_instance.accounts
    assert publisher_ocean_instance.services


@e2e_test
def test_register_asset(publisher_ocean_instance):
    logging.debug("".format())
    sample_ddo_path = get_resource_path('ddo', 'ddo_sa_sample.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup account
    ##########################################################
    publisher = publisher_ocean_instance.main_account

    # ensure Ocean token balance
    if publisher_ocean_instance.accounts.balance(publisher).ocn == 0:
        publisher_ocean_instance.accounts.request_tokens(publisher, 200)

    # You will need some token to make this transfer!
    assert publisher_ocean_instance.accounts.balance(publisher).ocn > 0

    ##########################################################
    # Create an asset DDO with valid metadata
    ##########################################################
    asset = DDO(json_filename=sample_ddo_path)

    ##########################################################
    # Register using high-level interface
    ##########################################################
    publisher_ocean_instance.assets.create(asset.metadata, publisher)


@e2e_test
def test_resolve_did(publisher_ocean_instance):
    # prep ddo
    metadata = Metadata.get_example()
    publisher = publisher_ocean_instance.main_account
    original_ddo = publisher_ocean_instance.assets.create(metadata, publisher)

    # happy path
    did = original_ddo.did
    ddo = publisher_ocean_instance.assets.resolve(did).as_dictionary()
    original = original_ddo.as_dictionary()
    assert ddo['publicKey'] == original['publicKey']
    assert ddo['authentication'] == original['authentication']
    assert ddo['service']
    assert original['service']
    assert ddo['service'][:-1] == original['service'][:-1]
    # assert ddo == original_ddo.as_dictionary(), 'Resolved ddo does not match original.'

    # Can't resolve unregistered asset
    unregistered_did = DID.did()
    with pytest.raises(OceanDIDNotFound):
        publisher_ocean_instance.assets.resolve(unregistered_did)

    # Raise error on bad did
    invalid_did = "did:op:0123456789"
    with pytest.raises(OceanDIDNotFound):
        publisher_ocean_instance.assets.resolve(invalid_did)


@e2e_test
def test_sign_agreement(publisher_ocean_instance, consumer_ocean_instance, registered_ddo):
    # point consumer_ocean_instance's brizo mock to the publisher's ocean instance
    Brizo.set_http_client(
        BrizoMock(publisher_ocean_instance, publisher_ocean_instance.main_account))

    consumer_ocn = consumer_ocean_instance
    consumer_acc = consumer_ocn.main_account
    keeper = Keeper.get_instance()

    pub_ocn = publisher_ocean_instance
    publisher_acc = pub_ocn.main_account

    service_definition_id = '1'
    did = registered_ddo.did
    asset_id = registered_ddo.asset_id
    ddo = consumer_ocn.assets.resolve(did)
    service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
    price = service_agreement.get_price()

    # Give consumer some tokens
    keeper.dispenser.request_tokens(price * 2, consumer_acc)

    agreement_id, signature = consumer_ocean_instance.agreements.prepare(
        did, service_agreement.service_definition_id, consumer_acc)

    success = publisher_ocean_instance.agreements.create(
        did,
        service_agreement.service_definition_id,
        agreement_id,
        signature,
        consumer_acc.address,
        publisher_acc
    )
    assert success, 'createAgreement failed.'

    event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id,
        10,
        log_event(keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AgreementCreated '

    # Verify condition types (condition contracts)
    agreement_values = keeper.agreement_manager.get_agreement(agreement_id)
    assert agreement_values.did == asset_id, ''
    cond_types = keeper.escrow_access_secretstore_template.get_condition_types()
    for i, cond_id in enumerate(agreement_values.condition_ids):
        cond = keeper.condition_manager.get_condition(cond_id)
        assert cond.type_ref == cond_types[i]
        assert int(cond.state) == 1

    access_cond_id, lock_cond_id, escrow_cond_id = agreement_values.condition_ids
    # Fulfill lock_reward_condition
    starting_balance = keeper.token.get_token_balance(keeper.escrow_reward_condition.address)
    keeper.token.token_approve(keeper.lock_reward_condition.address, price, consumer_acc)
    keeper.lock_reward_condition.fulfill(agreement_id, keeper.escrow_reward_condition.address,
                                         price, consumer_acc)
    assert keeper.token.get_token_balance(keeper.escrow_reward_condition.address) == (
            price + starting_balance), ''
    assert keeper.condition_manager.get_condition_state(lock_cond_id) == 2, ''
    event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.lock_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for LockRewardCondition.Fulfilled'

    # Fulfill access_secret_store_condition
    keeper.access_secret_store_condition.fulfill(
        agreement_id, asset_id, consumer_acc.address, publisher_acc)
    assert keeper.condition_manager.get_condition_state(access_cond_id) == 2, ''
    event = keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.access_secret_store_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AccessSecretStoreCondition.Fulfilled'

    # Fulfill escrow_reward_condition
    keeper.escrow_reward_condition.fulfill(
        agreement_id, price, publisher_acc.address,
        consumer_acc.address, lock_cond_id,
        access_cond_id, publisher_acc
    )
    assert keeper.condition_manager.get_condition_state(escrow_cond_id) == 2, ''
    event = keeper.escrow_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.escrow_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for EscrowReward.Fulfilled'

    # path = consumer_ocean_instance.assets.consume(
    #     agreement_id, did, service_definition_id,
    #     consumer_acc, ConfigProvider.get_config().downloads_path
    # )
    # print('All good, files are here: %s' % path)


@e2e_test
def test_verify_signature(consumer_ocean_instance):
    """
    squid-py currently uses `web3.eth.sign()` to sign the service agreement hash. This signing
    method
    uses ethereum `eth_sign` on the ethereum client which automatically prepends the
    message with text defined in EIP-191 as version 'E': `b'\\x19Ethereum Signed Message:\\n'`
    concatenated with the number of bytes in the message.

    It is more convenient to sign a message using `web3.eth.sign()` because it only requires the
    account address
    whereas `web3.eth.account.signHash()` requires a private_key to sign the message.
    `web3.eth.account.signHash()` also does not prepend anything to the message before signing.
    Messages signed via Metamask in pleuston use the latter method and current fail to verify in
    squid-py/brizo.
    The signature verification fails because recoverHash is being used on a prepended message but
    the signature
    created by `web3.eth.account.signHash()` does not add a prefix before signing.
    """

    # Signature created from Metamask (same as using `web3.eth.account.signHash()`)
    address = '0x8248039e67801Ac0B9d0e38201E963194abdb540'
    hex_agr_hash = '0xc8ea6bf6f4f4e2bf26a645dd4a1be20f5151c74964026c36efc2149bfae5f924'
    agreement_hash = Web3.toBytes(hexstr=hex_agr_hash)
    assert hex_agr_hash == '0x' + agreement_hash.hex()
    signature = (
        '0x200ce6aa55f0b4080c5f3a5dbe8385d2d196b0380cbdf388f79b6b004223c68a4f7972deb36417df8599155da2f903e43fe7e7eb40214db6bd6e55fd4c4fcf2a1c'
    )
    verify_signature(address, agreement_hash, signature, 1)

    # Signature created using `web3.eth.sign()` (squid-py, squid-js with no metamask)
    address = "0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e"
    hex_agr_hash = "0xeeaae0098b39fdf8fab6733152dd0ef54729ac486f9846450780c5cc9d44f5e8"
    agreement_hash = Web3.toBytes(hexstr=hex_agr_hash)
    signature = (
        "0x44fa549d33f5993f73e96f91cad01d9b37830da78494e35bda32a280d1b864ac020a761e872633c8149a5b63b65a1143f9f5a3be35822a9e90e0187d4a1f9d101c"
    )
    assert hex_agr_hash == '0x' + agreement_hash.hex()
    verify_signature(address, agreement_hash, signature, 0)
