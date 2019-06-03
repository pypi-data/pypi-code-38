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
"Principal" master view
"""

from __future__ import unicode_literals, absolute_import

import copy

from rattail.db.auth import has_permission
from rattail.core import Object
from rattail.util import OrderedDict

import wtforms
from webhelpers2.html import HTML

from tailbone.db import Session
from tailbone.views import MasterView


class PrincipalMasterView(MasterView):
    """
    Master view base class for security principal models, i.e. User and Role.
    """

    def get_fallback_templates(self, template, mobile=False):
        return [
            '/principal/{}.mako'.format(template),
        ] + super(PrincipalMasterView, self).get_fallback_templates(template, mobile=mobile)

    def perm_sortkey(self, item):
        key, value = item
        return value['label'].lower()

    def find_by_perm(self):
        """
        View for finding all users who have been granted a given permission
        """
        permissions = copy.deepcopy(self.request.registry.settings.get('tailbone_permissions', {}))

        # sort groups, and permissions for each group, for UI's sake
        sorted_perms = sorted(permissions.items(), key=self.perm_sortkey)
        for key, group in sorted_perms:
            group['perms'] = sorted(group['perms'].items(), key=self.perm_sortkey)

        # group options are stable, permission options may depend on submitted group
        group_choices = [(gkey, group['label']) for gkey, group in sorted_perms]
        permission_choices = [('_any_', "(any)")]
        if self.request.method == 'POST':
            if self.request.POST.get('permission_group') in permissions:
                permission_choices.extend([
                    (pkey, perm['label'])
                    for pkey, perm in permissions[self.request.POST['permission_group']]['perms']
                ])

        class PermissionForm(wtforms.Form):
            permission_group = wtforms.SelectField(choices=group_choices)
            permission = wtforms.SelectField(choices=permission_choices)

        principals = None
        form = PermissionForm(self.request.POST)
        if self.request.method == 'POST' and form.validate():
            permission = form.permission.data
            principals = self.find_principals_with_permission(self.Session(), permission)

        context = {'form': form, 'permissions': sorted_perms, 'principals': principals}

        if self.get_use_buefy():
            perms = self.get_buefy_perms_data(sorted_perms)
            context['buefy_perms'] = perms
            context['buefy_sorted_groups'] = list(perms)
            context['selected_group'] = self.request.POST.get('permission_group', 'common')
            context['selected_permission'] = self.request.POST.get('permission', None)

        return self.render_to_response('find_by_perm', context)

    def get_buefy_perms_data(self, sorted_perms):
        data = OrderedDict()
        for gkey, group in sorted_perms:

            gperms = []
            for pkey, perm in group['perms']:
                gperms.append({
                    'permkey': pkey,
                    'label': perm['label'],
                })

            data[gkey] = {
                'groupkey': gkey,
                'label': group['label'],
                'permissions': gperms,
            }

        return data

    @classmethod
    def defaults(cls, config):
        cls._principal_defaults(config)
        cls._defaults(config)

    @classmethod
    def _principal_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # find principal by permission
        config.add_route('{}.find_by_perm'.format(route_prefix), '{}/find-by-perm'.format(url_prefix))
        config.add_view(cls, attr='find_by_perm', route_name='{}.find_by_perm'.format(route_prefix),
                        permission='{}.find_by_perm'.format(permission_prefix))
        config.add_tailbone_permission(permission_prefix, '{}.find_by_perm'.format(permission_prefix),
                                       "Find all {} with permission X".format(model_title_plural))


class PermissionsRenderer(Object):
    permissions = None
    include_guest = False
    include_authenticated = False

    def __call__(self, principal, field):
        self.principal = principal
        return self.render()

    def render(self):
        principal = self.principal
        html = ''
        for groupkey in sorted(self.permissions, key=lambda k: self.permissions[k]['label'].lower()):
            inner = HTML.tag('p', c=self.permissions[groupkey]['label'])
            perms = self.permissions[groupkey]['perms']
            rendered = False
            for key in sorted(perms, key=lambda p: perms[p]['label'].lower()):
                checked = has_permission(Session(), principal, key,
                                         include_guest=self.include_guest,
                                         include_authenticated=self.include_authenticated)
                if checked:
                    label = perms[key]['label']
                    span = HTML.tag('span', c="[X]" if checked else "[ ]")
                    inner += HTML.tag('p', class_='perm', c=[span, HTML(' '), label])
                    rendered = True
            if rendered:
                html += HTML.tag('div', class_='group', c=[inner])
        return html or "(none granted)"
