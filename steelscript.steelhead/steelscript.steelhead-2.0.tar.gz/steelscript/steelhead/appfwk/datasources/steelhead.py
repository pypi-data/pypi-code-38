# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import copy
import pandas
import logging

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from tagging.models import Tag

from steelscript.common.interaction.model import Model
from steelscript.common.interaction.action import Action
from steelscript.appfwk.apps.jobs import QueryComplete, QueryContinue, \
    QueryError
from steelscript.appfwk.apps.datasource.models import DatasourceTable, \
    TableQueryBase, Table
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.datasource.models import TableField
from steelscript.cmdline.cli import CLIMode
from steelscript.appfwk.libs.fields import Function
from steelscript.appfwk.apps.devices.models import Device
from steelscript.appfwk.apps.datasource.modules.analysis import \
    AnalysisQuery, AnalysisTable, AnalysisException
from steelscript.appfwk.apps.jobs.models import Job

logger = logging.getLogger(__name__)


def tag_selection_preprocess(form, field, field_kwargs, params):

    tags = Tag.objects.all()
    if not tags:
        choices = [('', '<No device tags available>')]
    else:
        choices = [(t.id, t.name) for t in tags]

    field_kwargs['choices'] = choices


def fields_add_device_tag(obj, keyword='tag', label='Tag'):
    field = TableField(keyword=keyword, label=label,
                       field_cls=forms.ChoiceField,
                       pre_process_func=Function(tag_selection_preprocess,
                                                 {}))
    field.save()
    obj.fields.add(field)


def fields_add_command(obj):

    field = TableField(keyword='command', label='Command',
                       field_cls=forms.CharField)
    field.save()
    obj.fields.add(field)


class SteelHeadTable(DatasourceTable):
    class Meta:
        proxy = True
        app_label = 'steelscript.steelhead.appfwk'

    _query_class = 'SteelHeadQuery'

    def post_process_table(self, field_options):
        fields_add_device_selection(self, keyword='steelhead_device',
                                    label='SteelHead', module='steelhead',
                                    enabled=True)


class SteelHeadQuery(TableQueryBase):

    def run(self):

        obj_class = self.table.options.obj_class
        feature = self.table.options.feature
        method = self.table.options.method
        args = self.table.options.args

        sh = DeviceManager.get_device(self.job.criteria.steelhead_device)
        obj = obj_class.get(sh, feature=feature)
        res = getattr(obj, method)(*args)

        if not isinstance(res, list):
            res = [res]

        for e in res:
            for k, v in e.iteritems():
                e[k] = str(v)

        return QueryComplete(res)


class ProductInfoTable(SteelHeadTable):

    class Meta:
        proxy = True
        app_label = 'steelscript.steelhead.appfwk'

    TABLE_OPTIONS = {'obj_class': Action,
                     'feature': 'common',
                     'method': 'get_product_info',
                     'args': []}


class InterfacesTable(SteelHeadTable):

    class Meta:
        proxy = True
        app_label = 'steelscript.steelhead.appfwk'

    TABLE_OPTIONS = {'obj_class': Model,
                     'feature': 'networking',
                     'method': 'show_interfaces',
                     'args': ['brief']}


class FlowsTable(SteelHeadTable):
    class Meta:
        proxy = True
        app_label = 'steelscript.steelhead.appfwk'

    _query_class = 'FlowsQuery'


class FlowsQuery(TableQueryBase):

    def run(self):
        sh = DeviceManager.get_device(self.job.criteria.steelhead_device)

        flows = Model.get(sh, feature='flows')
        res = flows.show_flows('all')

        for k, v in res['flows_summary'].iteritems():
            v['category'] = k

        return QueryComplete(res['flows_summary'].values())


