# This file is a part of the AnyBlok / Delivery project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import json
import pytz
from datetime import datetime, timedelta
from logging import getLogger

import requests
from requests_toolbelt.multipart import decoder
from anyblok import Declarations
from lxml import etree
from .eventcodes import eventCodes


logger = getLogger(__name__)
NEW_LABEL_URL = "https://ws.colissimo.fr/sls-ws/SlsServiceWSRest/generateLabel"
UPDATE_LABEL_URL = (
    "https://www.coliposte.fr/tracking-chargeur-cxf/TrackingServiceWS/track")
Model = Declarations.Model


@Declarations.register(Model.Delivery.Carrier)
class Service:

    @classmethod
    def get_carriers(cls):
        res = super(Service, cls).get_carriers()
        res.update(dict(COLISSIMO='Colissimo'))
        return res


@Declarations.register(
    Model.Delivery.Carrier.Service,
    tablename=Model.Delivery.Carrier.Service)
class Colissimo(Model.Delivery.Carrier.Service):
    """ The Colissimo Carrier service (Polymorphic model that's override
    Model.Delivery.Carrier.service)

    Namespace : Model.Delivery.Carrier.Service.Colissimo
    """
    CARRIER_CODE = "COLISSIMO"

    def map_data(self, shipment=None):
        """Given a shipment object, transform its data to Colissimo
        specifications"""
        if not shipment:
            raise Exception("You must pass a shipment object to map_data")

        sh = shipment
        # datetime formatting
        deposit_date = datetime.now().strftime("%Y-%m-%d")

        data = {
            "contractNumber": "%s" % self.credential.account_number,
            "password": "%s" % self.credential.password,
            "outputFormat": {
                "x": "0",
                "y": "0",
                "outputPrintingType": "PDF_A4_300dpi"
                },
            "letter": {
                "service": {
                    "productCode": "%s" % self.product_code,
                    "depositDate": "%s" % deposit_date,
                    "orderNumber": "%s %s" % (sh.reason, sh.pack),
                },
                "parcel": {
                    "weight": "%s" % 0.3
                },
                "sender": {
                    "address": sh.sender_address.get_colissimo(),
                },
                "addressee": {
                    "address": sh.recipient_address.get_colissimo(),
                }
            }
        }
        return data

    def create_label_query(self, data):
        req = requests.post(NEW_LABEL_URL, json=data)
        # Parse multipart response
        multipart_data = decoder.MultipartDecoder.from_response(req)
        pdf = b''
        infos = dict()

        for part in multipart_data.parts:
            head = dict((item[0].decode(), item[1].decode()) for
                        item in part.headers.lower_items())
            if ("content-type" in head.keys() and
                head.get('content-type', None) ==
                    "application/octet-stream"):
                pdf = part.content
            elif ("content-type" in head.keys() and
                  head.get('content-type', None).startswith(
                      "application/json")):
                infos = json.loads(part.content.decode())

        return (req.status_code, pdf, infos)

    def create_label(self, shipment=None):
        data = self.map_data(shipment)
        res = dict()
        status_code, pdf, infos = self.create_label_query(data)

        if status_code in (400, 500):
            raise Exception(infos['messages'])
        elif status_code == 200:
            del data['contractNumber']
            del data['password']
            res['infos'] = infos
            res['pdf'] = pdf
            shipment.save_document(
                pdf,
                'application/pdf'
            )
            if not shipment.properties:
                shipment.properties = {
                    'sent': data,
                    'received': infos,
                }
            else:
                shipment.properties.update({
                    'sent': data,
                    'received': infos,
                })
            shipment.status = "label"
            shipment.tracking_number = infos['labelResponse']['parcelNumber']

        res['status_code'] = status_code
        return res

    def get_label_status_query(self, data):
        req = requests.get(UPDATE_LABEL_URL, data)
        response = etree.fromstring(req.text)[0][0][0]  # ugly but only way
        return {x.tag: x.text for x in response}

    def get_label_status(self, shipment=None):
        logger.info('Get label status for %r', shipment)

        properties = shipment.properties.copy() if shipment.properties else {}
        if 'events' not in properties:
            properties['events'] = {}
        else:
            properties['events'] = properties['events'].copy()

        if not shipment.create_date.tzinfo:
            shipment.refresh('create_date')

        now = pytz.UTC.localize(datetime.utcnow())
        if now - shipment.create_date > timedelta(days=90):
            res = {
                'errorCode': '0',
                'eventCode': 'TIMEOUT',
                'eventDate': now.isoformat(),
                'eventLibelle': 'Colis datant de plus de 90 jours'
            }
        else:

            data = {"accountNumber": "%s" % self.credential.account_number,
                    "password": "%s" % self.credential.password,
                    "skybillNumber": shipment.tracking_number}
            res = self.get_label_status_query(data)

        if res['errorCode'] != '0':
            raise Exception(res['errorMessage'])

        if res['eventDate'] in properties['events']:
            return

        try:
            status = eventCodes[res['eventCode']]
            shipment.status = status
            properties['events'][res['eventDate']] = {
                'eventDate': res['eventDate'],
                'eventStatus': status,
                'eventLibelle': res['eventLibelle'],
            }
            shipment.properties = properties
            self.registry.flush()
            logger.info('%r status : %r', shipment, status)
        except KeyError:
            logger.exception("%r" % res)
            raise
