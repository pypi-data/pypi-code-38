# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for maintaining vendor catalogs
"""

from __future__ import unicode_literals, absolute_import

import logging

import six

from rattail.db import model, api
from rattail.vendors.catalogs import iter_catalog_parsers

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views.batch import FileBatchMasterView


log = logging.getLogger(__name__)


class VendorCatalogsView(FileBatchMasterView):
    """
    Master view for vendor catalog batches.
    """
    model_class = model.VendorCatalog
    model_row_class = model.VendorCatalogRow
    default_handler_spec = 'rattail.batch.vendorcatalog:VendorCatalogHandler'
    url_prefix = '/vendors/catalogs'
    template_prefix = '/batch/vendorcatalog'
    editable = False
    rows_bulk_deletable = True

    grid_columns = [
        'id',
        'created',
        'created_by',
        'vendor',
        'effective',
        'filename',
        'rowcount',
        'executed',
    ]

    form_fields = [
        'id',
        'vendor',
        'filename',
        'future',
        'effective',
        'created',
        'created_by',
        'rowcount',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'vendor_code',
        'old_unit_cost',
        'unit_cost',
        'unit_cost_diff',
        'starts',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'item_entry',
        'product',
        'upc',
        'brand_name',
        'description',
        'size',
        'old_vendor_code',
        'vendor_code',
        'old_case_size',
        'case_size',
        'old_case_cost',
        'case_cost',
        'case_cost_diff',
        'old_unit_cost',
        'unit_cost',
        'unit_cost_diff',
        'suggested_retail',
        'starts',
        'ends',
        'discount_starts',
        'discount_ends',
        'discount_amount',
        'discount_percent',
        'status_code',
        'status_text',
    ]

    def get_parsers(self):
        if not hasattr(self, 'parsers'):
            self.parsers = sorted(iter_catalog_parsers(), key=lambda p: p.display)
        return self.parsers

    def configure_grid(self, g):
        super(VendorCatalogsView, self).configure_grid(g)
        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

    def get_instance_title(self, batch):
        return six.text_type(batch.vendor)

    def configure_form(self, f):
        super(VendorCatalogsView, self).configure_form(f)

        # vendor
        f.set_renderer('vendor', self.render_vendor)
        if self.creating:
            f.replace('vendor', 'vendor_uuid')
            f.set_node('vendor_uuid', colander.String())
            vendor_display = ""
            if self.request.method == 'POST':
                if self.request.POST.get('vendor_uuid'):
                    vendor = self.Session.query(model.Vendor).get(self.request.POST['vendor_uuid'])
                    if vendor:
                        vendor_display = six.text_type(vendor)
            vendors_url = self.request.route_url('vendors.autocomplete')
            f.set_widget('vendor_uuid', forms.widgets.JQueryAutocompleteWidget(
                field_display=vendor_display, service_url=vendors_url))
            f.set_label('vendor_uuid', "Vendor")
        else:
            f.set_readonly('vendor')

        # filename
        f.set_label('filename', "Catalog File")

        if self.creating:

            f.set_fields([
                'filename',
                'parser_key',
                'vendor_uuid',
                'future',
            ])

            parser_values = [(p.key, p.display) for p in self.get_parsers()]
            parser_values.insert(0, ('', "(please choose)"))
            f.set_widget('parser_key', dfwidget.SelectWidget(values=parser_values))
            f.set_label('parser_key', "File Type")

        # effective
        if not self.creating:
            f.set_readonly('effective')

    def render_vendor(self, batch, field):
        vendor = batch.vendor
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def get_batch_kwargs(self, batch):
        kwargs = super(VendorCatalogsView, self).get_batch_kwargs(batch)
        kwargs['parser_key'] = batch.parser_key
        if batch.vendor:
            kwargs['vendor'] = batch.vendor
        elif batch.vendor_uuid:
            kwargs['vendor_uuid'] = batch.vendor_uuid
        kwargs['future'] = batch.future
        return kwargs

    def configure_row_grid(self, g):
        super(VendorCatalogsView, self).configure_row_grid(g)
        batch = self.get_instance()

        # starts
        if not batch.future:
            g.hide_column('starts')

        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('old_unit_cost', "Old Cost")
        g.set_label('unit_cost', "New Cost")
        g.set_label('unit_cost_diff', "Diff.")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'
        if row.status_code in (row.STATUS_NEW_COST,
                               row.STATUS_UPDATE_COST, # TODO: deprecate/remove this one
                               row.STATUS_CHANGE_VENDOR_ITEM_CODE,
                               row.STATUS_CHANGE_CASE_SIZE,
                               row.STATUS_CHANGE_COST):
            return 'notice'

    def configure_row_form(self, f):
        super(VendorCatalogsView, self).configure_row_form(f)
        f.set_renderer('product', self.render_product)
        f.set_type('discount_percent', 'percent')

    def template_kwargs_create(self, **kwargs):
        parsers = self.get_parsers()
        for parser in parsers:
            if parser.vendor_key:
                vendor = api.get_vendor(Session(), parser.vendor_key)
                if vendor:
                    parser.vendormap_value = "{{uuid: '{}', name: '{}'}}".format(
                        vendor.uuid, vendor.name.replace("'", "\\'"))
                else:
                    log.warning("vendor '{}' not found for parser: {}".format(
                        parser.vendor_key, parser.key))
                    parser.vendormap_value = 'null'
            else:
                parser.vendormap_value = 'null'
        kwargs['parsers'] = parsers
        return kwargs


def includeme(config):
    VendorCatalogsView.defaults(config)
