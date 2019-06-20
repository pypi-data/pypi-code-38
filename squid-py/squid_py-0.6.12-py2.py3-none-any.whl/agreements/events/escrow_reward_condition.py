
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import time

from eth_utils import add_0x_prefix

from squid_py.agreements.utils import process_fulfill_condition
from squid_py.brizo import BrizoProvider
from squid_py.did import did_to_id
from squid_py.did_resolver.did_resolver import DIDResolver
from squid_py.keeper import Keeper
from squid_py.keeper.utils import process_tx_receipt
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.secret_store import SecretStoreProvider

logger = logging.getLogger(__name__)


def fulfill_escrow_reward_condition(event, agreement_id, service_agreement, price, consumer_address,
                                    publisher_account, condition_ids, escrow_condition_id):
    """

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param service_agreement: ServiceAgreement instance
    :param price: Asset price, int
    :param consumer_address: ethereum account address of consumer, hex str
    :param publisher_account: Account instance of the publisher
    :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
    :param escrow_condition_id: hex str the id of escrow reward condition at this `agreement_id`
    :return:
    """
    if not event:
        logger.warning(f'`fulfill_escrow_reward_condition` got empty event: '
                       f'event listener timed out.')
        return

    keeper = Keeper.get_instance()
    if keeper.condition_manager.get_condition_state(escrow_condition_id) > 1:
        logger.debug(
            f'escrow reward condition already fulfilled/aborted: '
            f'agreementId={agreement_id}, escrow reward conditionId={escrow_condition_id}'
        )
        return

    logger.debug(f"release reward (agreement {agreement_id}) after event {event}.")
    access_id, lock_id = condition_ids[:2]
    logger.debug(f'fulfill_escrow_reward_condition: '
                 f'agreementId={agreement_id}'
                 f'price={price}, {type(price)}'
                 f'consumer={consumer_address},'
                 f'publisher={publisher_account.address},'
                 f'conditionIds={condition_ids}')
    assert price == service_agreement.get_price(), 'price mismatch.'
    assert isinstance(price, int), f'price expected to be int type, got type "{type(price)}"'
    time.sleep(5)
    keeper = Keeper.get_instance()
    did_owner = keeper.agreement_manager.get_agreement_did_owner(agreement_id)
    args = (
        agreement_id,
        price,
        Web3Provider.get_web3().toChecksumAddress(did_owner),
        consumer_address,
        lock_id,
        access_id,
        publisher_account
    )
    process_fulfill_condition(args, keeper.escrow_reward_condition, escrow_condition_id, logger, 10)


def refund_reward(event, agreement_id, did, service_agreement, price, consumer_account,
                  publisher_address, condition_ids, escrow_condition_id):
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
    :param escrow_condition_id: hex str the id of escrow reward condition at this `agreement_id`
    """
    logger.debug(f"trigger refund (agreement {agreement_id}) after event {event}.")
    if Keeper.get_instance().condition_manager.get_condition_state(escrow_condition_id) > 1:
        logger.debug(
            f'escrow reward condition already fulfilled/aborted: '
            f'agreementId={agreement_id}, escrow reward conditionId={escrow_condition_id},'
            f' publisher={publisher_address}'
        )
        return

    access_id, lock_id = condition_ids[:2]
    name_to_parameter = {param.name: param for param in
                         service_agreement.condition_by_name['escrowReward'].parameters}
    document_id = add_0x_prefix(name_to_parameter['_documentId'].value)
    asset_id = add_0x_prefix(did_to_id(did))
    did_owner = Keeper.get_instance().agreement_manager.get_agreement_did_owner(agreement_id)
    assert document_id == asset_id, f'document_id {document_id} <=> asset_id {asset_id} mismatch.'
    assert price == service_agreement.get_price(), 'price mismatch.'
    try:
        escrow_condition = Keeper.get_instance().escrow_reward_condition
        tx_hash = escrow_condition.fulfill(
            agreement_id,
            price,
            Web3Provider.get_web3().toChecksumAddress(did_owner),
            consumer_account.address,
            lock_id,
            access_id,
            consumer_account
        )
        process_tx_receipt(
            tx_hash,
            getattr(escrow_condition.contract.events, escrow_condition.FULFILLED_EVENT)(),
            'EscrowReward.Fulfilled'
        )
    except Exception as e:
        logger.error(f'Error when doing escrow_reward_condition.fulfills (agreementId {agreement_id}): {e}',  exc_info=1)
        raise e


def consume_asset(event, agreement_id, did, service_agreement, consumer_account, consume_callback,
                  secret_store_url, parity_url, downloads_path):
    """
    Consumption of an asset after get the event call.

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param consumer_account: Account instance of the consumer
    :param consume_callback:
    :param secret_store_url: str URL of secret store node for retrieving decryption keys
    :param parity_url: str URL of parity client to use for secret store encrypt/decrypt
    :param downloads_path: str path to save downloaded files
    """
    logger.debug(f"consuming asset (agreementId {agreement_id}) after event {event}.")
    if consume_callback:
        secret_store = SecretStoreProvider.get_secret_store(
            secret_store_url, parity_url, consumer_account
        )
        brizo = BrizoProvider.get_brizo()

        consume_callback(
            agreement_id,
            service_agreement.service_definition_id,
            DIDResolver(Keeper.get_instance().did_registry).resolve(did),
            consumer_account,
            downloads_path,
            brizo,
            secret_store
        )

    #     logger.info('Done consuming asset.')
    #
    # else:
    #     logger.info('Handling consume asset but the consume callback is not set. The user '
    #                 'can trigger consume asset directly using the agreementId and assetId.')


fulfillEscrowRewardCondition = fulfill_escrow_reward_condition
