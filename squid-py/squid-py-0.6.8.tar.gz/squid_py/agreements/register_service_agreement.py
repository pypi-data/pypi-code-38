
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime

from squid_py.agreements.events import (access_secret_store_condition, escrow_reward_condition,
                                        lock_reward_condition, verify_reward_condition)
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.keeper import Keeper
from squid_py.keeper.events_manager import EventsManager
from squid_py.data_store.agreements import AgreementsStorage

logger = logging.getLogger(__name__)

EVENT_WAIT_TIMEOUT = 60


def register_service_agreement_consumer(storage_path, publisher_address, agreement_id, did,
                                        service_agreement, service_definition_id, price,
                                        encrypted_files, consumer_account, condition_ids,
                                        consume_callback=None, start_time=None):
    """
    Registers the given service agreement in the local storage.
    Subscribes to the service agreement events.

    :param storage_path: storage path for the internal db, str
    :param publisher_address: ethereum account address of publisher, hex str
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param service_definition_id: identifier of the service inside the asset DDO, str
    :param price: Asset price, int
    :param encrypted_files: resutl of the files encrypted by the secret store, hex str
    :param consumer_account: Account instance of the consumer
    :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
    :param consume_callback:
    :param start_time: start time, int
    """
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    AgreementsStorage(storage_path).record_service_agreement(
        agreement_id, did, service_definition_id, price, encrypted_files, start_time
    )

    process_agreement_events_consumer(
        publisher_address, agreement_id, did, service_agreement,
        price, consumer_account, condition_ids,
        consume_callback
    )


def process_agreement_events_consumer(publisher_address, agreement_id, did, service_agreement,
                                      price, consumer_account, condition_ids,
                                      consume_callback):
    """
    Process the agreement events during the register of the service agreement for the consumer side.

    :param publisher_address: ethereum account address of publisher, hex str
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param price: Asset price, int
    :param consumer_account: Account instance of the consumer
    :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
    :param consume_callback:
    :return:
    """
    conditions_dict = service_agreement.condition_by_name
    events_manager = EventsManager.get_instance(Keeper.get_instance())
    events_manager.watch_agreement_created_event(
        agreement_id,
        lock_reward_condition.fulfillLockRewardCondition,
        None,
        (agreement_id, price, consumer_account),
        EVENT_WAIT_TIMEOUT,
    )

    if consume_callback:
        def _refund_callback(_price, _publisher_address, _condition_ids):
            def do_refund(_event, _agreement_id, _did, _service_agreement, _consumer_account, *_):
                escrow_reward_condition.refund_reward(
                    _event, _agreement_id, _did, _service_agreement, _price,
                    _consumer_account, _publisher_address, _condition_ids
                )

            return do_refund

        events_manager.watch_access_event(
            agreement_id,
            escrow_reward_condition.consume_asset,
            _refund_callback(price, publisher_address, condition_ids),
            (agreement_id, did, service_agreement, consumer_account, consume_callback),
            conditions_dict['accessSecretStore'].timeout
        )


def register_service_agreement_publisher(storage_path, consumer_address, agreement_id, did,
                                         service_agreement, service_definition_id, price,
                                         publisher_account, condition_ids, start_time=None):
    """
    Registers the given service agreement in the local storage.
    Subscribes to the service agreement events.

    :param storage_path:storage path for the internal db, str
    :param consumer_address: ethereum account address of consumer, hex str
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param service_definition_id: identifier of the service inside the asset DDO, str
    :param price: Asset price, int
    :param publisher_account: Account instance of the publisher
    :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
    :param start_time:
    :return:
    """
    if start_time is None:
        start_time = int(datetime.now().timestamp())

    AgreementsStorage(storage_path).record_service_agreement(
        agreement_id, did, service_definition_id, price, '', start_time
    )

    process_agreement_events_publisher(
        publisher_account, agreement_id, did, service_agreement,
        price, consumer_address, condition_ids
    )


def process_agreement_events_publisher(publisher_account, agreement_id, did, service_agreement,
                                       price, consumer_address, condition_ids):
    """
    Process the agreement events during the register of the service agreement for the publisher side

    :param publisher_account: Account instance of the publisher
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param price: Asset price, int
    :param consumer_address: ethereum account address of consumer, hex str
    :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
    :return:
    """
    conditions_dict = service_agreement.condition_by_name
    events_manager = EventsManager.get_instance(Keeper.get_instance())
    events_manager.watch_lock_reward_event(
        agreement_id,
        access_secret_store_condition.fulfillAccessSecretStoreCondition,
        None,
        (agreement_id, did, service_agreement,
         consumer_address, publisher_account),
        conditions_dict['lockReward'].timeout
    )

    events_manager.watch_access_event(
        agreement_id,
        escrow_reward_condition.fulfillEscrowRewardCondition,
        None,
        (agreement_id, service_agreement,
         price, consumer_address, publisher_account, condition_ids),
        conditions_dict['accessSecretStore'].timeout
    )

    events_manager.watch_reward_event(
        agreement_id,
        verify_reward_condition.verifyRewardTokens,
        None,
        (agreement_id, did, service_agreement,
         price, consumer_address, publisher_account),
        conditions_dict['escrowReward'].timeout
    )


def execute_pending_service_agreements(storage_path, account, actor_type, did_resolver_fn):
    """
     Iterates over pending service agreements recorded in the local storage,
    fetches their service definitions, and subscribes to service agreement events.

    :param storage_path: storage path for the internal db, str
    :param account:
    :param actor_type:
    :param did_resolver_fn:
    :return:
    """
    keeper = Keeper.get_instance()
    # service_agreement_id, did, service_definition_id, price, files, start_time, status
    for (agreement_id, did, _, price, _, _, _
         ) in AgreementsStorage(storage_path).get_service_agreements(storage_path):

        ddo = did_resolver_fn(did)
        for service in ddo.services:
            if service.type != 'Access':
                continue

            consumer_provider_tuple = keeper.escrow_access_secretstore_template.get_agreement_data(
                agreement_id)
            if not consumer_provider_tuple:
                continue

            consumer, provider = consumer_provider_tuple
            did = ddo.did
            service_agreement = ServiceAgreement.from_service_dict(service.as_dictionary())
            condition_ids = service_agreement.generate_agreement_condition_ids(
                agreement_id, did, consumer, provider, keeper)

            if actor_type == 'consumer':
                assert account.address == consumer
                process_agreement_events_consumer(
                    provider, agreement_id, did, service_agreement,
                    price, account, condition_ids, None)
            else:
                assert account.address == provider
                process_agreement_events_publisher(
                    account, agreement_id, did, service_agreement,
                    price, consumer, condition_ids)
