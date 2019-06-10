# This file is a part of the AnyBlok / Delivery project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from os import urandom
from uuid import uuid1


@pytest.mark.usefixtures('rollback_registry')
class TestDeliveryModel:
    """ Test delivery model"""

    @pytest.fixture(autouse=True)
    def init_registry(self, rollback_registry):
        self.registry = rollback_registry

    def create_sender_address(self):
        address = self.registry.Address.insert(
                first_name="Shipping",
                last_name="services",
                company_name="Acme",
                street1="1 company street",
                zip_code="00000", state="", city="There", country="FRA")
        return address

    def create_recipient_address(self):
        address = self.registry.Address.insert(
                first_name="Jon",
                last_name="Doe",
                street1="1 street",
                street2="crossroad",
                street3="♥",
                zip_code="99999",
                state="A region",
                city="Nowhere",
                country="FRA"
            )
        return address

    def test_credentials(self):
        cred = self.registry.Delivery.Carrier.Credential.insert(
                account_number="test", password="xxx")
        assert cred.account_number == 'test'
        assert cred.password == 'xxx'

    def test_addresses(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()

        assert sender_address != recipient_address
        assert self.registry.Address.query().count() == 2
        query = self.registry.Address.query()
        assert query.filter_by(country="FRA").count() == 2
        assert query.filter_by(country="USA").count() == 0

    def create_carrier_service(self):
        ca = self.registry.Delivery.Carrier.insert(
            name="SomeOne", code="SOMEONE")

        ca_cred = self.registry.Delivery.Carrier.Credential.insert(
                    account_number="123",
                    password="password")
        service = self.registry.Delivery.Carrier.Service.insert(
                    name="Livraison à domicile", product_code="DOM",
                    carrier=ca, credential=ca_cred)
        return service

    def test_save_document_new(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        service = self.create_carrier_service()
        shipment = self.registry.Delivery.Shipment.insert(
                service=service, sender_address=sender_address,
                recipient_address=recipient_address)
        assert not shipment.document
        binary_file = urandom(100)
        content_type = 'application/pdf'
        shipment.save_document(binary_file, content_type)
        assert shipment.document
        assert shipment.document.file == binary_file
        assert shipment.document.contenttype == content_type
        assert shipment.document.filesize == len(binary_file)
        assert shipment.document.hash

    def test_save_document_already_exist(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        service = self.create_carrier_service()
        document = self.registry.Attachment.Document.Latest.insert(
            file=urandom(100)
        )
        shipment = self.registry.Delivery.Shipment.insert(
            service=service, sender_address=sender_address,
            recipient_address=recipient_address,
            document_uuid=document.uuid
        )
        assert shipment.document
        old_version = document.version
        binary_file = urandom(100)
        content_type = 'application/pdf'
        shipment.save_document(binary_file, content_type)
        assert shipment.document.version != old_version
        assert shipment.document
        assert shipment.document.file == binary_file
        assert shipment.document.contenttype == content_type
        assert shipment.document.filesize == len(binary_file)
        assert shipment.document.hash

    def test_save_document_unexisting_document(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        service = self.create_carrier_service()
        shipment = self.registry.Delivery.Shipment.insert(
            service=service, sender_address=sender_address,
            recipient_address=recipient_address,
            document_uuid=uuid1()
        )
        assert shipment.document_uuid
        assert not shipment.document
        binary_file = urandom(100)
        content_type = 'application/pdf'
        shipment.save_document(binary_file, content_type)
        assert shipment.document
        assert shipment.document.file == binary_file
        assert shipment.document.contenttype == content_type
        assert shipment.document.filesize == len(binary_file)
        assert shipment.document.hash

    def test_service_create_label(self):
        service = self.create_carrier_service()
        with pytest.raises(Exception):
            service.create_label()

    def test_service_get_labels_status(self):
        service = self.create_carrier_service()
        with pytest.raises(Exception):
            service.get_label_status()

    def test_shipment_create_label(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        service = self.create_carrier_service()
        shipment = self.registry.Delivery.Shipment.insert(
                service=service, sender_address=sender_address,
                recipient_address=recipient_address)
        shipment.status = 'label'
        assert shipment.create_label() is None

    def test_shipment_get_label_status(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        service = self.create_carrier_service()
        shipment = self.registry.Delivery.Shipment.insert(
                service=service, sender_address=sender_address,
                recipient_address=recipient_address)
        assert shipment.get_label_status() is None

    def test_shipment_get_labels_status(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        service = self.create_carrier_service()
        self.registry.Delivery.Shipment.insert(
                service=service, sender_address=sender_address,
                recipient_address=recipient_address)
        assert self.registry.Delivery.Shipment.get_labels_status() is None
