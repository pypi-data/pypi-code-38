"""Ocean module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from squid_py.agreements.register_service_agreement import (register_service_agreement_consumer,
                                                            register_service_agreement_publisher)
from squid_py.agreements.service_agreement import ServiceAgreement
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.did import did_to_id
from squid_py.exceptions import (OceanInvalidAgreementTemplate,
                                 OceanInvalidServiceAgreementSignature, OceanServiceAgreementExists)
from squid_py.keeper.web3_provider import Web3Provider
from squid_py.keeper.events_manager import EventsManager
from squid_py.ocean.ocean_conditions import OceanConditions
from squid_py.utils.utilities import prepare_prefixed_hash

logger = logging.getLogger('ocean')


class OceanAgreements:
    """Ocean agreements class."""

    def __init__(self, keeper, asset_resolver, asset_consumer, config):
        self._keeper = keeper
        self._asset_resolver = asset_resolver
        self._asset_consumer = asset_consumer
        self._config = config
        self.conditions = OceanConditions(self._keeper)

    def get(self, agreement_id):
        """
        Retrieve the agreement data of agreement_id.

        :param agreement_id: id of the agreement, hex str
        :return: AgreementValues instance -- a namedtuple with the following attributes:

            did,
            owner,
            template_id,
            condition_ids,
            updated_by,
            block_number_updated

        """
        return self._keeper.agreement_manager.get_agreement(agreement_id)

    @staticmethod
    def new():
        return ServiceAgreement.create_new_agreement_id()

    def sign(self, agreement_id, did, service_definition_id, consumer_account):
        asset = self._asset_resolver.resolve(did)
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, asset)

        publisher_address = self._keeper.did_registry.get_did_owner(asset.asset_id)
        agreement_hash = service_agreement.get_service_agreement_hash(
            agreement_id, asset.asset_id, consumer_account.address, publisher_address, self._keeper
        )
        return self._keeper.sign_hash(agreement_hash, consumer_account)

    def prepare(self, did, service_definition_id, consumer_account):
        """

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_definition_id: identifier of the service inside the asset DDO, str
         the ddo to use in this agreement.
        :param consumer_account: Account instance of the consumer
        :return: tuple (agreement_id: str, signature: hex str)
        """
        agreement_id = self.new()
        signature = self.sign(agreement_id, did, service_definition_id, consumer_account)
        return agreement_id, signature

    def send(self, did, agreement_id, service_definition_id, signature,
             consumer_account, auto_consume=False):
        """
        Send a signed service agreement to the publisher Brizo instance to
        consume/access the service.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_definition_id: str identifies the specific service in
         the ddo to use in this agreement.
        :param signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_account: Account instance of the consumer
        :param auto_consume: boolean tells this function wether to automatically trigger
            consuming the asset upon receiving access permission
        :raises OceanInitializeServiceAgreementError: on failure
        :return: bool
        """
        asset = self._asset_resolver.resolve(did)
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, asset)
        # subscribe to events related to this agreement_id before sending the request.
        logger.debug(f'Registering service agreement with id: {agreement_id}')
        publisher_address = self._keeper.did_registry.get_did_owner(asset.asset_id)
        condition_ids = service_agreement.generate_agreement_condition_ids(
            agreement_id, asset.asset_id, consumer_account.address, publisher_address, self._keeper)

        register_service_agreement_consumer(
            self._config.storage_path,
            publisher_address,
            agreement_id,
            did,
            service_agreement,
            service_definition_id,
            service_agreement.get_price(),
            asset.encrypted_files,
            consumer_account,
            condition_ids,
            self._asset_consumer.download if auto_consume else None,
        )

        return BrizoProvider.get_brizo().initialize_service_agreement(
            did,
            agreement_id,
            service_definition_id,
            signature,
            consumer_account.address,
            service_agreement.endpoints.purchase
        )

    def create(self, did, service_definition_id, agreement_id,
               service_agreement_signature, consumer_address,
               account, auto_consume=False):
        """
        Execute the service agreement on-chain using keeper's ServiceAgreement contract.

        The on-chain executeAgreement method requires the following arguments:
        templateId, signature, consumer, hashes, timeouts, serviceAgreementId, did.
        `agreement_message_hash` is necessary to verify the signature.
        The consumer `signature` includes the conditions timeouts and parameters values which
        is usedon-chain to verify that the values actually match the signed hashes.

        :param did: str representation fo the asset DID. Use this to retrieve the asset DDO.
        :param service_definition_id: str identifies the specific service in
         the ddo to use in this agreement.
        :param agreement_id: 32 bytes identifier created by the consumer and will be used
         on-chain for the executed agreement.
        :param service_agreement_signature: str the signed agreement message hash which includes
         conditions and their parameters values and other details of the agreement.
        :param consumer_address: ethereum account address of consumer, hex str
        :param account: Account instance creating the agreement. Can be either the
            consumer, publisher or provider
        :param auto_consume: bool
        :return: dict the `executeAgreement` transaction receipt
        """
        assert consumer_address and Web3Provider.get_web3().isChecksumAddress(
            consumer_address), f'Invalid consumer address {consumer_address}'
        assert account.address in self._keeper.accounts, \
            f'Unrecognized account address {account.address}'

        agreement_template_approved = self._keeper.template_manager.is_template_approved(
            self._keeper.escrow_access_secretstore_template.address)
        if not agreement_template_approved:
            msg = (f'The EscrowAccessSecretStoreTemplate contract at address '
                   f'{self._keeper.escrow_access_secretstore_template.address} is not '
                   f'approved and cannot be used for creating service agreements.')
            logger.warning(msg)
            raise OceanInvalidAgreementTemplate(msg)

        asset = self._asset_resolver.resolve(did)
        asset_id = asset.asset_id
        service_agreement = ServiceAgreement.from_ddo(service_definition_id, asset)
        agreement_template = self._keeper.escrow_access_secretstore_template

        if agreement_template.get_agreement_consumer(agreement_id) is not None:
            raise OceanServiceAgreementExists(
                f'Service agreement {agreement_id} already exists, cannot reuse '
                f'the same agreement id.')

        if consumer_address != account.address:
            if not self._verify_service_agreement_signature(
                    did, agreement_id, service_definition_id,
                    consumer_address, service_agreement_signature,
                    ddo=asset
            ):
                raise OceanInvalidServiceAgreementSignature(
                    f'Verifying consumer signature failed: '
                    f'signature {service_agreement_signature}, '
                    f'consumerAddress {consumer_address}'
                )

        publisher_address = Web3Provider.get_web3().toChecksumAddress(asset.publisher)
        condition_ids = service_agreement.generate_agreement_condition_ids(
            agreement_id, asset_id, consumer_address, publisher_address, self._keeper)

        time_locks = service_agreement.conditions_timelocks
        time_outs = service_agreement.conditions_timeouts
        success = agreement_template.create_agreement(
            agreement_id,
            asset_id,
            condition_ids,
            time_locks,
            time_outs,
            consumer_address,
            account
        )

        if not success:
            # success is based on tx receipt which is not reliable.
            # So we check on-chain directly to see if agreement_id is there
            consumer = self._keeper.escrow_access_secretstore_template.get_agreement_consumer(agreement_id)
            if consumer:
                success = True
            else:
                event_log = self._keeper.escrow_access_secretstore_template.subscribe_agreement_created(
                    agreement_id, 30, None, (), wait=True
                )
                success = event_log is not None

        if success:
            logger.info(f'Service agreement {agreement_id} created successfully.')
        else:
            logger.info(f'Create agreement "{agreement_id}" failed.')
            self._log_agreement_info(
                asset, service_agreement, agreement_id, service_agreement_signature,
                consumer_address, account, condition_ids
            )

        if success:
            # subscribe to events related to this agreement_id
            if consumer_address == account.address:
                register_service_agreement_consumer(
                    self._config.storage_path,
                    publisher_address,
                    agreement_id,
                    did,
                    service_agreement,
                    service_definition_id,
                    service_agreement.get_price(),
                    asset.encrypted_files,
                    account,
                    condition_ids,
                    self._asset_consumer.download if auto_consume else None
                )

            else:
                register_service_agreement_publisher(
                    self._config.storage_path,
                    consumer_address,
                    agreement_id,
                    did,
                    service_agreement,
                    service_definition_id,
                    service_agreement.get_price(),
                    account,
                    condition_ids
                )

        return success

    def _log_agreement_info(self, asset, service_agreement, agreement_id, agreement_signature,
                            consumer_address, publisher_account, condition_ids):
        agreement_hash = service_agreement.get_service_agreement_hash(
            agreement_id, asset.asset_id, consumer_address, publisher_account.address, self._keeper)
        publisher_ether_balance = self._keeper.get_ether_balance(publisher_account.address)
        logger.debug(
            f'Agreement parameters:'
            f'\n  agreement id: {agreement_id}'
            f'\n  consumer address: {consumer_address}'
            f'\n  publisher address: {publisher_account.address}'
            f'\n  conditions ids: {condition_ids}'
            f'\n  asset did: {asset.did}'
            f'\n  agreement signature: {agreement_signature}'
            f'\n  agreement hash: {agreement_hash}'
            f'\n  EscrowAccessSecretStoreTemplate: '
            f'{self._keeper.escrow_access_secretstore_template.address}'
            f'\n  publisher ether balance: {publisher_ether_balance}'
        )

    def is_access_granted(self, agreement_id, did, consumer_address):
        """
        Check permission for the agreement.

        Verify on-chain that the `consumer_address` has permission to access the given asset `did`
        according to the `agreement_id`.

        :param agreement_id: id of the agreement, hex str
        :param did: DID, str
        :param consumer_address: ethereum account address of consumer, hex str
        :return: bool True if user has permission
        """
        agreement_consumer = self._keeper.escrow_access_secretstore_template.get_agreement_consumer(
            agreement_id)

        if agreement_consumer is None:
            return False

        if agreement_consumer != consumer_address:
            logger.warning(f'Invalid consumer address {consumer_address} and/or '
                           f'service agreement id {agreement_id} (did {did})'
                           f', agreement consumer is {agreement_consumer}')
            return False

        document_id = did_to_id(did)
        return self._keeper.access_secret_store_condition.check_permissions(
            document_id, consumer_address
        )

    def _verify_service_agreement_signature(self, did, agreement_id, service_definition_id,
                                            consumer_address, signature, ddo=None):
        """
        Verify service agreement signature.

        Verify that the given signature is truly signed by the `consumer_address`
        and represents this did's service agreement..

        :param did: DID, str
        :param agreement_id: id of the agreement, hex str
        :param service_definition_id: identifier of the service inside the asset DDO, str
        :param consumer_address: ethereum account address of consumer, hex str
        :param signature: Signature, str
        :param ddo: DDO instance
        :return: True if signature is legitimate, False otherwise
        :raises: ValueError if service is not found in the ddo
        :raises: AssertionError if conditions keys do not match the on-chain conditions keys
        """
        if not ddo:
            ddo = self._asset_resolver.resolve(did)

        service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
        agreement_hash = service_agreement.get_service_agreement_hash(
            agreement_id, ddo.asset_id, consumer_address,
            Web3Provider.get_web3().toChecksumAddress(ddo.proof['creator']), self._keeper)

        prefixed_hash = prepare_prefixed_hash(agreement_hash)
        recovered_address = Web3Provider.get_web3().eth.account.recoverHash(
            prefixed_hash, signature=signature
        )
        is_valid = (recovered_address == consumer_address)
        if not is_valid:
            logger.warning(f'Agreement signature failed: agreement hash is {agreement_hash.hex()}')

        return is_valid

    def _approve_token_transfer(self, amount, consumer_account):
        if self._keeper.token.get_token_balance(consumer_account.address) < amount:
            raise ValueError(
                f'Account {consumer_account.address} does not have sufficient tokens '
                f'to approve for transfer.')

        self._keeper.token.token_approve(self._keeper.payment_conditions.address, amount,
                                         consumer_account)

    def status(self, agreement_id):
        """
        Get the status of a service agreement.

        :param agreement_id: id of the agreement, hex str
        :return: dict with condition status of each of the agreement's conditions or None if the
        agreement is invalid.
        """
        condition_ids = self._keeper.agreement_manager.get_agreement(agreement_id).condition_ids
        result = {"agreementId": agreement_id}
        conditions = dict()
        for i in condition_ids:
            conditions[self._keeper.get_condition_name_by_address(
                self._keeper.condition_manager.get_condition(
                    i).type_ref)] = self._keeper.condition_manager.get_condition_state(i)
        result["conditions"] = conditions
        return result

    def subscribe_events(self, provider_address, callback):
        events_manager = EventsManager.get_instance(self._keeper)
        events_manager.agreement_listener.add_event_filter(
            '_accessProvider',
            provider_address,
            callback,
            None,
            (),
            None,
            pin_event=True
        )
