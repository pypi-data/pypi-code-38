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
Role Views
"""

from __future__ import unicode_literals, absolute_import

import six
from sqlalchemy import orm

from rattail.db import model
from rattail.db.auth import has_permission, administrator_role, guest_role, authenticated_role

import colander
from deform import widget as dfwidget

from tailbone import grids
from tailbone.db import Session
from tailbone.views.principal import PrincipalMasterView, PermissionsRenderer


class RolesView(PrincipalMasterView):
    """
    Master view for the Role model.
    """
    model_class = model.Role
    has_versions = True

    grid_columns = [
        'name',
        'session_timeout',
    ]

    form_fields = [
        'name',
        'session_timeout',
        'permissions',
    ]

    def configure_grid(self, g):
        super(RolesView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')
        g.set_link('name')

    def unique_name(self, node, value):
        query = self.Session.query(model.Role)\
                            .filter(model.Role.name == value)
        if self.editing:
            role = self.get_instance()
            query = query.filter(model.Role.uuid != role.uuid)
        if query.count():
            raise colander.Invalid(node, "Name must be unique")

    def configure_form(self, f):
        super(RolesView, self).configure_form(f)
        role = f.model_instance

        # name
        f.set_validator('name', self.unique_name)

        # permissions
        self.tailbone_permissions = self.request.registry.settings.get('tailbone_permissions', {})
        f.set_renderer('permissions', PermissionsRenderer(permissions=self.tailbone_permissions))
        f.set_node('permissions', colander.Set())
        f.set_widget('permissions', PermissionsWidget(permissions=self.tailbone_permissions))
        if self.editing:
            granted = []
            for groupkey in self.tailbone_permissions:
                for key in self.tailbone_permissions[groupkey]['perms']:
                    if has_permission(self.Session(), role, key, include_guest=False, include_authenticated=False):
                        granted.append(key)
            f.set_default('permissions', granted)

        # session_timeout
        f.set_renderer('session_timeout', self.render_session_timeout)
        if self.editing and role is guest_role(self.Session()):
            f.set_readonly('session_timeout')

    def render_session_timeout(self, role, field):
        if role is guest_role(self.Session()):
            return "(not applicable)"
        if role.session_timeout is None:
            return ""
        return six.text_type(role.session_timeout)

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        role = super(RolesView, self).objectify(form, data)
        role.permissions = data['permissions']
        return role

    def template_kwargs_view(self, **kwargs):
        role = kwargs['instance']
        if role.users:
            users = sorted(role.users, key=lambda u: u.username)
            actions = [
                grids.GridAction('view', icon='zoomin',
                                 url=lambda r, i: self.request.route_url('users.view', uuid=r.uuid))
            ]
            kwargs['users'] = grids.Grid(None, users, ['username'], request=self.request, model_class=model.User,
                                         main_actions=actions)
        else:
            kwargs['users'] = None
        kwargs['guest_role'] = guest_role(self.Session())
        kwargs['authenticated_role'] = authenticated_role(self.Session())
        return kwargs

    def before_delete(self, role):
        admin = administrator_role(self.Session())
        guest = guest_role(self.Session())
        authenticated = authenticated_role(self.Session())
        if role in (admin, guest, authenticated):
            self.request.session.flash("You may not delete the {} role.".format(role.name), 'error')
            return self.redirect(self.request.get_referrer(default=self.request.route_url('roles')))

    def find_principals_with_permission(self, session, permission):
        # TODO: this should search Permission table instead, and work backward to Role?
        all_roles = session.query(model.Role)\
                           .order_by(model.Role.name)\
                           .options(orm.joinedload(model.Role._permissions))
        roles = []
        for role in all_roles:
            if has_permission(session, role, permission):
                roles.append(role)
        return roles


class PermissionsWidget(dfwidget.Widget):
    template = 'permissions'
    permissions = None
    true_val = 'true'

    def deserialize(self, field, pstruct):
        return [key for key, val in pstruct.items()
                if val == self.true_val]

    def get_checked_value(self, cstruct, value):
        if cstruct is colander.null:
            return False
        return value in cstruct

    def serialize(self, field, cstruct, **kw):
        kw.setdefault('permissions', self.permissions)
        template = self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)


def includeme(config):
    RolesView.defaults(config)
