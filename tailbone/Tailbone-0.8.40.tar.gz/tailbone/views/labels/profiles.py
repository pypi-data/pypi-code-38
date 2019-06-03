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
Label Profile Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import colander

from tailbone import forms
from tailbone.views import MasterView


class ProfilesView(MasterView):
    """
    Master view for the LabelProfile model.
    """
    model_class = model.LabelProfile
    model_title = "Label Profile"
    url_prefix = '/labels/profiles'
    has_versions = True

    grid_columns = [
        'ordinal',
        'code',
        'description',
        'visible',
        'sync_me',
    ]

    form_fields = [
        'ordinal',
        'code',
        'description',
        'printer_spec',
        'formatter_spec',
        'format',
        'visible',
        'sync_me',
    ]

    def configure_grid(self, g):
        super(ProfilesView, self).configure_grid(g)
        g.set_sort_defaults('ordinal')
        g.set_type('visible', 'boolean')
        g.set_link('code')
        g.set_link('description')

    def configure_form(self, f):
        super(ProfilesView, self).configure_form(f)

        # format
        f.set_type('format', 'codeblock')

    def after_create(self, profile):
        self.after_edit(profile)

    def after_edit(self, profile):
        if not profile.format:
            formatter = profile.get_formatter(self.rattail_config)
            if formatter:
                try:
                    profile.format = formatter.default_format
                except NotImplementedError:
                    pass

    def make_printer_settings_form(self, profile, printer):
        use_buefy = self.get_use_buefy()
        schema = colander.Schema()

        for name, label in printer.required_settings.items():
            node = colander.SchemaNode(colander.String(),
                                       name=name,
                                       title=label,
                                       default=profile.get_printer_setting(name))
            schema.add(node)

        form = forms.Form(schema=schema, request=self.request,
                          use_buefy=use_buefy,
                          model_instance=profile,
                          # TODO: ugh, this is necessary to avoid some logic
                          # which assumes a ColanderAlchemy schema i think?
                          appstruct=None)
        form.cancel_url = self.get_action_url('view', profile)
        form.auto_disable_cancel = True

        form.insert_before(schema.children[0].name, 'label_profile')
        form.set_readonly('label_profile')
        form.set_renderer('label_profile', lambda p, f: p.description)

        form.insert_after('label_profile', 'printer_spec')
        form.set_readonly('printer_spec')
        form.set_renderer('printer_spec', lambda p, f: p.printer_spec)

        return form

    def printer_settings(self):
        """
        View for editing extended Printer Settings, for a given Label Profile.
        """
        profile = self.get_instance()
        read_profile = self.redirect(self.get_action_url('view', profile))

        printer = profile.get_printer(self.rattail_config)
        if not printer:
            msg = "Label profile \"{}\" does not have a functional printer spec.".format(profile)
            self.request.session.flash(msg)
            return read_profile
        if not printer.required_settings:
            msg = "Printer class for label profile \"{}\" does not require any settings.".format(profile)
            self.request.session.flash(msg)
            return read_profile

        form = self.make_printer_settings_form(profile, printer)

        # TODO: should use form.validate() here
        if self.request.method == 'POST':
            for setting in printer.required_settings:
                if setting in self.request.POST:
                    profile.save_printer_setting(setting, self.request.POST[setting])
            return read_profile

        return self.render_to_response('printer', {
            'form': form,
            'dform': form.make_deform_form(),
            'profile': profile,
            'printer': printer,
        })

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._labelprofile_defaults(config)

    @classmethod
    def _labelprofile_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()

        # edit printer settings
        config.add_route('{}.printer_settings'.format(route_prefix), '{}/{{{}}}/printer'.format(url_prefix, model_key))
        config.add_view(cls, attr='printer_settings', route_name='{}.printer_settings'.format(route_prefix),
                        permission='{}.edit'.format(permission_prefix))


def includeme(config):
    ProfilesView.defaults(config)
