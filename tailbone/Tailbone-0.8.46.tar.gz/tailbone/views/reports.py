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
Reporting views
"""

from __future__ import unicode_literals, absolute_import

import re
import datetime
import logging

import six

import rattail
from rattail.db import model, Session as RattailSession
from rattail.files import resource_path
from rattail.time import localtime
from rattail.reporting import get_report_handler
from rattail.threads import Thread

import colander
from mako.template import Template
from pyramid.response import Response
from webhelpers2.html import HTML

from tailbone import forms, grids
from tailbone.db import Session
from tailbone.views import View
from tailbone.views.exports import ExportMasterView
from tailbone.progress import SessionProgress


plu_upc_pattern = re.compile(r'^000000000(\d{5})$')
weighted_upc_pattern = re.compile(r'^002(\d{5})00000\d$')

log = logging.getLogger(__name__)


def get_upc(product):
    """
    UPC formatter.  Strips PLUs to bare number, and adds "minus check digit"
    for non-PLU UPCs.
    """
    upc = six.text_type(product.upc)
    m = plu_upc_pattern.match(upc)
    if m:
        return six.text_type(int(m.group(1)))
    m = weighted_upc_pattern.match(upc)
    if m:
        return six.text_type(int(m.group(1)))
    return '{0}-{1}'.format(upc[:-1], upc[-1])


class OrderingWorksheet(View):
    """
    This is the "Ordering Worksheet" report.
    """

    report_template_path = 'tailbone:reports/ordering_worksheet.mako'

    upc_getter = staticmethod(get_upc)

    def __call__(self):
        if self.request.params.get('vendor'):
            vendor = Session.query(model.Vendor).get(self.request.params['vendor'])
            if vendor:
                departments = []
                uuids = self.request.params.get('departments')
                if uuids:
                    for uuid in uuids.split(','):
                        dept = Session.query(model.Department).get(uuid)
                        if dept:
                            departments.append(dept)
                preferred_only = self.request.params.get('preferred_only') == '1'
                body = self.write_report(vendor, departments, preferred_only)
                response = Response(content_type='text/html')
                response.headers['Content-Length'] = len(body)
                response.headers['Content-Disposition'] = 'attachment; filename=ordering.html'
                response.text = body
                return response
        return {}

    def write_report(self, vendor, departments, preferred_only):
        """
        Rendering engine for the ordering worksheet report.
        """

        q = Session.query(model.ProductCost)
        q = q.join(model.Product)
        q = q.filter(model.Product.deleted == False)
        q = q.filter(model.ProductCost.vendor == vendor)
        q = q.filter(model.Product.department_uuid.in_([x.uuid for x in departments]))
        if preferred_only:
            q = q.filter(model.ProductCost.preference == 1)

        costs = {}
        for cost in q:
            dept = cost.product.department
            subdept = cost.product.subdepartment
            costs.setdefault(dept, {})
            costs[dept].setdefault(subdept, [])
            costs[dept][subdept].append(cost)

        def cost_sort_key(cost):
            product = cost.product
            brand = product.brand.name if product.brand else ''
            key = '{0} {1}'.format(brand, product.description)
            return key

        now = localtime(self.request.rattail_config)
        data = dict(
            vendor=vendor,
            costs=costs,
            cost_sort_key=cost_sort_key,
            date=now.strftime('%a %d %b %Y'),
            time=now.strftime('%I:%M %p'),
            get_upc=self.upc_getter,
            rattail=rattail,
            )

        template_path = resource_path(self.report_template_path)
        template = Template(filename=template_path)
        return template.render(**data)


class InventoryWorksheet(View):
    """
    This is the "Inventory Worksheet" report.
    """

    report_template_path = 'tailbone:reports/inventory_worksheet.mako'

    upc_getter = staticmethod(get_upc)

    def __call__(self):
        """
        This is the "Inventory Worksheet" report.
        """

        departments = Session.query(model.Department)

        if self.request.params.get('department'):
            department = departments.get(self.request.params['department'])
            if department:
                body = self.write_report(department)
                response = Response(content_type=str('text/html'))
                response.headers[str('Content-Length')] = len(body)
                response.headers[str('Content-Disposition')] = str('attachment; filename=inventory.html')
                response.text = body
                return response

        departments = departments.order_by(model.Department.name)
        departments = departments.all()
        return{'departments': departments}

    def write_report(self, department):
        """
        Generates the Inventory Worksheet report.
        """

        def get_products(subdepartment):
            q = Session.query(model.Product)
            q = q.outerjoin(model.Brand)
            q = q.filter(model.Product.deleted == False)
            q = q.filter(model.Product.subdepartment == subdepartment)
            if self.request.params.get('weighted-only'):
                q = q.filter(model.Product.weighed == True)
            if self.request.params.get('exclude-not-for-sale'):
                q = q.filter(model.Product.not_for_sale == False)
            q = q.order_by(model.Brand.name, model.Product.description)
            return q.all()

        now = localtime(self.request.rattail_config)
        data = dict(
            date=now.strftime('%a %d %b %Y'),
            time=now.strftime('%I:%M %p'),
            department=department,
            get_products=get_products,
            get_upc=self.upc_getter,
            )

        template_path = resource_path(self.report_template_path)
        template = Template(filename=template_path)
        return template.render(**data)


class ReportOutputView(ExportMasterView):
    """
    Master view for report output
    """
    model_class = model.ReportOutput
    route_prefix = 'report_output'
    url_prefix = '/reports/generated'
    downloadable = True

    grid_columns = [
        'id',
        'report_name',
        'filename',
        'created',
        'created_by',
    ]

    form_fields = [
        'id',
        'report_name',
        'report_type',
        'params',
        'filename',
        'created',
        'created_by',
    ]

    def configure_grid(self, g):
        super(ReportOutputView, self).configure_grid(g)
        g.set_link('filename')

    def configure_form(self, f):
        super(ReportOutputView, self).configure_form(f)

        # params
        f.set_renderer('params', self.render_params)

        # filename
        if self.viewing:
            f.set_renderer('filename', self.render_download)

    def render_params(self, report, field):
        params = report.params
        if not params:
            return ""

        # TODO: should sort these, perhaps according to Report definition?
        params = [{'key': key, 'value': value}
                  for key, value in params.items()]

        route_prefix = self.get_route_prefix()
        g = grids.Grid(
            key='{}.params'.format(route_prefix),
            data=params,
            columns=['key', 'value'],
        )
        return HTML.literal(g.render_grid())

    def render_download(self, report, field):
        path = report.filepath(self.rattail_config)
        url = self.get_action_url('download', report)
        return self.render_file_field(path, url=url)

    def download(self):
        report = self.get_instance()
        path = report.filepath(self.rattail_config)
        return self.file_response(path)


class GenerateReport(View):
    """
    View for generating a new report.
    """

    def __init__(self, request):
        super(GenerateReport, self).__init__(request)
        self.handler = self.get_handler()

    def get_handler(self):
        return get_report_handler(self.rattail_config)

    def choose(self):
        """
        View which allows user to choose which type of report they wish to
        generate.
        """
        # handler is responsible for determining which report types are valid
        reports = self.handler.get_reports()

        # make form to accept user choice of report type
        schema = NewReport().bind(valid_report_types=list(reports))
        form = forms.Form(schema=schema, request=self.request)
        form.submit_label = "Continue"
        form.cancel_url = self.request.route_url('report_output')

        # TODO: should probably "group" certain reports together somehow?
        # e.g. some for customers/membership, others for product movement etc.
        values = [(r.type_key, r.name) for r in reports.values()]
        form.set_widget('report_type', forms.widgets.PlainSelectWidget(values=values,
                                                                       size=10))

        # if form validates, that means user has chosen a report type, so we
        # just redirect to the appropriate "new report" page
        if form.validate(newstyle=True):
            raise self.redirect(self.request.route_url('generate_specific_report',
                                                       type_key=form.validated['report_type']))

        return {
            'index_title': "Generate Report",
            'form': form,
            'dform': form.make_deform_form(),
            'reports': reports,
            'report_descriptions': dict([(r.type_key, r.__doc__)
                                         for r in reports.values()]),
            'use_form': self.rattail_config.getbool('tailbone', 'reporting.choosing_uses_form',
                                                    default=True),
        }

    def generate(self):
        """
        View for actually generating a new report.  Allows user to provide
        input parameters specific to the report type, then creates a new report
        and redirects user to view the output.
        """
        type_key = self.request.matchdict['type_key']
        report = self.handler.get_report(type_key)
        report_params = report.make_params(Session())

        NODE_TYPES = {
            datetime.date: colander.Date,
        }

        schema = colander.Schema()
        for param in report_params:

            # make a new node of appropriate schema type
            node_type = NODE_TYPES.get(param.type, colander.String)
            node = colander.SchemaNode(typ=node_type(), name=param.name)

            # allow empty value if param is optional
            if not param.required:
                node.missing = colander.null

            schema.add(node)

        form = forms.Form(schema=schema, request=self.request,
                          use_buefy=self.get_use_buefy())
        form.submit_label = "Generate this Report"
        form.cancel_url = self.request.route_url('generate_report')

        # must declare jquery support for date fields, ugh
        # TODO: obviously would be nice for this to be automatic?
        for param in report_params:
            if param.type is datetime.date:
                form.set_type(param.name, 'date_jquery')

        # if form validates, start generating new report output; show progress page
        if form.validate(newstyle=True):
            key = 'report_output.generate'
            progress = SessionProgress(self.request, key)
            kwargs = {'progress': progress}
            thread = Thread(target=self.generate_thread,
                            args=(report, form.validated, self.request.user.uuid),
                            kwargs=kwargs)
            thread.start()
            return self.render_progress(progress, {
                'cancel_url': self.request.route_url('report_output'),
                'cancel_msg': "Report generation was canceled",
            })

        return {
            'index_title': "Generate Report",
            'index_url': self.request.route_url('generate_report'),
            'report': report,
            'form': form,
            'dform': form.make_deform_form(),
            'use_buefy': self.get_use_buefy(),
        }

    def generate_thread(self, report, params, user_uuid, progress=None):
        """
        Generate output for the given report and params, and return the
        resulting :class:`rattail:~rattail.db.model.reports.ReportOutput`
        object.
        """
        session = RattailSession()
        user = session.query(model.User).get(user_uuid)
        try:
            output = self.handler.generate_output(session, report, params, user, progress=progress)

        # if anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("Failed to generate '%s' report: %s", report.type_key, report)
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Failed to generate report: {}: {}".format(
                    type(error).__name__, error)
                progress.session.save()

        # if no error, check result flag (false means user canceled)
        else:
            session.commit()
            success_url = self.request.route_url('report_output.view', uuid=output.uuid)
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                progress.session.save()

    @classmethod
    def defaults(cls, config):

        # note that we include this in the "Generated Reports" permissions group
        config.add_tailbone_permission('report_output', 'report_output.generate',
                                       "Generate new report (of any type)")

        # "generate report" (which is really "choose")
        config.add_route('generate_report', '/reports/generate')
        config.add_view(cls, attr='choose', route_name='generate_report',
                        permission='report_output.generate',
                        renderer='/reports/choose.mako')

        # "generate specific report" (accept custom params, truly generate)
        config.add_route('generate_specific_report', '/reports/generate/{type_key}')
        config.add_view(cls, attr='generate', route_name='generate_specific_report',
                        permission='report_output.generate',
                        renderer='/reports/generate.mako')


@colander.deferred
def valid_report_type(node, kw):
    valid_report_types = kw['valid_report_types']

    def validate(node, value):
        # we just need to provide possible values, and let core validator
        # handle the rest
        oneof = colander.OneOf(valid_report_types)
        return oneof(node, value)

    return validate


class NewReport(colander.Schema):

    report_type = colander.SchemaNode(colander.String(),
                                      validator=valid_report_type)


def add_routes(config):
    config.add_route('reports.ordering',        '/reports/ordering')
    config.add_route('reports.inventory',       '/reports/inventory')


def includeme(config):
    add_routes(config)

    config.add_view(OrderingWorksheet, route_name='reports.ordering',
                    renderer='/reports/ordering.mako')

    config.add_view(InventoryWorksheet, route_name='reports.inventory',
                    renderer='/reports/inventory.mako')

    # fix permission group
    config.add_tailbone_permission_group('report_output', "Generated Reports")

    # note that GenerateReport must come first, per route matching
    GenerateReport.defaults(config)
    ReportOutputView.defaults(config)
