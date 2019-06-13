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
Email Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail import mail
from rattail.db import api, model
from rattail.config import parse_list

import colander
from deform import widget as dfwidget
from webhelpers2.html import HTML

from tailbone.db import Session
from tailbone.views import View, MasterView


class ProfilesView(MasterView):
    """
    Master view for email admin (settings/preview).
    """
    normalized_model_name = 'emailprofile'
    model_title = "Email Setting"
    model_key = 'key'
    url_prefix = '/settings/email'
    filterable = False
    pageable = False
    creatable = False
    deletable = False

    grid_columns = [
        'key',
        'prefix',
        'subject',
        'to',
        'enabled',
    ]

    form_fields = [
        'key',
        'fallback_key',
        'description',
        'prefix',
        'subject',
        'sender',
        'replyto',
        'to',
        'cc',
        'bcc',
        'enabled',
    ]

    def __init__(self, request):
        super(ProfilesView, self).__init__(request)
        self.handler = self.get_handler()

    def get_handler(self):
        # TODO: should let config override which handler we use
        return mail.EmailHandler(self.rattail_config)

    def get_data(self, session=None):
        data = []
        for email in self.handler.iter_emails():
            key = email.key or email.__name__
            email = email(self.rattail_config, key)
            data.append(self.normalize(email))
        return data

    def configure_grid(self, g):
        g.sorters['key'] = g.make_simple_sorter('key', foldcase=True)
        g.sorters['prefix'] = g.make_simple_sorter('prefix', foldcase=True)
        g.sorters['subject'] = g.make_simple_sorter('subject', foldcase=True)
        g.sorters['enabled'] = g.make_simple_sorter('enabled')
        g.set_sort_defaults('key')
        g.set_type('enabled', 'boolean')
        g.set_link('key')
        g.set_link('subject')

        # to
        g.set_renderer('to', self.render_to_short)
        g.sorters['to'] = g.make_simple_sorter('to', foldcase=True)

    def render_to_short(self, email, column):
        profile = email['_email']
        if self.rattail_config.production():
            if profile.dynamic_to:
                if profile.dynamic_to_help:
                    return profile.dynamic_to_help

        value = email['to']
        if not value:
            return ""
        recips = parse_list(value)
        if len(recips) < 3:
            return value
        return "{}, ...".format(', '.join(recips[:2]))

    def normalize(self, email):
        def get_recips(type_):
            recips = email.get_recips(type_)
            if recips:
                return ', '.join(recips)
        data = email.sample_data(self.request)
        return {
            '_email': email,
            'key': email.key,
            'fallback_key': email.fallback_key,
            'description': email.__doc__,
            'prefix': email.get_prefix(data, magic=False) or '',
            'subject': email.get_subject(data, render=False) or '',
            'sender': email.get_sender() or '',
            'replyto': email.get_replyto() or '',
            'to': get_recips('to') or '',
            'cc': get_recips('cc') or '',
            'bcc': get_recips('bcc') or '',
            'enabled': email.get_enabled(),
        }

    def get_instance(self):
        key = self.request.matchdict['key']
        return self.normalize(self.handler.get_email(key))

    def get_instance_title(self, email):
        return email['_email'].get_complete_subject(render=False)

    def editable_instance(self, profile):
        if self.rattail_config.demo():
            return profile['key'] != 'user_feedback'
        return True

    def deletable_instance(self, profile):
        if self.rattail_config.demo():
            return profile['key'] != 'user_feedback'
        return True

    def configure_form(self, f):
        super(ProfilesView, self).configure_form(f)
        profile = f.model_instance['_email']

        # key
        f.set_readonly('key')

        # fallback_key
        f.set_readonly('fallback_key')

        # description
        f.set_readonly('description')

        # prefix
        f.set_label('prefix', "Subject Prefix")

        # subject
        f.set_label('subject', "Subject Text")

        # sender
        f.set_label('sender', "From")

        # replyto
        f.set_label('replyto', "Reply-To")

        # to
        f.set_widget('to', dfwidget.TextAreaWidget(cols=60, rows=6))
        if self.rattail_config.production():
            if profile.dynamic_to:
                f.set_readonly('to')
                if profile.dynamic_to_help:
                    f.model_instance['to'] = profile.dynamic_to_help

        # cc
        f.set_widget('cc', dfwidget.TextAreaWidget(cols=60, rows=2))

        # bcc
        f.set_widget('bcc', dfwidget.TextAreaWidget(cols=60, rows=2))

        # enabled
        f.set_type('enabled', 'boolean')

    def make_form_schema(self):
        return EmailProfileSchema()

    def save_edit_form(self, form):
        key = self.request.matchdict['key']
        data = self.form_deserialized
        session = self.Session()
        api.save_setting(session, 'rattail.mail.{}.prefix'.format(key), data['prefix'])
        api.save_setting(session, 'rattail.mail.{}.subject'.format(key), data['subject'])
        api.save_setting(session, 'rattail.mail.{}.from'.format(key), data['sender'])
        api.save_setting(session, 'rattail.mail.{}.replyto'.format(key), data['replyto'])
        api.save_setting(session, 'rattail.mail.{}.to'.format(key), (data['to'] or '').replace('\n', ', '))
        api.save_setting(session, 'rattail.mail.{}.cc'.format(key), (data['cc'] or '').replace('\n', ', '))
        api.save_setting(session, 'rattail.mail.{}.bcc'.format(key), (data['bcc'] or '').replace('\n', ', '))
        api.save_setting(session, 'rattail.mail.{}.enabled'.format(key), six.text_type(data['enabled']).lower())
        return data

    def template_kwargs_view(self, **kwargs):
        key = self.request.matchdict['key']
        kwargs['email'] = self.handler.get_email(key)
        return kwargs


