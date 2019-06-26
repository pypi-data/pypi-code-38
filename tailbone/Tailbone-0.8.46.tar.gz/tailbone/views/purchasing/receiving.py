# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Views for 'receiving' (purchasing) batches
"""

from __future__ import unicode_literals, absolute_import

import re
import logging

import six
import humanize
import sqlalchemy as sa

from rattail import pod
from rattail.db import model, api, Session as RattailSession
from rattail.db.util import maxlen
from rattail.gpc import GPC
from rattail.time import localtime, make_utc
from rattail.util import pretty_quantity, prettify, OrderedDict
from rattail.vendors.invoices import iter_invoice_parsers, require_invoice_parser
from rattail.threads import Thread

import colander
from deform import widget as dfwidget
from pyramid import httpexceptions
from webhelpers2.html import tags, HTML

from tailbone import forms, grids
from tailbone.views.purchasing import PurchasingBatchView
from tailbone.progress import SessionProgress


log = logging.getLogger(__name__)


class MobileItemStatusFilter(grids.filters.MobileFilter):

    value_choices = ['incomplete', 'unexpected', 'damaged', 'expired', 'all']

    def filter_equal(self, query, value):

        # NOTE: this is only relevant for truck dump or "from scratch"
        if value == 'received':
            return query.filter(sa.or_(
                model.PurchaseBatchRow.cases_received != 0,
                model.PurchaseBatchRow.units_received != 0))

        if value == 'incomplete':
            # looking for any rows with "ordered" quantity, but where the
            # status does *not* signify a "settled" row so to speak
            # TODO: would be nice if we had a simple flag to leverage?
            return query.filter(sa.or_(model.PurchaseBatchRow.cases_ordered != 0,
                                       model.PurchaseBatchRow.units_ordered != 0))\
                        .filter(~model.PurchaseBatchRow.status_code.in_((
                            model.PurchaseBatchRow.STATUS_OK,
                            model.PurchaseBatchRow.STATUS_PRODUCT_NOT_FOUND,
                            model.PurchaseBatchRow.STATUS_CASE_QUANTITY_DIFFERS)))

        if value == 'invalid':
            return query.filter(model.PurchaseBatchRow.status_code.in_((
                model.PurchaseBatchRow.STATUS_PRODUCT_NOT_FOUND,
                model.PurchaseBatchRow.STATUS_COST_NOT_FOUND,
                model.PurchaseBatchRow.STATUS_CASE_QUANTITY_UNKNOWN,
                model.PurchaseBatchRow.STATUS_CASE_QUANTITY_DIFFERS,
            )))

        if value == 'unexpected':
            # looking for any rows which have "received" quantity but which
            # do *not* have any "ordered" quantity
            return query.filter(sa.and_(
                sa.or_(
                    model.PurchaseBatchRow.cases_ordered == None,
                    model.PurchaseBatchRow.cases_ordered == 0),
                sa.or_(
                    model.PurchaseBatchRow.units_ordered == None,
                    model.PurchaseBatchRow.units_ordered == 0),
                sa.or_(
                    model.PurchaseBatchRow.cases_received != 0,
                    model.PurchaseBatchRow.units_received != 0,
                    model.PurchaseBatchRow.cases_damaged != 0,
                    model.PurchaseBatchRow.units_damaged != 0,
                    model.PurchaseBatchRow.cases_expired != 0,
                    model.PurchaseBatchRow.units_expired != 0)))

        if value == 'damaged':
            return query.filter(sa.or_(
                model.PurchaseBatchRow.cases_damaged != 0,
                model.PurchaseBatchRow.units_damaged != 0))

        if value == 'expired':
            return query.filter(sa.or_(
                model.PurchaseBatchRow.cases_expired != 0,
                model.PurchaseBatchRow.units_expired != 0))

        return query

    def iter_choices(self):
        for value in self.value_choices:
            yield value, prettify(value)


class ReceivingBatchView(PurchasingBatchView):
    """
    Master view for receiving batches
    """
    route_prefix = 'receiving'
    url_prefix = '/receiving'
    model_title = "Receiving Batch"
    model_title_plural = "Receiving Batches"
    index_title = "Receiving"
    downloadable = True
    rows_editable = True
    mobile_creatable = True
    mobile_rows_filterable = True
    mobile_rows_creatable = True
    mobile_rows_quickable = True
    mobile_rows_deletable = True

    allow_from_po = False
    allow_from_scratch = True
    allow_truck_dump = False

    default_uom_is_case = True

    purchase_order_fieldname = 'purchase'

    labels = {
        'truck_dump_batch': "Truck Dump Parent",
        'invoice_parser_key': "Invoice Parser",
    }

    grid_columns = [
        'id',
        'vendor',
        'truck_dump',
        'description',
        'department',
        'buyer',
        'date_ordered',
        'created',
        'created_by',
        'rowcount',
        'invoice_total_calculated',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'batch_type',
        'store',
        'vendor',
        'description',
        'truck_dump',
        'truck_dump_children_first',
        'truck_dump_children',
        'truck_dump_ready',
        'truck_dump_batch',
        'invoice_file',
        'invoice_parser_key',
        'department',
        'purchase',
        'vendor_email',
        'vendor_fax',
        'vendor_contact',
        'vendor_phone',
        'date_ordered',
        'date_received',
        'po_number',
        'po_total',
        'invoice_date',
        'invoice_number',
        'invoice_total',
        'invoice_total_calculated',
        'notes',
        'created',
        'created_by',
        'status_code',
        'truck_dump_status',
        'rowcount',
        'order_quantities_known',
        'complete',
        'executed',
        'executed_by',
    ]

    mobile_form_fields = [
        'vendor',
        'department',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        # 'item_id',
        'brand_name',
        'description',
        'size',
        'department_name',
        'cases_shipped',
        'units_shipped',
        'cases_received',
        'units_received',
        # 'po_total',
        'invoice_total_calculated',
        'credits',
        'status_code',
        'truck_dump_status',
    ]

    row_form_fields = [
        'item_entry',
        'upc',
        'item_id',
        'product',
        'brand_name',
        'description',
        'size',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'cases_shipped',
        'units_shipped',
        'cases_received',
        'units_received',
        'cases_damaged',
        'units_damaged',
        'cases_expired',
        'units_expired',
        'cases_mispick',
        'units_mispick',
        'po_line_number',
        'po_unit_cost',
        'po_total',
        'invoice_line_number',
        'invoice_unit_cost',
        'invoice_total',
        'invoice_total_calculated',
        'status_code',
        'truck_dump_status',
        'claims',
        'credits',
    ]

    # convenience list of all quantity attributes involved for a truck dump claim
    claim_keys = [
        'cases_received',
        'units_received',
        'cases_damaged',
        'units_damaged',
        'cases_expired',
        'units_expired',
    ]

    @property
    def batch_mode(self):
        return self.enum.PURCHASE_BATCH_MODE_RECEIVING

    def row_deletable(self, row):
        batch = row.batch

        # don't allow if master view has disabled that entirely
        if not self.rows_deletable:
            return False

        # can never delete rows for complete/executed batches
        # TODO: not so sure about the 'complete' part though..?
        if batch.executed or batch.complete:
            return False

        # can "always" delete rows from truck dump parent...
        if batch.is_truck_dump_parent():

            # ...but only on desktop!
            if not self.mobile:
                return True

            # ...for mobile we only allow deletion of rows which did *not* come
            # from a child batch, i.e. can delete ad-hoc rows only
            # TODO: should have a better way to detect this; for now we rely on
            # the fact that only rows from an invoice or similar would have
            # order quantities
            if not (row.cases_ordered or row.units_ordered):
                return True

        # can always delete rows from truck dump child
        elif batch.is_truck_dump_child():
            return True

        else: # okay, normal batch
            if batch.order_quantities_known:
                return False
            else: # allow delete if receiving rom scratch
                return True

        # cannot delete row by default
        return False

    def get_instance_title(self, batch):
        title = super(ReceivingBatchView, self).get_instance_title(batch)
        if batch.is_truck_dump_parent():
            title = "{} (TRUCK DUMP PARENT)".format(title)
        elif batch.is_truck_dump_child():
            title = "{} (TRUCK DUMP CHILD)".format(title)
        return title

    def configure_form(self, f):
        super(ReceivingBatchView, self).configure_form(f)
        batch = f.model_instance

        # batch_type
        if self.creating:
            batch_types = OrderedDict()
            if self.allow_from_scratch:
                batch_types['from_scratch'] = "From Scratch"
            if self.allow_from_po:
                batch_types['from_po'] = "From PO"
            if self.allow_truck_dump:
                batch_types['truck_dump_children_first'] = "Truck Dump (children FIRST)"
                batch_types['truck_dump_children_last'] = "Truck Dump (children LAST)"
            f.set_enum('batch_type', batch_types)
        else:
            f.remove_field('batch_type')

        # truck_dump*
        if self.allow_truck_dump:

            # truck_dump
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump')
            else:
                f.set_readonly('truck_dump')

            # truck_dump_children_first
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump_children_first')

            # truck_dump_children
            if self.viewing and batch.is_truck_dump_parent():
                f.set_renderer('truck_dump_children', self.render_truck_dump_children)
            else:
                f.remove_field('truck_dump_children')

            # truck_dump_ready
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump_ready')

            # truck_dump_status
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump_status')
            else:
                f.set_readonly('truck_dump_status')
                f.set_enum('truck_dump_status', model.PurchaseBatch.STATUS)

            # truck_dump_batch
            if self.creating:
                f.replace('truck_dump_batch', 'truck_dump_batch_uuid')
                batches = self.Session.query(model.PurchaseBatch)\
                                      .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)\
                                      .filter(model.PurchaseBatch.truck_dump == True)\
                                      .filter(model.PurchaseBatch.complete == True)\
                                      .filter(model.PurchaseBatch.executed == None)\
                                      .order_by(model.PurchaseBatch.id)
                batch_values = [(b.uuid, "({}) {}, {}".format(b.id_str, b.date_received, b.vendor))
                                for b in batches]
                batch_values.insert(0, ('', "(please choose)"))
                f.set_widget('truck_dump_batch_uuid', forms.widgets.JQuerySelectWidget(values=batch_values))
                f.set_label('truck_dump_batch_uuid', "Truck Dump Parent")
            elif batch.is_truck_dump_child():
                f.set_readonly('truck_dump_batch')
                f.set_renderer('truck_dump_batch', self.render_truck_dump_batch)
            else:
                f.remove_field('truck_dump_batch')

            # truck_dump_vendor
            if self.creating:
                f.set_label('truck_dump_vendor', "Vendor")
                f.set_readonly('truck_dump_vendor')
                f.set_renderer('truck_dump_vendor', self.render_truck_dump_vendor)

        else:
            f.remove_fields('truck_dump',
                            'truck_dump_children_first',
                            'truck_dump_children',
                            'truck_dump_ready',
                            'truck_dump_status',
                            'truck_dump_batch')

        # invoice_file
        if self.creating:
            f.set_type('invoice_file', 'file', required=False)
        else:
            f.set_readonly('invoice_file')
            f.set_renderer('invoice_file', self.render_downloadable_file)

        # invoice_parser_key
        if self.creating:
            parsers = sorted(iter_invoice_parsers(), key=lambda p: p.display)
            parser_values = [(p.key, p.display) for p in parsers]
            parser_values.insert(0, ('', "(please choose)"))
            f.set_widget('invoice_parser_key', forms.widgets.JQuerySelectWidget(values=parser_values))
        else:
            f.remove_field('invoice_parser_key')

        # store
        if self.creating:
            store = self.rattail_config.get_store(self.Session())
            f.set_default('store_uuid', store.uuid)
            # TODO: seems like set_hidden() should also set HiddenWidget
            f.set_hidden('store_uuid')
            f.set_widget('store_uuid', dfwidget.HiddenWidget())

        # purchase
        if self.creating:
            f.remove_field('purchase')

        # department
        if self.creating:
            f.remove_field('department_uuid')

        # order_quantities_known
        if not self.editing:
            f.remove_field('order_quantities_known')

        # invoice totals
        f.set_label('invoice_total', "Invoice Total (Orig.)")
        f.set_label('invoice_total_calculated', "Invoice Total (Calc.)")

    def template_kwargs_create(self, **kwargs):
        kwargs = super(ReceivingBatchView, self).template_kwargs_create(**kwargs)
        if self.allow_truck_dump:
            vmap = {}
            batches = self.Session.query(model.PurchaseBatch)\
                                  .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)\
                                  .filter(model.PurchaseBatch.truck_dump == True)\
                                  .filter(model.PurchaseBatch.complete == True)
            for batch in batches:
                vmap[batch.uuid] = batch.vendor_uuid
            kwargs['batch_vendor_map'] = vmap
        return kwargs

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(ReceivingBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        if not mobile:
            batch_type = self.request.POST['batch_type']
            if batch_type == 'from_scratch':
                kwargs.pop('truck_dump_batch', None)
                kwargs.pop('truck_dump_batch_uuid', None)
            elif batch_type == 'truck_dump_children_first':
                kwargs['truck_dump'] = True
                kwargs['truck_dump_children_first'] = True
                kwargs['order_quantities_known'] = True
                # TODO: this makes sense in some cases, but all?
                # (should just omit that field when not relevant)
                kwargs['date_ordered'] = None
            elif batch_type == 'truck_dump_children_last':
                kwargs['truck_dump'] = True
                kwargs['truck_dump_ready'] = True
                # TODO: this makes sense in some cases, but all?
                # (should just omit that field when not relevant)
                kwargs['date_ordered'] = None
            elif batch_type.startswith('truck_dump_child'):
                truck_dump = self.get_instance()
                kwargs['store'] = truck_dump.store
                kwargs['vendor'] = truck_dump.vendor
                kwargs['truck_dump_batch'] = truck_dump
            else:
                raise NotImplementedError
        return kwargs

    def department_for_purchase(self, purchase):
        pass

    def delete_instance(self, batch):
        """
        Delete all data (files etc.) for the batch.
        """
        truck_dump = batch.truck_dump_batch
        if batch.is_truck_dump_parent():
            for child in batch.truck_dump_children:
                self.delete_instance(child)
        super(ReceivingBatchView, self).delete_instance(batch)
        if truck_dump:
            self.handler.refresh(truck_dump)

    def render_truck_dump_batch(self, batch, field):
        truck_dump = batch.truck_dump_batch
        if not truck_dump:
            return ""
        text = "({}) {}".format(truck_dump.id_str, truck_dump.description or '')
        url = self.request.route_url('receiving.view', uuid=truck_dump.uuid)
        return tags.link_to(text, url)

    def render_truck_dump_vendor(self, batch, field):
        truck_dump = self.get_instance()
        vendor = truck_dump.vendor
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def render_truck_dump_children(self, batch, field):
        contents = []
        children = batch.truck_dump_children
        if children:
            items = []
            for child in children:
                text = "({}) {}".format(child.id_str, child.description or '')
                url = self.request.route_url('receiving.view', uuid=child.uuid)
                items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
            contents.append(HTML.tag('ul', c=items))
        if not batch.executed and (batch.complete or batch.truck_dump_children_first):
            buttons = self.make_truck_dump_child_buttons(batch)
            if buttons:
                buttons = HTML.literal(' ').join(buttons)
                contents.append(HTML.tag('div', class_='buttons', c=[buttons]))
        if not contents:
            return ""
        return HTML.tag('div', c=contents)

    def make_truck_dump_child_buttons(self, batch):
        return [
            tags.link_to("Add from Invoice File", self.get_action_url('add_child_from_invoice', batch), class_='button autodisable'),
        ]

    def add_child_from_invoice(self):
        """
        View for adding a child batch to a truck dump, from invoice file.
        """
        batch = self.get_instance()
        if not batch.is_truck_dump_parent():
            self.request.session.flash("Batch is not a truck dump: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        if batch.executed:
            self.request.session.flash("Batch has already been executed: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        if not batch.complete and not batch.truck_dump_children_first:
            self.request.session.flash("Batch is not marked as complete: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        self.creating = True
        form = self.make_child_from_invoice_form(self.get_model_class())
        return self.create(form=form)

    def make_child_from_invoice_form(self, instance, **kwargs):
        """
        Creates a new form for the given model class/instance
        """
        kwargs['configure'] = self.configure_child_from_invoice_form
        return self.make_form(instance=instance, **kwargs)

    def configure_child_from_invoice_form(self, f):
        assert self.creating
        truck_dump = self.get_instance()

        self.configure_form(f)

        f.set_fields([
            'batch_type',
            'truck_dump_parent',
            'truck_dump_vendor',
            'invoice_file',
            'invoice_parser_key',
            'invoice_number',
            'description',
            'notes',
        ])

        # batch_type
        f.set_widget('batch_type', forms.widgets.ReadonlyWidget())
        f.set_default('batch_type', 'truck_dump_child_from_invoice')

        # truck_dump_batch_uuid
        f.set_readonly('truck_dump_parent')
        f.set_renderer('truck_dump_parent', self.render_truck_dump_parent)

        # invoice_parser_key
        f.set_required('invoice_parser_key')

    def render_truck_dump_parent(self, batch, field):
        truck_dump = self.get_instance()
        text = six.text_type(truck_dump)
        url = self.request.route_url('receiving.view', uuid=truck_dump.uuid)
        return tags.link_to(text, url)

    def render_mobile_listitem(self, batch, i):
        title = "({}) {} for ${:0,.2f} - {}, {}".format(
            batch.id_str,
            batch.vendor,
            batch.invoice_total or batch.po_total or 0,
            batch.department,
            batch.created_by)
        return title

    def make_mobile_row_filters(self):
        """
        Returns a set of filters for the mobile row grid.
        """
        batch = self.get_instance()
        filters = grids.filters.GridFilterSet()

        # visible filter options will depend on whether batch came from purchase
        if batch.order_quantities_known:
            value_choices = ['incomplete', 'unexpected', 'damaged', 'expired', 'invalid', 'all']
            default_status = 'incomplete'
        else:
            value_choices = ['received', 'damaged', 'expired', 'invalid', 'all']
            default_status = 'all'

        # remove 'expired' filter option if not relevant
        if 'expired' in value_choices and not self.handler.allow_expired_credits():
            value_choices.remove('expired')

        filters['status'] = MobileItemStatusFilter('status',
                                                   value_choices=value_choices,
                                                   default_value=default_status)
        return filters

    def get_purchase(self, uuid):
        return self.Session.query(model.Purchase).get(uuid)

    def mobile_create(self):
        """
        Mobile view for creating a new receiving batch
        """
        mode = self.batch_mode
        data = {'mode': mode}
        phase = 1

        schema = MobileNewReceivingBatch().bind(session=self.Session())
        form = forms.Form(schema=schema, request=self.request)
        if form.validate(newstyle=True):
            phase = form.validated['phase']

            if form.validated['workflow'] == 'from_scratch':
                if not self.allow_from_scratch:
                    raise NotImplementedError("Requested workflow not supported: from_scratch")
                batch = self.model_class()
                batch.store = self.rattail_config.get_store(self.Session())
                batch.mode = mode
                batch.vendor = self.Session.query(model.Vendor).get(form.validated['vendor'])
                batch.created_by = self.request.user
                batch.date_received = localtime(self.rattail_config).date()
                kwargs = self.get_batch_kwargs(batch, mobile=True)
                batch = self.handler.make_batch(self.Session(), **kwargs)
                return self.redirect(self.get_action_url('view', batch, mobile=True))

            elif form.validated['workflow'] == 'truck_dump':
                if not self.allow_truck_dump:
                    raise NotImplementedError("Requested workflow not supported: truck_dump")
                batch = self.model_class()
                batch.store = self.rattail_config.get_store(self.Session())
                batch.mode = mode
                batch.truck_dump = True
                batch.vendor = self.Session.query(model.Vendor).get(form.validated['vendor'])
                batch.created_by = self.request.user
                batch.date_received = localtime(self.rattail_config).date()
                kwargs = self.get_batch_kwargs(batch, mobile=True)
                batch = self.handler.make_batch(self.Session(), **kwargs)
                return self.redirect(self.get_action_url('view', batch, mobile=True))

            elif form.validated['workflow'] == 'from_po':
                if not self.allow_from_po:
                    raise NotImplementedError("Requested workflow not supported: from_po")

                vendor = self.Session.query(model.Vendor).get(form.validated['vendor'])
                data['vendor'] = vendor

                schema = self.make_mobile_receiving_from_po_schema()
                po_form = forms.Form(schema=schema, request=self.request)
                if phase == 2:
                    if po_form.validate(newstyle=True):
                        batch = self.model_class()
                        batch.store = self.rattail_config.get_store(self.Session())
                        batch.mode = mode
                        batch.vendor = vendor
                        batch.buyer = self.request.user.employee
                        batch.created_by = self.request.user
                        batch.date_received = localtime(self.rattail_config).date()
                        self.assign_purchase_order(batch, po_form)
                        kwargs = self.get_batch_kwargs(batch, mobile=True)
                        batch = self.handler.make_batch(self.Session(), **kwargs)
                        if self.handler.should_populate(batch):
                            self.handler.populate(batch)
                        return self.redirect(self.get_action_url('view', batch, mobile=True))

                else:
                    phase = 2

            else:
                raise NotImplementedError("Requested workflow not supported: {}".format(form.validated['workflow']))

        data['form'] = form
        data['dform'] = form.make_deform_form()
        data['mode_title'] = self.enum.PURCHASE_BATCH_MODE[mode].capitalize()
        data['phase'] = phase

        if phase == 1:
            data['vendor_use_autocomplete'] = self.rattail_config.getbool(
                'rattail', 'vendor.use_autocomplete', default=True)
            if not data['vendor_use_autocomplete']:
                vendors = self.Session.query(model.Vendor)\
                                      .order_by(model.Vendor.name)
                options = [(tags.Option(vendor.name, vendor.uuid))
                           for vendor in vendors]
                options.insert(0, tags.Option("(please choose)", ''))
                data['vendor_options'] = options

        elif phase == 2:
            purchases = self.eligible_purchases(vendor.uuid, mode=mode)
            data['purchases'] = [(p['key'], p['display']) for p in purchases['purchases']]
            data['purchase_order_fieldname'] = self.purchase_order_fieldname

        return self.render_to_response('create', data, mobile=True)

    def make_mobile_receiving_from_po_schema(self):
        schema = colander.MappingSchema()
        schema.add(colander.SchemaNode(colander.String(),
                                       name=self.purchase_order_fieldname,
                                       validator=self.validate_purchase))
        return schema.bind(session=self.Session())

    @staticmethod
    @colander.deferred
    def validate_purchase(node, kw):
        session = kw['session']
        def validate(node, value):
            purchase = session.query(model.Purchase).get(value)
            if not purchase:
                raise colander.Invalid(node, "Purchase not found")
            return purchase.uuid
        return validate

    def assign_purchase_order(self, batch, po_form):
        """
        Assign the original purchase order to the given batch.  Default
        behavior assumes a Rattail Purchase object is what we're after.
        """
        purchase = self.get_purchase(po_form.validated[self.purchase_order_fieldname])
        if isinstance(purchase, model.Purchase):
            batch.purchase_uuid = purchase.uuid

        department = self.department_for_purchase(purchase)
        if department:
            batch.department_uuid = department.uuid

    def configure_mobile_form(self, f):
        super(ReceivingBatchView, self).configure_mobile_form(f)
        batch = f.model_instance

        # truck_dump
        if not self.creating:
            if not batch.is_truck_dump_parent():
                f.remove_field('truck_dump')

        # department
        if not self.creating:
            if batch.is_truck_dump_parent():
                f.remove_field('department')

    def configure_row_grid(self, g):
        super(ReceivingBatchView, self).configure_row_grid(g)
        g.set_label('department_name', "Department")

        # credits
        # note that sorting by credits involves a subquery with group by clause.
        # seems likely there may be a better way? but this seems to work fine
        Credits = self.Session.query(model.PurchaseBatchCredit.row_uuid,
                                     sa.func.count().label('credit_count'))\
                              .group_by(model.PurchaseBatchCredit.row_uuid)\
                              .subquery()
        g.set_joiner('credits', lambda q: q.outerjoin(Credits))
        g.sorters['credits'] = lambda q, d: q.order_by(getattr(Credits.c.credit_count, d)())

        # hide 'ordered' columns for truck dump parent, if its "children first"
        # flag is set, since that batch type is only concerned with receiving
        batch = self.get_instance()
        if batch.is_truck_dump_parent() and not batch.truck_dump_children_first:
            g.hide_column('cases_ordered')
            g.hide_column('units_ordered')

        # add "Transform to Unit" action, if appropriate
        if batch.is_truck_dump_parent():
            permission_prefix = self.get_permission_prefix()
            if self.request.has_perm('{}.edit_row'.format(permission_prefix)):
                transform = grids.GridAction('transform',
                                             icon='shuffle',
                                             label="Transform to Unit",
                                             url=self.transform_unit_url)
                g.more_actions.append(transform)
                if g.main_actions and g.main_actions[-1].key == 'delete':
                    delete = g.main_actions.pop()
                    g.more_actions.append(delete)

        # truck_dump_status
        if not batch.is_truck_dump_parent():
            g.hide_column('truck_dump_status')
        else:
            g.set_enum('truck_dump_status', model.PurchaseBatchRow.STATUS)

    def transform_unit_url(self, row, i):
        # grid action is shown only when we return a URL here
        if self.row_editable(row):
            if row.batch.is_truck_dump_parent():
                if row.product and row.product.is_pack_item():
                    return self.get_row_action_url('transform_unit', row)

    def receive_row(self, mobile=False):
        """
        Primary desktop view for row-level receiving.
        """
        # TODO: this code was largely copied from mobile_receive_row() but it
        # tries to pave the way for shared logic, i.e. where the latter would
        # simply invoke this method and return the result.  however we're not
        # there yet...for now it's only tested for desktop
        self.mobile = mobile
        self.viewing = True
        row = self.get_row_instance()
        batch = row.batch
        permission_prefix = self.get_permission_prefix()
        possible_modes = [
            'received',
            'damaged',
            'expired',
        ]
        context = {
            'row': row,
            'batch': batch,
            'parent_instance': batch,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': self.get_row_image_url(row),
            'allow_expired': self.handler.allow_expired_credits(),
            'allow_cases': self.handler.allow_cases(),
            'quick_receive': False,
            'quick_receive_all': False,
        }

        if mobile:
            context['quick_receive'] = self.rattail_config.getbool('rattail.batch', 'purchase.mobile_quick_receive',
                                                                   default=True)
            if batch.order_quantities_known:
                context['quick_receive_all'] = self.rattail_config.getbool('rattail.batch', 'purchase.mobile_quick_receive_all',
                                                                           default=False)

        schema = ReceiveRowForm().bind(session=self.Session())
        form = forms.Form(schema=schema, request=self.request)
        form.cancel_url = self.get_row_action_url('view', row, mobile=mobile)
        form.set_widget('mode', forms.widgets.JQuerySelectWidget(values=[(m, m) for m in possible_modes]))
        form.set_widget('quantity', forms.widgets.CasesUnitsWidget(amount_required=True,
                                                                   one_amount_only=True))
        form.set_type('expiration_date', 'date_jquery')

        if not mobile:
            form.remove_field('quick_receive')

        if form.validate(newstyle=True):

            # handler takes care of the row receiving logic for us
            kwargs = dict(form.validated)
            kwargs['cases'] = kwargs['quantity']['cases']
            kwargs['units'] = kwargs['quantity']['units']
            del kwargs['quantity']
            self.handler.receive_row(row, **kwargs)

            # keep track of last-used uom, although we just track
            # whether or not it was 'CS' since the unit_uom can vary
            # TODO: should this be done for desktop too somehow?
            sticky_case = None
            if mobile and not form.validated['quick_receive']:
                cases = form.validated['cases']
                units = form.validated['units']
                if cases and not units:
                    sticky_case = True
                elif units and not cases:
                    sticky_case = False
            if sticky_case is not None:
                self.request.session['tailbone.mobile.receiving.sticky_uom_is_case'] = sticky_case

            if mobile:
                return self.redirect(self.get_action_url('view', batch, mobile=True))
            else:
                return self.redirect(self.get_row_action_url('view', row))

        # unit_uom can vary by product
        context['unit_uom'] = 'LB' if row.product and row.product.weighed else 'EA'

        if context['quick_receive'] and context['quick_receive_all']:
            if context['allow_cases']:
                context['quick_receive_uom'] = 'CS'
                raise NotImplementedError("TODO: add CS support for quick_receive_all")
            else:
                context['quick_receive_uom'] = context['unit_uom']
                accounted_for = self.handler.get_units_accounted_for(row)
                remainder = self.handler.get_units_ordered(row) - accounted_for

                if accounted_for:
                    # some product accounted for; button should receive "remainder" only
                    if remainder:
                        remainder = pretty_quantity(remainder)
                        context['quick_receive_quantity'] = remainder
                        context['quick_receive_text'] = "Receive Remainder ({} {})".format(remainder, context['unit_uom'])
                    else:
                        # unless there is no remainder, in which case disable it
                        context['quick_receive'] = False

                else: # nothing yet accounted for, button should receive "all"
                    if not remainder:
                        raise ValueError("why is remainder empty?")
                    remainder = pretty_quantity(remainder)
                    context['quick_receive_quantity'] = remainder
                    context['quick_receive_text'] = "Receive ALL ({} {})".format(remainder, context['unit_uom'])

        # effective uom can vary in a few ways...the basic default is 'CS' if
        # self.default_uom_is_case is true, otherwise whatever unit_uom is.
        sticky_case = None
        if mobile:
            # TODO: should do this for desktop also, but rename the session variable
            sticky_case = self.request.session.get('tailbone.mobile.receiving.sticky_uom_is_case')
        if sticky_case is None:
            context['uom'] = 'CS' if self.default_uom_is_case else context['unit_uom']
        elif sticky_case:
            context['uom'] = 'CS'
        else:
            context['uom'] = context['unit_uom']
        if context['uom'] == 'CS' and row.units_ordered and not row.cases_ordered:
            context['uom'] = context['unit_uom']

        # TODO: should do this for desktop in addition to mobile?
        if mobile and batch.order_quantities_known and not row.cases_ordered and not row.units_ordered:
            warn = True
            if batch.is_truck_dump_parent() and row.product:
                uuids = [child.uuid for child in batch.truck_dump_children]
                if uuids:
                    count = self.Session.query(model.PurchaseBatchRow)\
                                        .filter(model.PurchaseBatchRow.batch_uuid.in_(uuids))\
                                        .filter(model.PurchaseBatchRow.product == row.product)\
                                        .count()
                    if count:
                        warn = False
            if warn:
                self.request.session.flash("This item was NOT on the original purchase order.", 'receiving-warning')

        # TODO: should do this for desktop in addition to mobile?
        if mobile:
            # maybe alert user if they've already received some of this product
            alert_received = self.rattail_config.getbool('tailbone', 'receiving.alert_already_received',
                                                         default=False)
            if alert_received:
                if self.handler.get_units_confirmed(row):
                    msg = "You have already received some of this product; last update was {}.".format(
                        humanize.naturaltime(make_utc() - row.modified))
                    self.request.session.flash(msg, 'receiving-warning')

        context['form'] = form
        context['dform'] = form.make_deform_form()
        context['parent_url'] = self.get_action_url('view', batch, mobile=mobile)
        context['parent_title'] = self.get_instance_title(batch)
        return self.render_to_response('receive_row', context, mobile=mobile)

    def declare_credit(self):
        """
        View for declaring a credit, i.e. converting some "received" or similar
        quantity, to a credit of some sort.
        """
        row = self.get_row_instance()
        batch = row.batch
        possible_credit_types = [
            'damaged',
            'expired',
        ]
        context = {
            'row': row,
            'batch': batch,
            'parent_instance': batch,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': self.get_row_image_url(row),
            'allow_expired': self.handler.allow_expired_credits(),
            'allow_cases': self.handler.allow_cases(),
        }

        schema = DeclareCreditForm()
        form = forms.Form(schema=schema, request=self.request)
        form.set_widget('credit_type', forms.widgets.JQuerySelectWidget(
            values=[(m, m) for m in possible_credit_types]))
        form.set_widget('quantity', forms.widgets.CasesUnitsWidget(
            amount_required=True, one_amount_only=True))
        form.set_type('expiration_date', 'date_jquery')

        if form.validate(newstyle=True):

            # handler takes care of the row receiving logic for us
            kwargs = dict(form.validated)
            kwargs['cases'] = kwargs['quantity']['cases']
            kwargs['units'] = kwargs['quantity']['units']
            del kwargs['quantity']
            try:
                result = self.handler.can_declare_credit(row, **kwargs)
            except Exception as error:
                self.request.session.flash("Handler says you can't declare that credit: {}".format(error), 'error')
            else:
                if result:
                    self.handler.declare_credit(row, **kwargs)
                    return self.redirect(self.get_row_action_url('view', row))

                self.request.session.flash("Handler says you can't declare that credit; not sure why", 'error')

        context['form'] = form
        context['dform'] = form.make_deform_form()
        context['parent_url'] = self.get_action_url('view', batch)
        context['parent_title'] = self.get_instance_title(batch)
        return self.render_to_response('declare_credit', context)

    def transform_unit_row(self):
        """
        View which transforms the given row, which is assumed to associate with
        a "pack" item, such that it instead associates with the "unit" item,
        with quantities adjusted accordingly.
        """
        batch = self.get_instance()

        row_uuid = self.request.params.get('row_uuid')
        row = self.Session.query(model.PurchaseBatchRow).get(row_uuid) if row_uuid else None
        if row and row.batch is batch and not row.removed:
            pass # we're good
        else:
            if self.request.method == 'POST':
                raise self.notfound()
            return {'error': "Row not found."}

        def normalize(product):
            data = {
                'upc': product.upc,
                'item_id': product.item_id,
                'description': product.description,
                'size': product.size,
                'case_quantity': None,
                'cases_received': row.cases_received,
            }
            cost = product.cost_for_vendor(batch.vendor)
            if cost:
                data['case_quantity'] = cost.case_size
            return data

        if self.request.method == 'POST':
            self.handler.transform_pack_to_unit(row)
            self.request.session.flash("Transformed pack to unit item for: {}".format(row.product))
            return self.redirect(self.get_action_url('view', batch))

        pack_data = normalize(row.product)
        pack_data['units_received'] = row.units_received
        unit_data = normalize(row.product.unit)
        unit_data['units_received'] = None
        if row.units_received:
            unit_data['units_received'] = row.units_received * row.product.pack_size
        diff = self.make_diff(pack_data, unit_data, monospace=True)
        return self.render_to_response('transform_unit_row', {
            'batch': batch,
            'row': row,
            'diff': diff,
        })

    def configure_row_form(self, f):
        super(ReceivingBatchView, self).configure_row_form(f)
        batch = self.get_instance()

        # allow input for certain fields only; all others are readonly
        mutable = [
            'invoice_unit_cost',
        ]
        for name in f.fields:
            if name not in mutable:
                f.set_readonly(name)

        # invoice totals
        f.set_label('invoice_total', "Invoice Total (Orig.)")
        f.set_label('invoice_total_calculated', "Invoice Total (Calc.)")

        # claims
        f.set_readonly('claims')
        if batch.is_truck_dump_parent():
            f.set_renderer('claims', self.render_parent_row_claims)
            f.set_helptext('claims', "Parent row is claimed by these child rows.")
        elif batch.is_truck_dump_child():
            f.set_renderer('claims', self.render_child_row_claims)
            f.set_helptext('claims', "Child row makes claims against these parent rows.")
        else:
            f.remove_field('claims')

        # truck_dump_status
        if self.creating or not batch.is_truck_dump_parent():
            f.remove_field('truck_dump_status')
        else:
            f.set_readonly('truck_dump_status')
            f.set_enum('truck_dump_status', model.PurchaseBatchRow.STATUS)

    def render_parent_row_claims(self, row, field):
        items = []
        for claim in row.claims:
            child_row = claim.claiming_row
            child_batch = child_row.batch
            text = child_batch.id_str
            if child_batch.description:
                text = "{} ({})".format(text, child_batch.description)
            text = "{}, row {}".format(text, child_row.sequence)
            url = self.get_row_action_url('view', child_row)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def render_child_row_claims(self, row, field):
        items = []
        for claim in row.truck_dump_claims:
            parent_row = claim.claimed_row
            parent_batch = parent_row.batch
            text = parent_batch.id_str
            if parent_batch.description:
                text = "{} ({})".format(text, parent_batch.description)
            text = "{}, row {}".format(text, parent_row.sequence)
            url = self.get_row_action_url('view', parent_row)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def validate_row_form(self, form):

        # if normal validation fails, stop there
        if not super(ReceivingBatchView, self).validate_row_form(form):
            return False

        # if user is editing row from truck dump child, then we must further
        # validate the form to ensure whatever new amounts they've requested
        # would in fact fall within the bounds of what is available from the
        # truck dump parent batch...
        if self.editing:
            batch = self.get_instance()
            if batch.is_truck_dump_child():
                old_row = self.get_row_instance()
                case_quantity = old_row.case_quantity

                # get all "existing" (old) claim amounts
                old_claims = {}
                for claim in old_row.truck_dump_claims:
                    for key in self.claim_keys:
                        amount = getattr(claim, key)
                        if amount is not None:
                            old_claims[key] = old_claims.get(key, 0) + amount

                # get all "proposed" (new) claim amounts
                new_claims = {}
                for key in self.claim_keys:
                    amount = form.validated[key]
                    if amount is not colander.null and amount is not None:
                        # do not allow user to request a negative claim amount
                        if amount < 0:
                            self.request.session.flash("Cannot claim a negative amount for: {}".format(key), 'error')
                            return False
                        new_claims[key] = amount

                # figure out what changes are actually being requested
                claim_diff = {}
                for key in new_claims:
                    if key not in old_claims:
                        claim_diff[key] = new_claims[key]
                    elif new_claims[key] != old_claims[key]:
                        claim_diff[key] = new_claims[key] - old_claims[key]
                        # do not allow user to request a negative claim amount
                        if claim_diff[key] < (0 - old_claims[key]):
                            self.request.session.flash("Cannot claim a negative amount for: {}".format(key), 'error')
                            return False
                for key in old_claims:
                    if key not in new_claims:
                        claim_diff[key] = 0 - old_claims[key]

                # find all rows from truck dump parent which "may" pertain to child row
                # TODO: perhaps would need to do a more "loose" match on UPC also?
                if not old_row.product_uuid:
                    raise NotImplementedError("Don't (yet) know how to handle edit for row with no product")
                parent_rows = [row for row in batch.truck_dump_batch.active_rows()
                               if row.product_uuid == old_row.product_uuid]

                # NOTE: "confirmed" are the proper amounts which exist in the
                # parent batch.  "claimed" are the amounts claimed by this row.

                # get existing "confirmed" and "claimed" amounts for all
                # (possibly related) truck dump parent rows
                confirmed = {}
                claimed = {}
                for parent_row in parent_rows:
                    for key in self.claim_keys:
                        amount = getattr(parent_row, key)
                        if amount is not None:
                            confirmed[key] = confirmed.get(key, 0) + amount
                    for claim in parent_row.claims:
                        for key in self.claim_keys:
                            amount = getattr(claim, key)
                            if amount is not None:
                                claimed[key] = claimed.get(key, 0) + amount

                # now to see if user's request is possible, given what is
                # available...

                # first we must (pretend to) "relinquish" any claims which are
                # to be reduced or eliminated, according to our diff
                for key, amount in claim_diff.items():
                    if amount < 0:
                        amount = abs(amount) # make positive, for more readable math
                        if key not in claimed or claimed[key] < amount:
                            self.request.session.flash("Cannot relinquish more claims than the "
                                                       "parent batch has to offer.", 'error')
                            return False
                        claimed[key] -= amount

                # next we must determine if any "new" requests would increase
                # the claim(s) beyond what is available
                for key, amount in claim_diff.items():
                    if amount > 0:
                        claimed[key] = claimed.get(key, 0) + amount
                        if key not in confirmed or confirmed[key] < claimed[key]:
                            self.request.session.flash("Cannot request to claim more product than "
                                                       "is available in Truck Dump Parent batch", 'error')
                            return False

                # looks like the claim diff is all good, so let's attach that
                # to the form now and then pick this up again in save()
                form._claim_diff = claim_diff

        # all validation went ok
        return True

    def save_edit_row_form(self, form):
        batch = self.get_instance()
        row = self.objectify(form)

        # editing a row for truck dump child batch can be complicated...
        if batch.is_truck_dump_child():

            # grab the claim diff which we attached to the form during validation
            claim_diff = form._claim_diff

            # first we must "relinquish" any claims which are to be reduced or
            # eliminated, according to our diff
            for key, amount in claim_diff.items():
                if amount < 0:
                    amount = abs(amount) # make positive, for more readable math

                    # we'd prefer to find an exact match, i.e. there was a 1CS
                    # claim and our diff said to reduce by 1CS
                    matches = [claim for claim in row.truck_dump_claims
                               if getattr(claim, key) == amount]
                    if matches:
                        claim = matches[0]
                        setattr(claim, key, None)

                    else:
                        # but if no exact match(es) then we'll just whittle
                        # away at whatever (smallest) claims we do find
                        possible = [claim for claim in row.truck_dump_claims
                                    if getattr(claim, key) is not None]
                        for claim in sorted(possible, key=lambda claim: getattr(claim, key)):
                            previous = getattr(claim, key)
                            if previous:
                                if previous >= amount:
                                    if (previous - amount):
                                        setattr(claim, key, previous - amount)
                                    else:
                                        setattr(claim, key, None)
                                    amount = 0
                                    break
                                else:
                                    setattr(claim, key, None)
                                    amount -= previous

                        if amount:
                            raise NotImplementedError("Had leftover amount when \"relinquishing\" claim(s)")

            # next we must stake all new claim(s) as requested, per our diff
            for key, amount in claim_diff.items():
                if amount > 0:

                    # if possible, we'd prefer to add to an existing claim
                    # which already has an amount for this key
                    existing = [claim for claim in row.truck_dump_claims
                                if getattr(claim, key) is not None]
                    if existing:
                        claim = existing[0]
                        setattr(claim, key, getattr(claim, key) + amount)

                    # next we'd prefer to add to an existing claim, of any kind
                    elif row.truck_dump_claims:
                        claim = row.truck_dump_claims[0]
                        setattr(claim, key, (getattr(claim, key) or 0) + amount)

                    else:
                        # otherwise we must create a new claim...

                        # find all rows from truck dump parent which "may" pertain to child row
                        # TODO: perhaps would need to do a more "loose" match on UPC also?
                        if not row.product_uuid:
                            raise NotImplementedError("Don't (yet) know how to handle edit for row with no product")
                        parent_rows = [parent_row for parent_row in batch.truck_dump_batch.active_rows()
                                       if parent_row.product_uuid == row.product_uuid]

                        # remove any parent rows which are fully claimed
                        # TODO: should perhaps leverage actual amounts for this, instead
                        parent_rows = [parent_row for parent_row in parent_rows
                                       if parent_row.status_code != parent_row.STATUS_TRUCKDUMP_CLAIMED]

                        # try to find a parent row which is exact match on claim amount
                        matches = [parent_row for parent_row in parent_rows
                                   if getattr(parent_row, key) == amount]
                        if matches:

                            # make the claim against first matching parent row
                            claim = model.PurchaseBatchRowClaim()
                            claim.claimed_row = parent_rows[0]
                            setattr(claim, key, amount)
                            row.truck_dump_claims.append(claim)

                        else:
                            # but if no exact match(es) then we'll just whittle
                            # away at whatever (smallest) parent rows we do find
                            for parent_row in sorted(parent_rows, lambda prow: getattr(prow, key)):

                                available = getattr(parent_row, key) - sum([getattr(claim, key) for claim in parent_row.claims])
                                if available:
                                    if available >= amount:
                                        # make claim against this parent row, making it fully claimed
                                        claim = model.PurchaseBatchRowClaim()
                                        claim.claimed_row = parent_row
                                        setattr(claim, key, amount)
                                        row.truck_dump_claims.append(claim)
                                        amount = 0
                                        break
                                    else:
                                        # make partial claim against this parent row
                                        claim = model.PurchaseBatchRowClaim()
                                        claim.claimed_row = parent_row
                                        setattr(claim, key, available)
                                        row.truck_dump_claims.append(claim)
                                        amount -= available

                            if amount:
                                raise NotImplementedError("Had leftover amount when \"staking\" claim(s)")

            # now we must be sure to refresh all truck dump parent batch rows
            # which were affected.  but along with that we also should purge
            # any empty claims, i.e. those which were fully relinquished
            pending_refresh = set()
            for claim in list(row.truck_dump_claims):
                parent_row = claim.claimed_row
                if claim.is_empty():
                    row.truck_dump_claims.remove(claim)
                    self.Session.flush()
                pending_refresh.add(parent_row)
            for parent_row in pending_refresh:
                self.handler.refresh_row(parent_row)
            self.handler.refresh_batch_status(batch.truck_dump_batch)

        self.after_edit_row(row)
        self.Session.flush()
        return row

    def redirect_after_edit_row(self, row, mobile=False):
        return self.redirect(self.get_row_action_url('view', row, mobile=mobile))

    def render_mobile_row_listitem(self, row, i):
        key = self.render_product_key_value(row)
        description = row.product.full_description if row.product else row.description
        return "({}) {}".format(key, description)

    def make_mobile_row_grid_kwargs(self, **kwargs):
        kwargs = super(ReceivingBatchView, self).make_mobile_row_grid_kwargs(**kwargs)

        # use custom `receive_row` instead of `view_row`
        # TODO: should still use `view_row` in some cases? e.g. executed batch
        kwargs['url'] = lambda obj: self.get_row_action_url('receive', obj, mobile=True)

        return kwargs

    def should_aggregate_products(self, batch):
        """
        Must return a boolean indicating whether rows should be aggregated by
        product for the given batch.
        """
        return True

    def quick_locate_rows(self, batch, entry, product):
        rows = []

        # try to locate rows by product uuid match before other key
        if product:
            rows = [row for row in batch.active_rows()
                    if row.product_uuid == product.uuid]
            if rows:
                return rows

        key = self.rattail_config.product_key()
        if key == 'upc':

            if entry.isdigit():

                # we prefer "exact" UPC matches, i.e. those which assumed the entry
                # already contained the check digit.
                provided = GPC(entry, calc_check_digit=False)
                rows = [row for row in batch.active_rows()
                        if row.upc == provided]
                if rows:
                    return rows

                # if no "exact" UPC matches, we'll settle for those (UPC matches)
                # which assume the entry lacked a check digit.
                checked = GPC(entry, calc_check_digit='upc')
                rows = [row for row in batch.active_rows()
                        if row.upc == checked]
                return rows

        elif key == 'item_id':
            rows = [row for row in batch.active_rows()
                    if row.item_id == entry]
            return rows

    def quick_locate_product(self, batch, entry):

        # first let the handler attempt lookup on product key (only)
        product = self.handler.locate_product_for_entry(self.Session(), entry,
                                                        lookup_by_code=False)
        if product:
            return product

        # now we'll attempt lookup by vendor item code
        product = api.get_product_by_vendor_code(self.Session(), entry, vendor=batch.vendor)
        if product:
            return product

        # okay then, let's attempt lookup by "alternate" code
        product = api.get_product_by_code(self.Session(), entry)
        if product:
            return product

    def save_quick_row_form(self, form):
        batch = self.get_instance()
        entry = form.validated['quick_entry']

        # first try to locate the product based on quick entry
        product = self.quick_locate_product(batch, entry)

        # then try to locate existing row(s) which match product/entry
        rows = self.quick_locate_rows(batch, entry, product)
        if rows:

            # if aggregating, just re-use matching row
            prefer_existing = self.should_aggregate_products(batch)
            if prefer_existing:
                if len(rows) > 1:
                    log.warning("found multiple row matches for '%s' in batch %s: %s",
                                entry, batch.id_str, batch)
                return rows[0]

            else: # borrow product from matching row, but make new row
                other_row = rows[0]
                row = model.PurchaseBatchRow()
                row.item_entry = entry
                row.product = other_row.product
                self.handler.add_row(batch, row)
                self.Session.flush()
                self.handler.refresh_batch_status(batch)
                return row

        # matching row(s) not found; add new row if product was identified
        # TODO: probably should be smarter about how we handle deleted?
        if product and not product.deleted:
            row = model.PurchaseBatchRow()
            row.item_entry = entry
            row.product = product
            self.handler.add_row(batch, row)
            self.Session.flush()
            self.handler.refresh_batch_status(batch)
            return row

        key = self.rattail_config.product_key()
        if key == 'upc':

            # check for "bad" upc
            if len(entry) > 14:
                return

            if not entry.isdigit():
                return

            provided = GPC(entry, calc_check_digit=False)
            checked = GPC(entry, calc_check_digit='upc')

            # product not in system, but presumably sane upc, so add to batch anyway
            row = model.PurchaseBatchRow()
            row.item_entry = entry
            add_check_digit = True # TODO: make this dynamic, of course
            if add_check_digit:
                row.upc = checked
            else:
                row.upc = provided
            row.item_id = entry
            row.description = "(unknown product)"
            self.handler.add_row(batch, row)
            self.Session.flush()
            self.handler.refresh_batch_status(batch)
            return row

        elif key == 'item_id':

            # check for "too long" item_id
            if len(entry) > maxlen(model.PurchaseBatchRow.item_id):
                return

            # product not in system, but presumably sane item_id, so add to batch anyway
            row = model.PurchaseBatchRow()
            row.item_entry = entry
            row.item_id = entry
            row.description = "(unknown product)"
            self.handler.add_row(batch, row)
            self.Session.flush()
            self.handler.refresh_batch_status(batch)
            return row

        else:
            raise NotImplementedError("don't know how to handle product key: {}".format(key))

    def redirect_after_quick_row(self, row, mobile=False):
        if mobile:
            return self.redirect(self.get_row_action_url('receive', row, mobile=mobile))
        return super(ReceivingBatchView, self).redirect_after_quick_row(row, mobile=mobile)

    def get_row_image_url(self, row):
        if self.rattail_config.getbool('rattail.batch', 'purchase.mobile_images', default=True):
            return pod.get_image_url(self.rattail_config, row.upc)

    def get_mobile_data(self, session=None):
        query = super(ReceivingBatchView, self).get_mobile_data(session=session)

        # do not expose truck dump child batches on mobile
        # TODO: is there any case where we *would* want to?
        query = query.filter(model.PurchaseBatch.truck_dump_batch == None)

        return query

    def mobile_view_row(self):
        """
        Mobile view for receiving batch row items.  Note that this also handles
        updating a row.
        """
        self.mobile = True
        self.viewing = True
        row = self.get_row_instance()
        batch = row.batch
        permission_prefix = self.get_permission_prefix()
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'batch': batch,
            'parent_instance': batch,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': self.get_row_image_url(row),
            'form': form,
            'allow_expired': self.handler.allow_expired_credits(),
            'allow_cases': self.handler.allow_cases(),
            'quick_receive': False,
            'quick_receive_all': False,
        }

        context['quick_receive'] = self.rattail_config.getbool('rattail.batch', 'purchase.mobile_quick_receive',
                                                               default=True)
        if batch.order_quantities_known:
            context['quick_receive_all'] = self.rattail_config.getbool('rattail.batch', 'purchase.mobile_quick_receive_all',
                                                                       default=False)

        if self.request.has_perm('{}.create_row'.format(permission_prefix)):
            schema = MobileReceivingForm().bind(session=self.Session())
            update_form = forms.Form(schema=schema, request=self.request)
            if update_form.validate(newstyle=True):
                row = self.Session.query(model.PurchaseBatchRow).get(update_form.validated['row'])
                mode = update_form.validated['mode']
                cases = update_form.validated['cases']
                units = update_form.validated['units']

                # handler takes care of the row receiving logic for us
                kwargs = dict(update_form.validated)
                del kwargs['row']
                self.handler.receive_row(row, **kwargs)

                # keep track of last-used uom, although we just track
                # whether or not it was 'CS' since the unit_uom can vary
                sticky_case = None
                if not update_form.validated['quick_receive']:
                    if cases and not units:
                        sticky_case = True
                    elif units and not cases:
                        sticky_case = False
                if sticky_case is not None:
                    self.request.session['tailbone.mobile.receiving.sticky_uom_is_case'] = sticky_case

                return self.redirect(self.get_action_url('view', batch, mobile=True))

        # unit_uom can vary by product
        context['unit_uom'] = 'LB' if row.product and row.product.weighed else 'EA'

        if context['quick_receive'] and context['quick_receive_all']:
            if context['allow_cases']:
                context['quick_receive_uom'] = 'CS'
                raise NotImplementedError("TODO: add CS support for quick_receive_all")
            else:
                context['quick_receive_uom'] = context['unit_uom']
                accounted_for = self.handler.get_units_accounted_for(row)
                remainder = self.handler.get_units_ordered(row) - accounted_for

                if accounted_for:
                    # some product accounted for; button should receive "remainder" only
                    if remainder:
                        remainder = pretty_quantity(remainder)
                        context['quick_receive_quantity'] = remainder
                        context['quick_receive_text'] = "Receive Remainder ({} {})".format(remainder, context['unit_uom'])
                    else:
                        # unless there is no remainder, in which case disable it
                        context['quick_receive'] = False

                else: # nothing yet accounted for, button should receive "all"
                    if not remainder:
                        raise ValueError("why is remainder empty?")
                    remainder = pretty_quantity(remainder)
                    context['quick_receive_quantity'] = remainder
                    context['quick_receive_text'] = "Receive ALL ({} {})".format(remainder, context['unit_uom'])

        # effective uom can vary in a few ways...the basic default is 'CS' if
        # self.default_uom_is_case is true, otherwise whatever unit_uom is.
        sticky_case = self.request.session.get('tailbone.mobile.receiving.sticky_uom_is_case')
        if sticky_case is None:
            context['uom'] = 'CS' if self.default_uom_is_case else context['unit_uom']
        elif sticky_case:
            context['uom'] = 'CS'
        else:
            context['uom'] = context['unit_uom']
        if context['uom'] == 'CS' and row.units_ordered and not row.cases_ordered:
            context['uom'] = context['unit_uom']

        if batch.order_quantities_known and not row.cases_ordered and not row.units_ordered:
            warn = True
            if batch.is_truck_dump_parent() and row.product:
                uuids = [child.uuid for child in batch.truck_dump_children]
                if uuids:
                    count = self.Session.query(model.PurchaseBatchRow)\
                                        .filter(model.PurchaseBatchRow.batch_uuid.in_(uuids))\
                                        .filter(model.PurchaseBatchRow.product == row.product)\
                                        .count()
                    if count:
                        warn = False
            if warn:
                self.request.session.flash("This item was NOT on the original purchase order.", 'receiving-warning')
        return self.render_to_response('view_row', context, mobile=True)

    def mobile_receive_row(self):
        """
        Mobile view for row-level receiving.
        """
        self.mobile = True
        self.viewing = True
        row = self.get_row_instance()
        batch = row.batch
        permission_prefix = self.get_permission_prefix()
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'batch': batch,
            'parent_instance': batch,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': self.get_row_image_url(row),
            'form': form,
            'allow_expired': self.handler.allow_expired_credits(),
            'allow_cases': self.handler.allow_cases(),
            'quick_receive': False,
            'quick_receive_all': False,
        }

        context['quick_receive'] = self.rattail_config.getbool('rattail.batch', 'purchase.mobile_quick_receive',
                                                               default=True)
        if batch.order_quantities_known:
            context['quick_receive_all'] = self.rattail_config.getbool('rattail.batch', 'purchase.mobile_quick_receive_all',
                                                                       default=False)

        if self.request.has_perm('{}.create_row'.format(permission_prefix)):
            schema = MobileReceivingForm().bind(session=self.Session())
            update_form = forms.Form(schema=schema, request=self.request)
            if update_form.validate(newstyle=True):
                row = self.Session.query(model.PurchaseBatchRow).get(update_form.validated['row'])
                mode = update_form.validated['mode']
                cases = update_form.validated['cases']
                units = update_form.validated['units']

                # handler takes care of the row receiving logic for us
                kwargs = dict(update_form.validated)
                del kwargs['row']
                self.handler.receive_row(row, **kwargs)

                # keep track of last-used uom, although we just track
                # whether or not it was 'CS' since the unit_uom can vary
                sticky_case = None
                if not update_form.validated['quick_receive']:
                    if cases and not units:
                        sticky_case = True
                    elif units and not cases:
                        sticky_case = False
                if sticky_case is not None:
                    self.request.session['tailbone.mobile.receiving.sticky_uom_is_case'] = sticky_case

                return self.redirect(self.get_action_url('view', batch, mobile=True))

        # unit_uom can vary by product
        context['unit_uom'] = 'LB' if row.product and row.product.weighed else 'EA'

        if context['quick_receive'] and context['quick_receive_all']:
            if context['allow_cases']:
                context['quick_receive_uom'] = 'CS'
                raise NotImplementedError("TODO: add CS support for quick_receive_all")
            else:
                context['quick_receive_uom'] = context['unit_uom']
                accounted_for = self.handler.get_units_accounted_for(row)
                remainder = self.handler.get_units_ordered(row) - accounted_for

                if accounted_for:
                    # some product accounted for; button should receive "remainder" only
                    if remainder:
                        remainder = pretty_quantity(remainder)
                        context['quick_receive_quantity'] = remainder
                        context['quick_receive_text'] = "Receive Remainder ({} {})".format(remainder, context['unit_uom'])
                    else:
                        # unless there is no remainder, in which case disable it
                        context['quick_receive'] = False

                else: # nothing yet accounted for, button should receive "all"
                    if not remainder:
                        raise ValueError("why is remainder empty?")
                    remainder = pretty_quantity(remainder)
                    context['quick_receive_quantity'] = remainder
                    context['quick_receive_text'] = "Receive ALL ({} {})".format(remainder, context['unit_uom'])

        # effective uom can vary in a few ways...the basic default is 'CS' if
        # self.default_uom_is_case is true, otherwise whatever unit_uom is.
        sticky_case = self.request.session.get('tailbone.mobile.receiving.sticky_uom_is_case')
        if sticky_case is None:
            context['uom'] = 'CS' if self.default_uom_is_case else context['unit_uom']
        elif sticky_case:
            context['uom'] = 'CS'
        else:
            context['uom'] = context['unit_uom']
        if context['uom'] == 'CS' and row.units_ordered and not row.cases_ordered:
            context['uom'] = context['unit_uom']

        if batch.order_quantities_known and not row.cases_ordered and not row.units_ordered:
            warn = True
            if batch.is_truck_dump_parent() and row.product:
                uuids = [child.uuid for child in batch.truck_dump_children]
                if uuids:
                    count = self.Session.query(model.PurchaseBatchRow)\
                                        .filter(model.PurchaseBatchRow.batch_uuid.in_(uuids))\
                                        .filter(model.PurchaseBatchRow.product == row.product)\
                                        .count()
                    if count:
                        warn = False
            if warn:
                self.request.session.flash("This item was NOT on the original purchase order.", 'receiving-warning')

        # maybe alert user if they've already received some of this product
        alert_received = self.rattail_config.getbool('tailbone', 'receiving.alert_already_received',
                                                     default=False)
        if alert_received:
            if self.handler.get_units_confirmed(row):
                msg = "You have already received some of this product; last update was {}.".format(
                    humanize.naturaltime(make_utc() - row.modified))
                self.request.session.flash(msg, 'receiving-warning')

        return self.render_to_response('receive_row', context, mobile=True)

    def auto_receive(self):
        """
        View which can "auto-receive" all items in the batch.  Meant only as a
        convenience for developers.
        """
        batch = self.get_instance()
        key = '{}.receive_all'.format(self.get_grid_key())
        progress = SessionProgress(self.request, key)
        kwargs = {'progress': progress}
        thread = Thread(target=self.auto_receive_thread, args=(batch.uuid, self.request.user.uuid), kwargs=kwargs)
        thread.start()

        return self.render_progress(progress, {
            'instance': batch,
            'cancel_url': self.get_action_url('view', batch),
            'cancel_msg': "Auto-receive was canceled",
        })

    def auto_receive_thread(self, uuid, user_uuid, progress=None):
        """
        Thread target for receiving all items on the given batch.
        """
        session = RattailSession()
        batch = session.query(model.PurchaseBatch).get(uuid)
        user = session.query(model.User).get(user_uuid)
        try:
            self.handler.auto_receive_all_items(batch, progress=progress)

        # if anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("auto-receive failed for: %s".format(batch))
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Auto-receive failed: {}: {}".format(
                    type(error).__name__, error)
                progress.session.save()

        # if no error, check result flag (false means user canceled)
        else:
            session.commit()
            session.refresh(batch)
            success_url = self.get_action_url('view', batch)
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                progress.session.save()

    @classmethod
    def _receiving_defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        model_key = cls.get_model_key()
        permission_prefix = cls.get_permission_prefix()

        # row-level receiving
        config.add_route('{}.receive_row'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}/receive'.format(url_prefix))
        config.add_view(cls, attr='receive_row', route_name='{}.receive_row'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix))
        config.add_route('mobile.{}.receive_row'.format(route_prefix), '/mobile{}/{{uuid}}/rows/{{row_uuid}}/receive'.format(url_prefix))
        config.add_view(cls, attr='mobile_receive_row', route_name='mobile.{}.receive_row'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix))

        # declare credit for row
        config.add_route('{}.declare_credit'.format(route_prefix), '{}/{{uuid}}/rows/{{row_uuid}}/declare-credit'.format(url_prefix))
        config.add_view(cls, attr='declare_credit', route_name='{}.declare_credit'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix))

        if cls.allow_truck_dump:

            # add TD child batch, from invoice file
            config.add_route('{}.add_child_from_invoice'.format(route_prefix), '{}/{{{}}}/add-child-from-invoice'.format(url_prefix, model_key))
            config.add_view(cls, attr='add_child_from_invoice', route_name='{}.add_child_from_invoice'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

            # transform TD parent row from "pack" to "unit" item
            config.add_route('{}.transform_unit_row'.format(route_prefix), '{}/{{{}}}/transform-unit'.format(url_prefix, model_key))
            config.add_view(cls, attr='transform_unit_row', route_name='{}.transform_unit_row'.format(route_prefix),
                            permission='{}.edit_row'.format(permission_prefix), renderer='json')

            # auto-receive all items
            if not rattail_config.production():
                config.add_route('{}.auto_receive'.format(route_prefix), '{}/{{{}}}/auto-receive'.format(url_prefix, model_key),
                                 request_method='POST')
                config.add_view(cls, attr='auto_receive', route_name='{}.auto_receive'.format(route_prefix),
                                permission='admin')


    @classmethod
    def defaults(cls, config):
        cls._receiving_defaults(config)
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)


# TODO: this is a stopgap measure to fix an obvious bug, which exists when the
# session is not provided by the view at runtime (i.e. when it was instead
# being provided by the type instance, which was created upon app startup).
@colander.deferred
def valid_vendor(node, kw):
    session = kw['session']
    def validate(node, value):
        vendor = session.query(model.Vendor).get(value)
        if not vendor:
            raise colander.Invalid(node, "Vendor not found")
        return vendor.uuid
    return validate


class MobileNewReceivingBatch(colander.MappingSchema):

    vendor = colander.SchemaNode(colander.String(),
                                 validator=valid_vendor)

    workflow = colander.SchemaNode(colander.String(),
                                   validator=colander.OneOf([
                                       'from_po',
                                       'from_scratch',
                                       'truck_dump',
                                   ]))

    phase = colander.SchemaNode(colander.Int())


class MobileNewReceivingFromPO(colander.MappingSchema):

    purchase = colander.SchemaNode(colander.String())


# TODO: this is a stopgap measure to fix an obvious bug, which exists when the
# session is not provided by the view at runtime (i.e. when it was instead
# being provided by the type instance, which was created upon app startup).
@colander.deferred
def valid_purchase_batch_row(node, kw):
    session = kw['session']
    def validate(node, value):
        row = session.query(model.PurchaseBatchRow).get(value)
        if not row:
            raise colander.Invalid(node, "Batch row not found")
        if row.batch.executed:
            raise colander.Invalid(node, "Batch has already been executed")
        return row.uuid
    return validate


class ReceiveRowForm(colander.MappingSchema):

    mode = colander.SchemaNode(colander.String(),
                               validator=colander.OneOf([
                                   'received',
                                   'damaged',
                                   'expired',
                                   # 'mispick',
                               ]))

    quantity = forms.types.ProductQuantity()

    expiration_date = colander.SchemaNode(colander.Date(),
                                          widget=dfwidget.TextInputWidget(),
                                          missing=colander.null)

    quick_receive = colander.SchemaNode(colander.Boolean())


class DeclareCreditForm(colander.MappingSchema):

    credit_type = colander.SchemaNode(colander.String(),
                                      validator=colander.OneOf([
                                          'damaged',
                                          'expired',
                                          # 'mispick',
                                      ]))

    quantity = forms.types.ProductQuantity()

    expiration_date = colander.SchemaNode(colander.Date(),
                                          widget=dfwidget.TextInputWidget(),
                                          missing=colander.null)


class MobileReceivingForm(colander.MappingSchema):

    row = colander.SchemaNode(colander.String(),
                              validator=valid_purchase_batch_row)

    mode = colander.SchemaNode(colander.String(),
                               validator=colander.OneOf([
                                   'received',
                                   'damaged',
                                   'expired',
                                   # 'mispick',
                               ]))

    cases = colander.SchemaNode(colander.Decimal(), missing=None)

    units = colander.SchemaNode(colander.Decimal(), missing=None)

    expiration_date = colander.SchemaNode(colander.Date(),
                                          widget=dfwidget.TextInputWidget(),
                                          missing=colander.null)

    quick_receive = colander.SchemaNode(colander.Boolean())


def includeme(config):
    ReceivingBatchView.defaults(config)
