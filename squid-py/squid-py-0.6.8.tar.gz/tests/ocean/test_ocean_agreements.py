#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from unittest.mock import MagicMock, Mock

import pytest

from squid_py import ConfigProvider
from squid_py.agreements.service_agreement_template import ServiceAgreementTemplate
from squid_py.agreements.service_types import ServiceTypes
from squid_py.assets.asset_consumer import AssetConsumer
from squid_py.keeper import Keeper
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.ocean.ocean_agreements import OceanAgreements
from tests.resources.helper_functions import (get_ddo_sample, log_event)
from tests.resources.tiers import e2e_test


@pytest.fixture
def ocean_agreements():
    keeper = Keeper.get_instance()
    w3 = Web3Provider.get_web3()
    did_resolver = Mock()
    ddo = get_ddo_sample()
    service = ddo.get_service(ServiceTypes.ASSET_ACCESS)
    service.update_value(
        ServiceAgreementTemplate.TEMPLATE_ID_KEY,
        w3.toChecksumAddress("0x00bd138abd70e2f00903268f3db08f2d25677c9e")
    )
    did_resolver.resolve = MagicMock(return_value=ddo)
    consumer_class = Mock
    consumer_class.download = MagicMock(return_value='')
    return OceanAgreements(
        keeper,
        did_resolver,
        AssetConsumer,
        ConfigProvider.get_config()
    )


def test_prepare_agreement(ocean_agreements):
    # consumer_account = get_consumer_account(ConfigProvider.get_config())
    # ddo = get_ddo_sample()
    # ocean_agreements.prepare(ddo.did, ServiceTypes.ASSET_ACCESS, consumer_account.address)
    # :TODO:
    pass


def test_send_agreement(ocean_agreements):
    pass


def test_create_agreement(ocean_agreements):
    pass


@e2e_test
def test_agreement_release_reward():
    pass


@e2e_test
def test_agreement_refund_reward():
    pass


def test_agreement_status(setup_agreements_enviroment, ocean_agreements):
    (
        keeper,
        publisher_acc,
        consumer_acc,
        agreement_id,
        asset_id,
        price,
        service_agreement,
        (lock_cond_id, access_cond_id, escrow_cond_id),

    ) = setup_agreements_enviroment

    success = keeper.escrow_access_secretstore_template.create_agreement(
        agreement_id,
        asset_id,
        [access_cond_id, lock_cond_id, escrow_cond_id],
        service_agreement.conditions_timelocks,
        service_agreement.conditions_timeouts,
        consumer_acc.address,
        publisher_acc
    )
    print('create agreement: ', success)
    assert success, f'createAgreement failed {success}'
    event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id,
        10,
        log_event(keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AgreementCreated '
    assert ocean_agreements.status(agreement_id) == {"agreementId": agreement_id,
                                                     "conditions": {"lockReward": 1,
                                                                    "accessSecretStore": 1,
                                                                    "escrowReward": 1
                                                                    }
                                                     }
    # keeper.dispenser.request_tokens(price, consumer_acc)

    # keeper.token.token_approve(keeper.lock_reward_condition.address, price, consumer_acc)
    ocean_agreements.conditions.lock_reward(agreement_id,price, consumer_acc)
    # keeper.lock_reward_condition.fulfill(
    #     agreement_id, keeper.escrow_reward_condition.address, price, consumer_acc)
    event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.lock_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for LockRewardCondition.Fulfilled'
    assert ocean_agreements.status(agreement_id) == {"agreementId": agreement_id,
                                                     "conditions": {"lockReward": 2,
                                                                    "accessSecretStore": 1,
                                                                    "escrowReward": 1
                                                                    }
                                                     }
    keeper.access_secret_store_condition.fulfill(
        agreement_id, asset_id, consumer_acc.address, publisher_acc)
    event = keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        20,
        log_event(keeper.access_secret_store_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AccessSecretStoreCondition.Fulfilled'
    assert ocean_agreements.status(agreement_id) == {"agreementId": agreement_id,
                                                     "conditions": {"lockReward": 2,
                                                                    "accessSecretStore": 2,
                                                                    "escrowReward": 1
                                                                    }
                                                     }
    keeper.escrow_reward_condition.fulfill(
        agreement_id, price, publisher_acc.address,
        consumer_acc.address, lock_cond_id,
        access_cond_id, publisher_acc
    )
    event = keeper.escrow_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.escrow_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for EscrowReward.Fulfilled'
    assert ocean_agreements.status(agreement_id) == {"agreementId": agreement_id,
                                                     "conditions": {"lockReward": 2,
                                                                    "accessSecretStore": 2,
                                                                    "escrowReward": 2
                                                                    }
                                                     }