class RecipientsType(colander.String):
    """
    Custom schema type for email recipients.  This is used to present the
    recipients as a "list" within the text area, i.e. one recipient per line.
    Then the list is collapsed to a comma-delimited string for storage.
    """

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        recips = parse_list(appstruct)
        return '\n'.join(recips)

    def deserialize(self, node, cstruct):
        if cstruct == '' and self.allow_empty:
            return ''
        if not cstruct:
            return colander.null
        recips = parse_list(cstruct)
        return ', '.join(recips)


class EmailProfileSchema(colander.MappingSchema):

    prefix = colander.SchemaNode(colander.String())

    subject = colander.SchemaNode(colander.String())

    sender = colander.SchemaNode(colander.String())

    replyto = colander.SchemaNode(colander.String(), missing='')

    to = colander.SchemaNode(RecipientsType())

    cc = colander.SchemaNode(RecipientsType(), missing='')

    bcc = colander.SchemaNode(RecipientsType(), missing='')

    enabled = colander.SchemaNode(colander.Boolean())


class EmailPreview(View):
    """
    Lists available email templates, and can show previews of each.
    """

    def __init__(self, request):
        super(EmailPreview, self).__init__(request)
        self.handler = self.get_handler()

    def get_handler(self):
        # TODO: should let config override which handler we use
        return mail.EmailHandler(self.rattail_config)

    def __call__(self):

        # Forms submitted via POST are only used for sending emails.
        if self.request.method == 'POST':
            self.email_template()
            url = self.request.get_referrer(default=self.request.route_url('emailprofiles'))
            return self.redirect(url)

        # Maybe render a preview?
        key = self.request.GET.get('key')
        if key:
            type_ = self.request.GET.get('type', 'html')
            return self.preview_template(key, type_)

        assert False, "should not be here"

    def email_template(self):
        recipient = self.request.POST.get('recipient')
        if recipient:
            key = self.request.POST.get('email_key')
            if key:
                email = self.handler.get_email(key)
                data = email.sample_data(self.request)
                msg = email.make_message(data)

                subject = msg['Subject']
                del msg['Subject']
                msg['Subject'] = "[preview] {0}".format(subject)

                del msg['To']
                del msg['Cc']
                del msg['Bcc']
                msg['To'] = recipient

                # TODO: should refactor this to use email handler
                sent = mail.deliver_message(self.rattail_config, key, msg)

                self.request.session.flash("Preview for '{}' was {}emailed to {}".format(
                    key, '' if sent else '(NOT) ', recipient))

    def preview_template(self, key, type_):
        email = self.handler.get_email(key)
        template = email.get_template(type_)
        data = email.sample_data(self.request)
        self.request.response.text = template.render(**data)
        if type_ == 'txt':
            self.request.response.content_type = b'text/plain'
        return self.request.response

    @classmethod
    def defaults(cls, config):
        # email preview
        config.add_route('email.preview', '/email/preview/')
        config.add_view(cls, route_name='email.preview',
                        renderer='/email/preview.mako',
                        permission='emailprofiles.preview')
        config.add_tailbone_permission('emailprofiles', 'emailprofiles.preview',
                                       "Send preview email")


class EmailAttemptView(MasterView):
    """
    Master view for email attempts.
    """
    model_class = model.EmailAttempt
    route_prefix = 'email_attempts'
    url_prefix = '/email/attempts'
    creatable = False
    editable = False
    deletable = False

    labels = {
        'status_code': "Status",
    }

    grid_columns = [
        'key',
        'sender',
        'subject',
        'to',
        'sent',
        'status_code',
    ]

    form_fields = [
        'key',
        'sender',
        'subject',
        'to',
        'cc',
        'bcc',
        'sent',
        'status_code',
        'status_text',
    ]

    def configure_grid(self, g):
        super(EmailAttemptView, self).configure_grid(g)

        # sent
        g.set_sort_defaults('sent', 'desc')

        # status_code
        g.set_enum('status_code', self.enum.EMAIL_ATTEMPT)

        # links
        g.set_link('key')
        g.set_link('sender')
        g.set_link('subject')
        g.set_link('to')

    def configure_form(self, f):
        super(EmailAttemptView, self).configure_form(f)

        # status_code
        f.set_enum('status_code', self.enum.EMAIL_ATTEMPT)


def includeme(config):
    ProfilesView.defaults(config)
    EmailPreview.defaults(config)
    EmailAttemptView.defaults(config)
