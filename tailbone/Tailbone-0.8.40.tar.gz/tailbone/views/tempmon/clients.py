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
Views for tempmon clients
"""

from __future__ import unicode_literals, absolute_import

import subprocess

from rattail.config import parse_list
from rattail_tempmon.db import model as tempmon

import colander
from webhelpers2.html import HTML, tags

from tailbone import forms
from tailbone.views.tempmon import MasterView
from tailbone.util import raw_datetime


class TempmonClientView(MasterView):
    """
    Master view for tempmon clients.
    """
    model_class = tempmon.Client
    model_title = "TempMon Client"
    model_title_plural = "TempMon Clients"
    route_prefix = 'tempmon.clients'
    url_prefix = '/tempmon/clients'

    has_rows = True
    model_row_class = tempmon.Reading

    grid_columns = [
        'config_key',
        'hostname',
        'location',
        'delay',
        'enabled',
        'online',
        'archived',
    ]

    form_fields = [
        'config_key',
        'hostname',
        'location',
        'disk_type',
        'delay',
        'appliances',
        'probes',
        'notes',
        'enabled',
        'online',
        'archived',
    ]

    row_grid_columns = [
        'probe',
        'degrees_f',
        'taken',
    ]

    def configure_grid(self, g):
        super(TempmonClientView, self).configure_grid(g)

        # config_key
        g.set_label('config_key', "Key")
        g.set_sort_defaults('config_key')
        g.set_link('config_key')

        # hostname
        g.filters['hostname'].default_active = True
        g.filters['hostname'].default_verb = 'contains'
        g.set_link('hostname')

        # location
        g.filters['location'].default_active = True
        g.filters['location'].default_verb = 'contains'
        g.set_link('location')

        # disk_type
        g.set_enum('disk_type', self.enum.TEMPMON_DISK_TYPE)

        # enabled
        g.set_renderer('enabled', self.render_enabled_grid)

        # archived
        g.filters['archived'].default_active = True
        g.filters['archived'].default_verb = 'is_false'

    def render_enabled_grid(self, client, field):
        if client.enabled:
            return "Yes"
        return "No"

    def configure_form(self, f):
        super(TempmonClientView, self).configure_form(f)

        # config_key
        f.set_validator('config_key', self.unique_config_key)

        # disk_type
        f.set_enum('disk_type', self.enum.TEMPMON_DISK_TYPE)
        f.widgets['disk_type'].values.insert(0, ('', "(unknown)"))

        # delay
        f.set_helptext('delay', tempmon.Client.delay.__doc__)

        # appliances
        if self.viewing:
            f.set_renderer('appliances', self.render_appliances)
        else:
            f.remove_field('appliances')

        # probes
        if self.viewing:
            f.set_renderer('probes', self.render_probes)
        else:
            f.remove_field('probes')

        # notes
        f.set_type('notes', 'text')

        # enabled
        if self.creating or self.editing:
            f.set_node('enabled', forms.types.DateTimeBoolean())
        else:
            f.set_renderer('enabled', self.render_enabled_form)
        f.set_helptext('enabled', tempmon.Client.enabled.__doc__)

        # online
        if self.creating or self.editing:
            f.remove_field('online')
        else:
            f.set_helptext('online', tempmon.Client.online.__doc__)

        # archived
        f.set_helptext('archived', tempmon.Client.archived.__doc__)

    def objectify(self, form, data=None):

        # this is a hack to prevent updates to the 'enabled' timestamp, when
        # simple edits are being done to the client.  i.e. we do want to set
        # the timestamp when it was previously null, but not otherwise.
        if self.editing:
            data = dict(data or form.validated)
            if data['enabled'] and form.model_instance.enabled:
                data['enabled'] = form.model_instance.enabled

        return super(TempmonClientView, self).objectify(form, data=data)

    def unique_config_key(self, node, value):
        query = self.Session.query(tempmon.Client)\
                            .filter(tempmon.Client.config_key == value)
        if self.editing:
            client = self.get_instance()
            query = query.filter(tempmon.Client.uuid != client.uuid)
        if query.count():
            raise colander.Invalid(node, "Config key must be unique")

    def render_appliances(self, client, field):
        appliances = {}
        for probe in client.probes:
            if probe.appliance and probe.appliance.uuid not in appliances:
                appliances[probe.appliance.uuid] = probe.appliance

        if not appliances:
            return ""

        appliances = sorted(appliances.values(), key=lambda a: a.name)
        items = [HTML.tag('li', c=[tags.link_to(a.name, self.request.route_url('tempmon.appliances.view', uuid=a.uuid))])
                 for a in appliances]
        return HTML.tag('ul', c=items)

    def render_enabled_form(self, client, field):
        if client.enabled:
            return raw_datetime(self.rattail_config, client.enabled)
        return "No"

    def delete_instance(self, client):
        # bulk-delete all readings first
        readings = self.Session.query(tempmon.Reading)\
                               .filter(tempmon.Reading.client == client)
        readings.delete(synchronize_session=False)
        self.Session.flush()
        self.Session.refresh(client)

        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        self.Session.delete(client)
        self.Session.flush()

    def get_row_data(self, client):
        query = self.Session.query(tempmon.Reading)\
                            .join(tempmon.Probe)\
                            .filter(tempmon.Reading.client == client)
        return query

    def get_parent(self, reading):
        return reading.client

    def configure_row_grid(self, g):
        super(TempmonClientView, self).configure_row_grid(g)

        # probe
        g.set_filter('probe', tempmon.Probe.description)
        g.set_sorter('probe', tempmon.Probe.description)

        g.set_sort_defaults('taken', 'desc')

    def restartable_client(self, client):
        cmd = self.get_restart_cmd(client)
        return bool(cmd)

    def restart(self):
        client = self.get_instance()
        if self.restartable_client(client):
            try:
                subprocess.check_output(self.get_restart_cmd(client),
                                        stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as error:
                self.request.session.flash("Failed to restart client: {}".format(error.output), 'error')
            else:
                self.request.session.flash("Client has been restarted: {}".format(
                    self.get_instance_title(client)))
        else:
            self.request.session.flash("Restart not supported for client: {}".format(client), 'error')
        return self.redirect(self.get_action_url('view', client))

    def get_restart_cmd(self, client):
        name = 'rattail.tempmon.client.restart'
        cmd = self.rattail_config.get('rattail.tempmon', 'client.restart.{}'.format(client.config_key))
        if not cmd:
            cmd = self.rattail_config.get('rattail.tempmon', 'client.restart')
        if cmd:
            cmd = cmd.format(hostname=client.hostname)
            return parse_list(cmd)

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        cls._defaults(config)

        # restart tempmon client
        config.add_tailbone_permission(permission_prefix, '{}.restart'.format(permission_prefix),
                                       "Restart a {}".format(model_title))
        config.add_route('{}.restart'.format(route_prefix), '{}/{{{}}}/restart'.format(url_prefix, model_key))
        config.add_view(cls, attr='restart', route_name='{}.restart'.format(route_prefix),
                        permission='{}.restart'.format(permission_prefix))


def includeme(config):
    TempmonClientView.defaults(config)
