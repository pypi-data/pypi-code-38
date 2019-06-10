#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_quartet_masterdata
------------

Tests for `quartet_masterdata` models module.
"""

from django.test import TestCase
from django.db.models import Q
from quartet_masterdata import models


class TestQuartet_Masterdata(TestCase):
    '''
    Create and validate master material (trade items) and locations.
    '''

    def setUp(self):
        from tests import factories
        location_type = factories.LocationTypeFactory.create()
        location = factories.LocationFactory.create()
        location2 = factories.LocationFactory.create(
            GLN13="2345234523454",
            SGLN="urn:epc:id:sgln:23452.3452345.0",
            name='test', latitude=12.232,
            longitude=33.2343)
        location_field = factories.LocationFieldFactory.create(
            location=location)
        location_identifier = factories.LocationIdentifierFactory.create(
            location=location
        )
        trade_item = factories.TradeItemFactory.create()
        trade_item_field = factories.TradeItemFieldFactory.create(
            trade_item=trade_item
        )

    def test_create_plant(self):
        location = models.Location.objects.select_related(
            'location_type',
        ).prefetch_related(
            'locationfield_set',
            'locationidentifier_set'
        ).get(SGLN='urn:epc:id:sgln:305555.123456.0')

    def test_create_trade_item(self):
        ti = models.TradeItem.objects.prefetch_related(
            'tradeitemfield_set'
        ).get(
            Q(GTIN14='12341234123411') &
            Q(NDC='1234-1234-12') &
            Q(additional_id='45039-33') &
            Q(tradeitemfield__name='MATNO') &
            Q(tradeitemfield__value='32423-33-333')
        )
        self.assertEqual(ti.country_of_origin, 'US')
        self.assertEqual(ti.gross_weight, 10.5)
        self.assertEqual(ti.net_weight, 10)
        self.assertEqual(ti.manufacturer_name, 'Acme Corp.')
        self.assertEqual(ti.additional_id_typecode, 'GST')
        self.assertEqual(ti.description_short, 'Supressitol')
        self.assertEqual(ti.dosage_form_type, 'PILL')
        self.assertEqual(ti.functional_name, 'Widget')
        self.assertEqual(ti.manufacturer_name, 'Acme Corp.')
        self.assertEqual(ti.net_content_description, '600 grams')
        self.assertEqual(ti.label_description, 'Supressitol Tablets: 10 grams '
                                               'of suppression.')
        self.assertEqual(ti.regulated_product_name, 'Supressitoxide Carbonite')
        self.assertEqual(ti.strength_description, '100mg')
        self.assertEqual(ti.trade_item_description, 'Supressitol Brand '
                                                    'Suppression Tablets')