class BandwidthTable(SteelHeadTable):
    class Meta:
        proxy = True
        app_label = 'steelscript.steelhead.appfwk'

    _query_class = 'BandwidthQuery'

    def post_process_table(self, field_options):
        super(BandwidthTable, self).post_process_table(field_options)

        durations = [('1min', '1 minute'), ('5min', '5 minutes'),
                     ('hour', '1 hour'), ('day', '1 day'),
                     ('week', '1 week'), ('month', '1 month')]

        field = TableField(keyword='duration',
                           label='Bandwidth Stats Duration',
                           field_cls=forms.ChoiceField,
                           field_kwargs={'choices': durations},
                           initial='5min'
                           )
        field.save()
        self.fields.add(field)


class BandwidthQuery(TableQueryBase):

    def run(self):

        sh = DeviceManager.get_device(self.job.criteria.steelhead_device)

        stats = Model.get(sh, feature='stats')
        duration = self.job.criteria.duration
        directions = ['lan-to-wan', 'wan-to-lan', 'bi-directional']

        total = []
        for d in directions:
            res = stats.show_stats_bandwidth('all', d, duration)
            res['direction'] = d
            total.append(res)

        return QueryComplete(total)


class SteelHeadCommandTable(DatasourceTable):
    class Meta:
        proxy = True
        app_label = 'steelscript.steelhead.appfwk'

    _query_class = 'SteelHeadCommandQuery'

    def post_process_table(self, field_options):
        super(SteelHeadCommandTable, self).post_process_table(field_options)

        self.add_column('dev_name', datatype='string')
        self.add_column('output', datatype='string')


class SteelHeadCommandQuery(TableQueryBase):

    def run(self):

        sh_db = self.job.criteria.dev

        cmd = self.job.criteria.command

        sh = DeviceManager.get_device(sh_db.id)
        output = sh.cli.exec_command(cmd, mode=CLIMode.ENABLE)

        return QueryComplete([dict(dev_name=sh_db.name, output=output)])


class BatchSteelHeadTable(AnalysisTable):
    class Meta:
        proxy = True
        app_label = 'steelscript.steelhead.appfwk'

    _query_class = 'BatchSteelHeadQuery'

    @classmethod
    def create(cls, name, **kwargs):
        try:
            table = Table.objects.get(name='sh-cmd')
        except ObjectDoesNotExist:
            table = SteelHeadCommandTable.create('sh-cmd', **kwargs)

        kwargs['related_tables'] = {'base': table}

        t = super(BatchSteelHeadTable, cls).create(name, **kwargs)
        t.add_column('dev_name', 'SteelHead Name', datatype='string')
        t.add_column('output', 'Command Output', datatype='string')

        return t

    def post_process_table(self, field_options):

        fields_add_device_tag(self)
        fields_add_command(self)


class BatchSteelHeadQuery(AnalysisQuery):

    def analyze(self, jobs):

        tag = Tag.objects.get(id=self.job.criteria.tag).name

        cmd_table = Table.from_ref(
            self.table.options.related_tables['base'])

        dep_jobs = {}

        for sh_db in Device.objects.filter_by_tag(tag, module='steelhead',
                                                  enabled=True):
            criteria = copy.copy(self.job.criteria)
            criteria.dev = sh_db
            job = Job.create(table=cmd_table, criteria=criteria,
                             parent=self.job)
            dep_jobs[job.id] = job

        if not dep_jobs:
            return QueryError("No enabled steelhead "
                              "devices found with tag '{}'".format(tag))

        return QueryContinue(self.collect, jobs=dep_jobs)

    def collect(self, jobs=None):
        dfs = []

        for jid, job in jobs.iteritems():
            if job.status == Job.ERROR:
                raise AnalysisException(
                    "Job for host '{}' failed: {}".format(
                        job.criteria.dev.name, job.message))

            subdf = job.data()
            if subdf is None:
                continue
            dfs.append(subdf)

        if not dfs:
            return QueryComplete(None)

        df = pandas.concat(dfs, ignore_index=True)

        def break_line(s):
            return s.replace('\n', '<br>')

        df['output'] = df['output'].apply(break_line)

        return QueryComplete(df)
