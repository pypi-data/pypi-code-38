
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from eth_utils import add_0x_prefix

from squid_py import ConfigProvider
from squid_py.brizo import BrizoProvider
from squid_py.did import did_to_id
from squid_py.did_resolver.did_resolver import DIDResolver
from squid_py.keeper import Keeper
from squid_py.secret_store import SecretStoreProvider

logger = logging.getLogger(__name__)


def fulfill_escrow_reward_condition(event, agreement_id, service_agreement, price, consumer_address,
                                    publisher_account, condition_ids):
    """

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param service_agreement: ServiceAgreement instance
    :param price: Asset price, int
    :param consumer_address: ethereum account address of consumer, hex str
    :param publisher_account: Account instance of the publisher
    :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
    :return:
    """
    if not event:
        logger.warning(f'`fulfill_escrow_reward_condition` got empty event: '
                       f'event listener timed out.')
        return

    logger.debug(f"release reward after event {event}.")
    access_id, lock_id = condition_ids[:2]
    logger.debug(f'fulfill_escrow_reward_condition: '
                 f'agreementId={agreement_id}'
                 f'price={price}, {type(price)}'
                 f'consumer={consumer_address},'
                 f'publisher={publisher_account.address},'
                 f'conditionIds={condition_ids}')
    assert price == service_agreement.get_price(), 'price mismatch.'
    assert isinstance(price, int), f'price expected to be int type, got type "{type(price)}"'
    try:
        Keeper.get_instance().escrow_reward_condition.fulfill(
            agreement_id,
            price,
            publisher_account.address,
            consumer_address,
            lock_id,
            access_id,
            publisher_account
        )
    except Exception as e:
        logger.error(f'Error when doing escrow_reward_condition.fulfill: {e}', exc_info=1)
        raise e


def refund_reward(event, agreement_id, did, service_agreement, price, consumer_account,
                  publisher_address, condition_ids):
    """
    Refund the reward to the publisher address.

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param price: Asset price, int
    :param consumer_account: Account instance of the consumer
    :param publisher_address: ethereum account address of publisher, hex str
    :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
    """
    logger.debug(f"trigger refund after event {event}.")
    access_id, lock_id = condition_ids[:2]
    name_to_parameter = {param.name: param for param in
                         service_agreement.condition_by_name['escrowReward'].parameters}
    document_id = add_0x_prefix(name_to_parameter['_documentId'].value)
    asset_id = add_0x_prefix(did_to_id(did))
    assert document_id == asset_id, f'document_id {document_id} <=> asset_id {asset_id} mismatch.'
    assert price == service_agreement.get_price(), 'price mismatch.'
    try:
        Keeper.get_instance().escrow_reward_condition.fulfill(
            agreement_id,
            price,
            publisher_address,
            consumer_account.address,
            lock_id,
            access_id,
            consumer_account
        )
    except Exception as e:
        logger.error(f'Error when doing escrow_reward_condition.fulfills: {e}',  exc_info=1)
        raise e


def consume_asset(event, agreement_id, did, service_agreement, consumer_account, consume_callback):
    """
    Consumption of an asset after get the event call.

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param consumer_account: Account instance of the consumer
    :param consume_callback:
    """
    logger.debug(f"consuming asset after event {event}.")
    if consume_callback:
        config = ConfigProvider.get_config()
        secret_store = SecretStoreProvider.get_secret_store(
            config.secret_store_url, config.parity_url, consumer_account
        )
        brizo = BrizoProvider.get_brizo()

        consume_callback(
            agreement_id,
            service_agreement.service_definition_id,
            DIDResolver(Keeper.get_instance().did_registry).resolve(did),
            consumer_account,
            ConfigProvider.get_config().downloads_path,
            brizo,
            secret_store
        )

    #     logger.info('Done consuming asset.')
    #
    # else:
    #     logger.info('Handling consume asset but the consume callback is not set. The user '
    #                 'can trigger consume asset directly using the agreementId and assetId.')


fulfillEscrowRewardCondition = fulfill_escrow_reward_condition
