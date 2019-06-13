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
Tailbone Web API - Auth Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db.auth import authenticate_user

from tailbone.api import APIView, api
from tailbone.db import Session
from tailbone.auth import login_user, logout_user


class AuthenticationView(APIView):

    def user_info(self, user):
        return {
            'ok': True,
            'user': {
                'uuid': user.uuid,
                'username': user.username,
                'display_name': user.display_name,
            },
        }

    @api
    def check_session(self):
        """
        View to serve as "no-op" / ping action to check current user's session.
        This will establish a server-side web session for the user if none
        exists.  Note that this also resets the user's session timer.
        """
        if self.request.user:
            return self.user_info(self.request.user)
        return {}

    @api
    def login(self):
        """
        API login view.
        """
        if self.request.method == 'OPTIONS':
            return self.request.response

        username = self.request.json.get('username')
        password = self.request.json.get('password')
        if not (username and password):
            return {'error': "Invalid username or password"}

        user = authenticate_user(Session(), username, password)
        if not user:
            return {'error': "Invalid username or password"}

        login_user(self.request, user)
        return self.user_info(user)

    @api
    def logout(self):
        """
        API logout view.
        """
        if self.request.method == 'OPTIONS':
            return self.request.response

        logout_user(self.request)
        return {'ok': True}

    @classmethod
    def defaults(cls, config):

        # session
        config.add_route('api.session', '/session', request_method='GET')
        config.add_view(cls, attr='check_session', route_name='api.session', renderer='json')

        # login
        config.add_route('api.login', '/login', request_method=('OPTIONS', 'POST'))
        config.add_view(cls, attr='login', route_name='api.login', renderer='json')

        # logout
        config.add_route('api.logout', '/logout', request_method=('OPTIONS', 'POST'))
        config.add_view(cls, attr='logout', route_name='api.logout', renderer='json')


def includeme(config):
    AuthenticationView.defaults(config)
