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
Settings Views
"""

from __future__ import unicode_literals, absolute_import

import re

import six

from rattail.db import model, api
from rattail.settings import Setting
from rattail.util import import_module_path
from rattail.config import parse_bool

import colander
from webhelpers2.html import tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView, View


class SettingsView(MasterView):
    """
    Master view for the settings model.
    """
    model_class = model.Setting
    model_title = "Raw Setting"
    model_title_plural = "Raw Settings"
    feedback = re.compile(r'^rattail\.mail\.user_feedback\..*')

    grid_columns = [
        'name',
        'value',
    ]

    def configure_grid(self, g):
        super(SettingsView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')
        g.set_link('name')

    def configure_form(self, f):
        super(SettingsView, self).configure_form(f)
        if self.creating:
            f.set_validator('name', self.unique_name)

    def unique_name(self, node, value):
        setting = self.Session.query(model.Setting).get(value)
        if setting:
            raise colander.Invalid(node, "Setting name must be unique")

    def editable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True

    def deletable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True


class AppSettingsForm(forms.Form):

    def get_label(self, key):
        return self.labels.get(key, key)


class AppSettingsView(View):
    """
    Core view which exposes "app settings" - aka. admin-friendly settings with
    descriptions and type-specific form controls etc.
    """

    def __call__(self):
        settings = sorted(self.iter_known_settings(),
                          key=lambda setting: (setting.group,
                                               setting.namespace,
                                               setting.name))
        groups = sorted(set([setting.group for setting in settings]))
        current_group = None

        form = self.make_form(settings)
        form.cancel_url = self.request.current_route_url()
        if form.validate(newstyle=True):
            self.save_form(form)
            group = self.request.POST.get('settings-group')
            if group is not None:
                self.request.session['appsettings.current_group'] = group
            self.request.session.flash("App Settings have been saved.")
            return self.redirect(self.request.current_route_url())

        if self.request.method == 'POST':
            current_group = self.request.POST.get('settings-group')

        if not current_group:
            current_group = self.request.session.get('appsettings.current_group')

        use_buefy = self.get_use_buefy()
        context = {
            'index_title': "App Settings",
            'form': form,
            'dform': form.make_deform_form(),
            'groups': groups,
            'settings': settings,
            'use_buefy': use_buefy,
        }
        if use_buefy:
            context['buefy_data'] = self.get_buefy_data(form, groups, settings)
            # TODO: this seems hacky, and probably only needed if theme changes?
            if current_group == '(All)':
                current_group = ''
        else:
            group_options = [tags.Option(group, group) for group in groups]
            group_options.insert(0, tags.Option("(All)", "(All)"))
            context['group_options'] = group_options
        context['current_group'] = current_group
        return context

    def get_buefy_data(self, form, groups, settings):
        dform = form.make_deform_form()
        grouped = dict([(label, [])
                        for label in groups])

        for setting in settings:
            field = dform[setting.node_name]
            s = {
                'field_name': field.name,
                'label': form.get_label(field.name),
                'data_type': setting.data_type.__name__,
                'choices': setting.choices,
                'helptext': form.render_helptext(field.name) if form.has_helptext(field.name) else None,
                'error': field.error,
            }
            value = self.get_setting_value(setting)
            if setting.data_type is bool:
                value = parse_bool(value)
            s['value'] = value
            if field.error:
                s['error_messages'] = field.error_messages()
            grouped[setting.group].append(s)

        data = []
        for label in groups:
            group = {'label': label, 'settings': grouped[label]}
            data.append(group)

        return data

    def make_form(self, known_settings):
        schema = colander.MappingSchema()
        helptext = {}
        for setting in known_settings:
            kwargs = {
                'name': setting.node_name,
                'default': self.get_setting_value(setting),
            }
            if kwargs['default'] is None or kwargs['default'] == '':
                kwargs['default'] = colander.null
            if not setting.required:
                kwargs['missing'] = colander.null
            if setting.choices:
                kwargs['validator'] = colander.OneOf(setting.choices)
                kwargs['widget'] = forms.widgets.JQuerySelectWidget(
                    values=[(val, val) for val in setting.choices])
            schema.add(colander.SchemaNode(self.get_node_type(setting), **kwargs))
            helptext[setting.node_name] = setting.__doc__.strip()
        return AppSettingsForm(schema=schema, request=self.request, helptext=helptext)

    def get_node_type(self, setting):
        if setting.data_type is bool:
            return colander.Bool()
        elif setting.data_type is int:
            return colander.Integer()
        return colander.String()

    def save_form(self, form):
        for setting in self.iter_known_settings():
            value = form.validated[setting.node_name]
            if value is colander.null:
                value = ''
            self.save_setting_value(setting, value)

    def iter_known_settings(self):
        """
        Iterate over all known settings.
        """
        for module in self.rattail_config.getlist('rattail', 'settings', default=['rattail.settings']):
            module = import_module_path(module)
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, Setting) and obj is not Setting:
                    # NOTE: we set this here, and reference it elsewhere
                    obj.node_name = self.get_node_name(obj)
                    yield obj

    def get_node_name(self, setting):
        return '[{}] {}'.format(setting.namespace, setting.name)

    def get_setting_value(self, setting):
        if setting.data_type is bool:
            return self.rattail_config.getbool(setting.namespace, setting.name)
        return self.rattail_config.get(setting.namespace, setting.name)

    def save_setting_value(self, setting, value):
        existing = self.get_setting_value(setting)
        if existing != value:
            legacy_name = '{}.{}'.format(setting.namespace, setting.name)
            if setting.data_type is bool:
                value = 'true' if value else 'false'
            else:
                value = six.text_type(value)
            api.save_setting(Session(), legacy_name, value)

    @classmethod
    def defaults(cls, config):
        config.add_route('appsettings', '/settings/app/')
        config.add_view(cls, route_name='appsettings',
                        renderer='/appsettings.mako',
                        permission='settings.edit')


def includeme(config):
    AppSettingsView.defaults(config)
    SettingsView.defaults(config)
