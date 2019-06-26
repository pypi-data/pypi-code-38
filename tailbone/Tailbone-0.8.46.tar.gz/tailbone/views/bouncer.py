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
Views for Email Bounces
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime

import six

from rattail.db import model
from rattail.bouncer import get_handler
from rattail.bouncer.config import get_profile_keys

from pyramid.response import FileResponse
from webhelpers2.html import HTML, tags

from tailbone import grids
from tailbone.views import MasterView


class EmailBouncesView(MasterView):
    """
    Master view for email bounces.
    """
    model_class = model.EmailBounce
    model_title_plural = "Email Bounces"
    url_prefix = '/email-bounces'
    creatable = False
    editable = False

    labels = {
        'config_key': "Source",
        'bounce_recipient_address': "Bounced To",
        'intended_recipient_address': "Intended For",
    }

    grid_columns = [
        'config_key',
        'bounced',
        'bounce_recipient_address',
        'intended_recipient_address',
        'processed_by',
    ]

    def __init__(self, request):
        super(EmailBouncesView, self).__init__(request)
        self.handler_options = sorted(get_profile_keys(self.rattail_config))

    def get_handler(self, bounce):
        return get_handler(self.rattail_config, bounce.config_key)

    def configure_grid(self, g):
        super(EmailBouncesView, self).configure_grid(g)

        g.joiners['processed_by'] = lambda q: q.outerjoin(model.User)
        g.filters['config_key'].default_active = True
        g.filters['config_key'].default_verb = 'equal'

        g.filters['config_key'].set_value_renderer(grids.filters.ChoiceValueRenderer(self.handler_options))
        g.filters['processed'].default_active = True
        g.filters['processed'].default_verb = 'is_null'
        g.filters['processed_by'] = g.make_filter('processed_by', model.User.username)
        g.sorters['processed_by'] = g.make_sorter(model.User.username)
        g.set_sort_defaults('bounced', 'desc')

        g.set_label('config_key', "Source")
        g.set_label('bounce_recipient_address', "Bounced To")
        g.set_label('intended_recipient_address', "Intended For")

        g.set_link('bounced')
        g.set_link('intended_recipient_address')

    def configure_form(self, f):
        super(EmailBouncesView, self).configure_form(f)
        bounce = f.model_instance
        f.set_renderer('message', self.render_message_file)
        f.set_renderer('links', self.render_links)
        f.fields = [
            'config_key',
            'message',
            'bounced',
            'bounce_recipient_address',
            'intended_recipient_address',
            'links',
            'processed',
            'processed_by',
        ]
        if not bounce.processed:
            f.remove_field('processed')
            f.remove_field('processed_by')

    def render_links(self, bounce, field):
        handler = self.get_handler(bounce)
        value = list(handler.make_links(self.Session(), bounce.intended_recipient_address))
        if not value:
            return "n/a"

        links = []
        for link in value:
            label = HTML.literal("{}:&nbsp; ".format(link.type))
            anchor = tags.link_to(link.title, link.url, target='_blank')
            links.append(HTML.tag('li', label + anchor))

        return HTML.tag('ul', HTML.literal('').join(links))

    def render_message_file(self, bounce, field):
        handler = self.get_handler(bounce)
        path = handler.msgpath(bounce)
        if not path:
            return ""

        url = self.get_action_url('download', bounce)
        return self.render_file_field(path, url)

    def template_kwargs_view(self, **kwargs):
        bounce = kwargs['instance']
        kwargs['bounce'] = bounce
        handler = self.get_handler(bounce)
        kwargs['handler'] = handler
        path = handler.msgpath(bounce)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                kwargs['message'] = f.read()
        else:
            kwargs['message'] = "(file not found)"
        return kwargs

    def process(self):
        """
        View for marking a bounce as processed.
        """
        bounce = self.get_instance()
        bounce.processed = datetime.datetime.utcnow()
        bounce.processed_by = self.request.user
        self.request.session.flash("Email bounce has been marked processed.")
        return self.redirect(self.request.route_url('emailbounces'))

    def unprocess(self):
        """
        View for marking a bounce as *unprocessed*.
        """
        bounce = self.get_instance()
        bounce.processed = None
        bounce.processed_by = None
        self.request.session.flash("Email bounce has been marked UN-processed.")
        return self.redirect(self.request.route_url('emailbounces'))

    def download(self):
        """
        View for downloading the message file associated with a bounce.
        """
        bounce = self.get_instance()
        handler = self.get_handler(bounce)
        path = handler.msgpath(bounce)
        response = FileResponse(path, request=self.request)
        response.headers[b'Content-Length'] = six.binary_type(os.path.getsize(path))
        response.headers[b'Content-Disposition'] = b'attachment; filename="bounce.eml"'
        return response

    @classmethod
    def defaults(cls, config):

        config.add_tailbone_permission_group('emailbounces', "Email Bounces", overwrite=False)

        # mark bounce as processed
        config.add_route('emailbounces.process', '/email-bounces/{uuid}/process')
        config.add_view(cls, attr='process', route_name='emailbounces.process',
                        permission='emailbounces.process')
        config.add_tailbone_permission('emailbounces', 'emailbounces.process',
                                       "Mark Email Bounce as processed")

        # mark bounce as *not* processed
        config.add_route('emailbounces.unprocess', '/email-bounces/{uuid}/unprocess')
        config.add_view(cls, attr='unprocess', route_name='emailbounces.unprocess',
                        permission='emailbounces.unprocess')
        config.add_tailbone_permission('emailbounces', 'emailbounces.unprocess',
                                       "Mark Email Bounce as UN-processed")

        # download raw email
        config.add_route('emailbounces.download', '/email-bounces/{uuid}/download')
        config.add_view(cls, attr='download', route_name='emailbounces.download',
                        permission='emailbounces.download')
        config.add_tailbone_permission('emailbounces', 'emailbounces.download',
                                       "Download raw message of Email Bounce")

        cls._defaults(config)


def includeme(config):
    EmailBouncesView.defaults(config)
