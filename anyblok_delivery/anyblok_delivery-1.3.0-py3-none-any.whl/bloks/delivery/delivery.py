# This file is a part of the AnyBlok / Delivery project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from logging import getLogger

from anyblok import Declarations
from anyblok.column import (
    UUID,
    String,
    Selection
)
from anyblok.relationship import Many2One
from anyblok.field import Function
from anyblok_postgres.column import Jsonb
import hashlib


logger = getLogger(__name__)
Model = Declarations.Model
Mixin = Declarations.Mixin


@Declarations.register(Declarations.Model)
class Delivery:
    """Namespace for deliveries"""


@Declarations.register(Model.Delivery)
class Carrier(Mixin.UuidColumn, Mixin.TrackModel):
    """ 'Model.Delivery.Carrier' namespace
    """
    name = String(label="Name", nullable=False)
    code = String(label="Code", unique=True, nullable=False)


@Declarations.register(Model.Delivery.Carrier)
class Credential(Mixin.UuidColumn, Mixin.TrackModel):
    """ Store carrier credentials
    Model.Delivery.Carrier.Credential
    """
    account_number = String(label="Account Number")
    password = String(label="Password", encrypt_key=True)


@Declarations.register(Model.Delivery.Carrier)
class Service(Mixin.UuidColumn, Mixin.TrackModel):
    """ Carrier service
    Model.Delivery.Carrier.Service
    """
    CARRIER_CODE = None

    name = String(label="Name", nullable=False)
    product_code = String(label="Product code", unique=True, nullable=False)
    carrier = Many2One(label="Name",
                       model=Declarations.Model.Delivery.Carrier,
                       one2many='services',
                       nullable=False)
    credential = Many2One(label="Credential",
                          model=Declarations.Model.Delivery.Carrier.Credential,
                          one2many='services',
                          nullable=False)
    properties = Jsonb(label="Properties")
    carrier_code = Selection(selections='get_carriers')

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Service, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.Delivery.Carrier.Service':
            mapper_args.update({'polymorphic_on': cls.carrier_code})

        mapper_args.update({'polymorphic_identity': cls.CARRIER_CODE})
        return mapper_args

    @classmethod
    def query(cls, *args, **kwargs):
        query = super(Service, cls).query(*args, **kwargs)
        if cls.__registry_name__.startswith('Model.Delivery.Carrier.Service.'):
            query = query.filter(cls.carrier_code == cls.CARRIER_CODE)

        return query

    @classmethod
    def get_carriers(cls):
        return dict()

    def create_label(self, *args, **kwargs):
        raise Exception("Creating a label directly from Carrier.Service class "
                        "is Forbidden. Please use a specialized one like "
                        "Colissimo, Dhl, etc...")

    def get_label_status(self, *args, **kwargs):
        raise Exception("Update the status of the label directly from "
                        "Carrier.Service class is Forbidden. Please use "
                        "a specialized one like Colissimo, Dhl, etc...")


@Declarations.register(Model.Delivery)
class Shipment(Mixin.UuidColumn, Mixin.TrackModel):
    """ Shipment
    """
    statuses = dict(new="New", label="Label", transit="Transit",
                    delivered="Delivered", exception="Exception",
                    error="Error")
    service = Many2One(label="Shipping service",
                       model=Declarations.Model.Delivery.Carrier.Service,
                       one2many='shipments',
                       nullable=False)
    sender_address = Many2One(label="Sender address",
                              model=Declarations.Model.Address,
                              column_names=["sender_address_uuid"],
                              nullable=False)
    recipient_address = Many2One(label="Recipient address",
                                 model=Declarations.Model.Address,
                                 column_names=["recipient_address_uuid"],
                                 nullable=False)
    reason = String(label="Reason reference")
    pack = String(label="Pack reference")
    status = Selection(label="Shipping status", selections=statuses,
                       default='new',
                       nullable=False)
    properties = Jsonb(label="Properties")
    document_uuid = UUID(label="Carrier slip document reference")
    document = Function(fget='get_latest_document')
    tracking_number = String(label="Carrier tracking number")

    def get_latest_document(self):
        Document = self.registry.Attachment.Document.Latest
        query = Document.query().filter_by(uuid=self.document_uuid)
        return query.one_or_none()

    def create_label(self):
        """Retrieve a shipping label from shipping service
        """
        if not self.status == 'new':
            return

        return self.service.create_label(shipment=self)

    def get_label_status(self):
        """Retrieve a shipping label from shipping service
        """
        if self.status in ('new', 'delivered', 'error'):
            return

        return self.service.get_label_status(shipment=self)

    @classmethod
    def get_labels_status(cls):
        status = ['label', 'transit', 'exception']
        shipments = cls.query().filter(cls.status.in_(status)).all()
        for shipment in shipments:
            shipment.get_label_status()

    def save_document(self, binary_file, content_type):
        document = self.document
        if document is None:
            document = self.registry.Attachment.Document.insert(
                data={'shipment': str(self.uuid)}
            )
            self.document_uuid = document.uuid

        document.set_file(binary_file)
        document.filesize = len(binary_file)
        document.contenttype = content_type
        hash = hashlib.sha256()
        hash.update(binary_file)
        document.hash = hash.digest()

        self.registry.flush()  # flush to update version in document
