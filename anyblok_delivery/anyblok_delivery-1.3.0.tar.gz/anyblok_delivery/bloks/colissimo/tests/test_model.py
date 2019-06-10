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
from datetime import datetime, timedelta
from unittest.mock import patch


@pytest.mark.usefixtures('rollback_registry')
class TestDeliveryModel:
    """ Test delivery model"""

    @pytest.fixture(autouse=True)
    def init_registry(self, rollback_registry):
        self.registry = rollback_registry

    def create_carrier_service_colissimo(self):
        ca = self.registry.Delivery.Carrier.insert(
            name="Colissimo", code="COLISSIMO")
        ca_cred = self.registry.Delivery.Carrier.Credential.insert(
                    account_number="123",
                    password="password")

        service = self.registry.Delivery.Carrier.Service.Colissimo.insert(
                    name="Livraison à domicile", product_code="DOM",
                    carrier=ca, credential=ca_cred)
        return service

    def create_sender_address(self):
        address = self.registry.Address.insert(
                first_name="Shipping",
                last_name="services",
                company_name="Acme",
                street1="1 company street",
                zip_code="75000", state="", city="Paris", country="FRA")
        return address

    def create_recipient_address(self):
        address = self.registry.Address.insert(
                first_name="Jon",
                last_name="Doe",
                street1="1 street",
                street2="crossroad",
                street3="♥",
                zip_code="66000",
                state="A region",
                city="Perpignan",
                country="FRA"
            )
        return address

    def test_carrier_service_colissimo(self):
        colissimo = self.create_carrier_service_colissimo()
        assert colissimo.carrier.code == "COLISSIMO"
        assert len(self.registry.Delivery.Carrier.Service.query().all()) == 1
        Delivery = self.registry.Delivery
        assert Delivery.Carrier.Service.Colissimo.query().count() == 1

    def test_map_data(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX"
                )
        data = shipment.service.map_data(shipment=shipment)
        assert type(data) is dict
        assert data['letter']['service']['productCode'] == "DOM"
        assert data['letter']['sender']['address']['countryCode'] == "FR"

    def test_create_label_200(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX"
                )

        with patch('anyblok_delivery.bloks.colissimo.colissimo.Colissimo'
                   '.create_label_query') as mock_post:
            status_code = 200
            pdf = urandom(100)
            infos = {'labelResponse': {'parcelNumber': '6A track number'}}
            mock_post.return_value = (status_code, pdf, infos)
            response = shipment.create_label()

            assert response['status_code'] == 200
            assert shipment.status == 'label'
            assert shipment.document.get_file()['file'] == pdf

    def test_create_label_400(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX"
                )

        with patch('anyblok_delivery.bloks.colissimo.colissimo.Colissimo'
                   '.create_label_query') as mock_post:
            status_code = 400
            pdf = urandom(0)
            infos = {'messages': dict()}
            mock_post.return_value = (status_code, pdf, infos)
            with pytest.raises(Exception):
                shipment.create_label()

    def test_create_label_500(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX"
                )

        with patch('anyblok_delivery.bloks.colissimo.colissimo.Colissimo'
                   '.create_label_query') as mock_post:
            status_code = 500
            pdf = urandom(0)
            infos = {'messages': dict()}
            mock_post.return_value = (status_code, pdf, infos)
            with pytest.raises(Exception):
                shipment.create_label()

    def test_get_label_status_error_code_0(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX", status='label'
                )

        with patch('anyblok_delivery.bloks.colissimo.colissimo.Colissimo'
                   '.get_label_status_query') as mock_post:
            mock_post.return_value = {
                'errorCode': '0', 'eventDate': datetime.now().isoformat(),
                'eventCode': 'DEPGUI', 'eventLibelle': 'Test'}
            shipment.get_label_status()
            assert shipment.status == 'delivered'

    def test_get_label_status_more_than_90_days(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX", status='label',
                create_date=datetime.utcnow() - timedelta(days=91))

        with patch('anyblok_delivery.bloks.colissimo.colissimo.Colissimo'
                   '.get_label_status_query') as mock_post:
            mock_post.return_value = {
                'errorCode': '0', 'eventDate': datetime.now().isoformat(),
                'eventCode': 'DEPGUI', 'eventLibelle': 'Test'}
            shipment.get_label_status()
            assert shipment.status == 'error'
