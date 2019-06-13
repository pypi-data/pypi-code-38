# -*- coding: utf-8; -*-
# -*- coding: utf-8; -*-
"""
Views for ${model_title} batches
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from webhelpers2.html import tags

from tailbone.views.batch import FileBatchMasterView

from .handler import ${model_name}Handler


class ${model_name}View(FileBatchMasterView):
    """
    Master view for ${model_title} batches.
    """
    model_class = model.${model_name}
    batch_handler_class = ${model_name}Handler
    model_row_class = model.${model_name}Row
    model_title = "${model_title} Batch"
    model_title_plural = "${model_title} Batches"
    route_prefix = 'batch.${model_name.lower()}s'
    url_prefix = '/batch/${table_name.replace('_', '-')}'

    form_fields = [
        'vendor',
        'filename',
        'effective',
        'created',
        'created_by',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'upc': "UPC",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'description',
        'status_code',
    ]

    def get_instance_title(self, batch):
        return six.text_type(batch.vendor)

    def configure_grid(self, g):
        super(${model_name}View, self).configure_form(f)

        # vendor
        g.set_joiner('vendor', lambda q: q.outerjoin(model.Vendor))
        g.set_filter('vendor', model.Vendor.name,
                     default_active=True, default_verb='contains')
        g.set_sorter('vendor', model.Vendor.name)

    def configure_form(self, f):
        super(${model_name}View, self).configure_form(f)

        # readonly fields
        f.set_readonly('vendor')
        f.set_readonly('effective')

        # vendor
        f.set_renderer('vendor', self.render_vendor)

    def render_vendor(self, batch, field):
        vendor = batch.vendor
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def row_grid_row_attrs(self, row, i):
        attrs = {}
        if row.status_code == row.STATUS_SOME_CONCERN:
            attrs['class_'] = 'notice'
        if row.status_code == row.STATUS_UTTER_CHAOS:
            attrs['class_'] = 'warning'
        return attrs


def includeme(config):

    # fix permission group title
    config.add_tailbone_permission_group('${model_name.lower()}s', "${model_title}s")

    ${model_name}View.defaults(config)
