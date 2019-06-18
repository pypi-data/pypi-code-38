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
Views for tempmon probes
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six

from rattail.time import make_utc, localtime
from rattail_tempmon.db import model as tempmon

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags, HTML

from tailbone import forms, grids
from tailbone.views.tempmon import MasterView
from tailbone.util import raw_datetime


class TempmonProbeView(MasterView):
    """
    Master view for tempmon probes.
    """
    model_class = tempmon.Probe
    model_title = "TempMon Probe"
    model_title_plural = "TempMon Probes"
    route_prefix = 'tempmon.probes'
    url_prefix = '/tempmon/probes'

    has_rows = True
    model_row_class = tempmon.Reading

    labels = {
        'critical_max_timeout': "Critical High Timeout",
        'good_max_timeout': "High Timeout",
        'good_min_timeout': "Low Timeout",
        'critical_min_timeout': "Critical Low Timeout",
    }

    grid_columns = [
        'client',
        'config_key',
        'appliance',
        'appliance_type',
        'description',
        'device_path',
        'enabled',
        'status',
    ]

    form_fields = [
        'client',
        'config_key',
        'appliance',
        'appliance_type',
        'description',
        'location',
        'device_path',
        'critical_temp_max',
        'critical_max_timeout',
        'good_temp_max',
        'good_max_timeout',
        'good_temp_min',
        'good_min_timeout',
        'critical_temp_min',
        'critical_min_timeout',
        'error_timeout',
        'therm_status_timeout',
        'status_alert_timeout',
        'notes',
        'enabled',
        'status',
    ]

    row_grid_columns = [
        'degrees_f',
        'taken',
    ]

    def configure_grid(self, g):
        super(TempmonProbeView, self).configure_grid(g)

        g.joiners['client'] = lambda q: q.join(tempmon.Client)
        g.sorters['client'] = g.make_sorter(tempmon.Client.config_key)
        g.set_sort_defaults('client')

        g.set_enum('appliance_type', self.enum.TEMPMON_APPLIANCE_TYPE)
        g.set_enum('status', self.enum.TEMPMON_PROBE_STATUS)

        g.set_renderer('enabled', self.render_enabled_grid)

        g.set_label('config_key', "Key")

        g.set_link('client')
        g.set_link('config_key')
        g.set_link('description')

    def render_enabled_grid(self, probe, field):
        if probe.enabled:
            return "Yes"
        return "No"

    def configure_form(self, f):
        super(TempmonProbeView, self).configure_form(f)

        # config_key
        f.set_validator('config_key', self.unique_config_key)

        # client
        f.set_renderer('client', self.render_client)
        f.set_label('client', "Tempmon Client")
        if self.creating or self.editing:
            f.replace('client', 'client_uuid')
            clients = self.Session.query(tempmon.Client)
            if self.creating:
                clients = clients.filter(tempmon.Client.archived == False)
            clients = clients.order_by(tempmon.Client.config_key)
            client_values = [(client.uuid, "{} ({})".format(client.config_key, client.hostname))
                             for client in clients]
            f.set_widget('client_uuid', dfwidget.SelectWidget(values=client_values))
            f.set_label('client_uuid', "Tempmon Client")

        # appliance
        f.set_renderer('appliance', self.render_appliance)
        if self.creating or self.editing:
            f.replace('appliance', 'appliance_uuid')
            appliances = self.Session.query(tempmon.Appliance)\
                                     .order_by(tempmon.Appliance.name)
            appliance_values = [(appliance.uuid, appliance.name)
                                for appliance in appliances]
            appliance_values.insert(0, ('', "(none)"))
            f.set_widget('appliance_uuid', dfwidget.SelectWidget(values=appliance_values))
            f.set_label('appliance_uuid', "Appliance")

        # appliance_type
        f.set_enum('appliance_type', self.enum.TEMPMON_APPLIANCE_TYPE)

        # therm_status_timeout
        f.set_helptext('therm_status_timeout', tempmon.Probe.therm_status_timeout.__doc__)

        # status_alert_timeout
        f.set_helptext('status_alert_timeout', tempmon.Probe.status_alert_timeout.__doc__)

        # notes
        f.set_type('notes', 'text')

        # status
        f.set_enum('status', self.enum.TEMPMON_PROBE_STATUS)
        if self.creating or self.editing:
            f.remove_fields('status')

        # enabled
        if self.creating or self.editing:
            f.set_node('enabled', forms.types.DateTimeBoolean())
        else:
            f.set_renderer('enabled', self.render_enabled_form)
        f.set_helptext('enabled', tempmon.Probe.enabled.__doc__)

    def objectify(self, form, data=None):

        # this is a hack to prevent updates to the 'enabled' timestamp, when
        # simple edits are being done to the probe.  i.e. we do want to set the
        # timestamp when it was previously null, but not otherwise.
        if self.editing:
            data = dict(data or form.validated)
            if data['enabled'] and form.model_instance.enabled:
                data['enabled'] = form.model_instance.enabled

        return super(TempmonProbeView, self).objectify(form, data=data)

    def unique_config_key(self, node, value):
        query = self.Session.query(tempmon.Probe)\
                            .filter(tempmon.Probe.config_key == value)
        if self.editing:
            probe = self.get_instance()
            query = query.filter(tempmon.Probe.uuid != probe.uuid)
        if query.count():
            raise colander.Invalid(node, "Config key must be unique")

    def render_client(self, probe, field):
        client = probe.client
        if not client:
            return ""
        text = six.text_type(client)
        url = self.request.route_url('tempmon.clients.view', uuid=client.uuid)
        return tags.link_to(text, url)

    def render_appliance(self, probe, field):
        appliance = probe.appliance
        if not appliance:
            return ""
        text = six.text_type(appliance)
        url = self.request.route_url('tempmon.appliances.view', uuid=appliance.uuid)
        return tags.link_to(text, url)

    def render_enabled_form(self, probe, field):
        if probe.enabled:
            return raw_datetime(self.rattail_config, probe.enabled)
        return "No"

    def delete_instance(self, probe):
        # bulk-delete all readings first
        readings = self.Session.query(tempmon.Reading)\
                               .filter(tempmon.Reading.probe == probe)
        readings.delete(synchronize_session=False)
        self.Session.flush()
        self.Session.refresh(probe)

        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        self.Session.delete(probe)
        self.Session.flush()

    def get_row_data(self, probe):
        query = self.Session.query(tempmon.Reading)\
                            .filter(tempmon.Reading.probe == probe)
        return query

    def get_parent(self, reading):
        return reading.client

    def configure_row_grid(self, g):
        super(TempmonProbeView, self).configure_row_grid(g)

        # # probe
        # g.set_filter('probe', tempmon.Probe.description)
        # g.set_sorter('probe', tempmon.Probe.description)

        g.set_sort_defaults('taken', 'desc')

    def graph(self):
        probe = self.get_instance()
        use_buefy = self.get_use_buefy()

        key = 'tempmon.probe.{}.graph_time_range'.format(probe.uuid)
        selected = self.request.params.get('time-range')
        if not selected:
            selected = self.request.session.get(key, 'last hour')
        self.request.session[key] = selected

        range_options = tags.Options([
            tags.Option("Last Hour", 'last hour'),
            tags.Option("Last 6 Hours", 'last 6 hours'),
            tags.Option("Last Day", 'last day'),
            tags.Option("Last Week", 'last week'),
        ])

        if use_buefy:
            time_range = HTML.tag('b-select', c=[range_options.render()],
                                  **{'v-model': 'currentTimeRange',
                                     '@input': 'timeRangeChanged'})
        else:
            time_range = tags.select('time-range', selected, range_options)

        context = {
            'probe': probe,
            'parent_title': six.text_type(probe),
            'parent_url': self.get_action_url('view', probe),
            'time_range': time_range,
            'current_time_range': selected,
        }
        return self.render_to_response('graph', context)

    def graph_readings(self):
        probe = self.get_instance()

        key = 'tempmon.probe.{}.graph_time_range'.format(probe.uuid)
        selected = self.request.params['time-range']
        assert selected
        self.request.session[key] = selected

        # figure out what our window of time is
        if selected == 'last hour':
            cutoff = 60 * 60            # seconds x minutes
        elif selected == 'last 6 hours':
            cutoff = 60 * 60 * 6        # hour x 6
        elif selected == 'last day':
            cutoff = 60 * 60 * 24       # hour x 24
        elif selected == 'last week':
            cutoff = 60 * 60 * 24 * 7   # day x 7
        else:
            raise NotImplementedError("Unknown time range: {}".format(selected))

        # figure out which readings we need to graph
        cutoff = make_utc() - datetime.timedelta(seconds=cutoff)
        readings = self.Session.query(tempmon.Reading)\
                               .filter(tempmon.Reading.probe == probe)\
                               .filter(tempmon.Reading.taken >= cutoff)\
                               .order_by(tempmon.Reading.taken)\
                               .all()

        # convert readings to data for scatter plot
        data = [{
            'x': localtime(self.rattail_config, reading.taken, from_utc=True).isoformat(),
            'y': float(reading.degrees_f),
        } for reading in readings]
        return data

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        model_key = cls.get_model_key()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # graph
        config.add_route('{}.graph'.format(route_prefix), '{}/{{{}}}/graph'.format(url_prefix, model_key),
                         request_method='GET')
        config.add_view(cls, attr='graph', route_name='{}.graph'.format(route_prefix),
                        permission='{}.view'.format(permission_prefix))

        # graph_readings
        config.add_route('{}.graph_readings'.format(route_prefix), '{}/{{{}}}/graph-readings'.format(url_prefix, model_key),
                         request_method='GET')
        config.add_view(cls, attr='graph_readings', route_name='{}.graph_readings'.format(route_prefix),
                        permission='{}.view'.format(permission_prefix), renderer='json')

        cls._defaults(config)


def includeme(config):
    TempmonProbeView.defaults(config)
