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
Views for tempmon appliances
"""

from __future__ import unicode_literals, absolute_import

import os

import six
from PIL import Image

from rattail_tempmon.db import model as tempmon

import colander
from webhelpers2.html import HTML, tags

from tailbone.views.tempmon import MasterView


class TempmonApplianceView(MasterView):
    """
    Master view for tempmon appliances.
    """
    model_class = tempmon.Appliance
    model_title = "TempMon Appliance"
    model_title_plural = "TempMon Appliances"
    route_prefix = 'tempmon.appliances'
    url_prefix = '/tempmon/appliances'
    has_image = True
    has_thumbnail = True

    grid_columns = [
        'name',
        'appliance_type',
        'location',
        'image',
    ]

    form_fields = [
        'name',
        'appliance_type',
        'location',
        'clients',
        'probes',
        'image',
    ]

    def configure_grid(self, g):
        super(TempmonApplianceView, self).configure_grid(g)

        # name
        g.set_sort_defaults('name')
        g.set_link('name')

        # appliance_type
        g.set_enum('appliance_type', self.enum.TEMPMON_APPLIANCE_TYPE)
        g.set_label('appliance_type', "Type")
        g.filters['appliance_type'].label = "Appliance Type"

        # location
        g.set_link('location')

        # image
        g.set_renderer('image', self.render_grid_thumbnail)
        g.set_link('image')

    def render_grid_thumbnail(self, appliance, field):
        route_prefix = self.get_route_prefix()
        url = self.request.route_url('{}.thumbnail'.format(route_prefix), uuid=appliance.uuid)
        image = tags.image(url, "")
        helper = HTML.tag('span', class_='image-helper')
        return HTML.tag('div', class_='image-frame', c=[helper, image])

    def configure_form(self, f):
        super(TempmonApplianceView, self).configure_form(f)

        # name
        f.set_validator('name', self.unique_name)

        # appliance_type
        f.set_enum('appliance_type', self.enum.TEMPMON_APPLIANCE_TYPE)

        # image
        if self.creating or self.editing:
            f.set_type('image', 'file')
            f.set_required('image', False)
        else:
            f.set_renderer('image', self.render_image)

        # clients
        if self.viewing:
            f.set_renderer('clients', self.render_clients)
        else:
            f.remove_field('clients')

        # probes
        if self.viewing:
            f.set_renderer('probes', self.render_probes)
        elif self.creating or self.editing:
            f.remove_field('probes')

    def unique_name(self, node, value):
        query = self.Session.query(tempmon.Appliance)\
                            .filter(tempmon.Appliance.name == value)
        if self.editing:
            appliance = self.get_instance()
            query = query.filter(tempmon.Appliance.uuid != appliance.uuid)
        if query.count():
            raise colander.Invalid(node, "Name must be unique")

    def get_image_bytes(self, appliance):
        return appliance.image_normal or appliance.image_raw

    def get_thumbnail_bytes(self, appliance):
        return appliance.image_thumbnail

    def render_image(self, appliance, field):
        route_prefix = self.get_route_prefix()
        url = self.request.route_url('{}.image'.format(route_prefix), uuid=appliance.uuid)
        return tags.image(url, "Appliance Image", id='appliance-image') #, width=500) #, height=500)

    def render_clients(self, appliance, field):
        clients = {}
        for probe in appliance.probes:
            if probe.client.uuid not in clients:
                clients[probe.client.uuid] = probe.client

        if not clients:
            return ""

        clients = sorted(clients.values(), key=lambda client: client.hostname)
        items = [HTML.tag('li', c=[tags.link_to(client.hostname, self.request.route_url('tempmon.clients.view', uuid=client.uuid))])
                 for client in clients]
        return HTML.tag('ul', c=items)

    def process_uploads(self, appliance, form, uploads):
        image = uploads.pop('image', None)
        if image:

            # capture raw image as-is (note, this assumes jpeg)
            with open(image['temp_path'], 'rb') as f:
                appliance.image_raw = f.read()

            # resize image and store as separate attributes
            with open(image['temp_path'], 'rb') as f:
                im = Image.open(f)

                im.thumbnail((600, 600), Image.ANTIALIAS)
                data = six.BytesIO()
                im.save(data, 'JPEG')
                appliance.image_normal = data.getvalue()
                data.close()

                im.thumbnail((150, 150), Image.ANTIALIAS)
                data = six.BytesIO()
                im.save(data, 'JPEG')
                appliance.image_thumbnail = data.getvalue()
                data.close()

            # cleanup temp files
            os.remove(image['temp_path'])
            os.rmdir(image['tempdir'])

        if uploads:
            raise NotImplementedError("too many uploads?")


def includeme(config):
    TempmonApplianceView.defaults(config)
