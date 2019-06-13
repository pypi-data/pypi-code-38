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
Auth Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db.auth import authenticate_user, set_user_password

import colander
from deform import widget as dfwidget
from pyramid.httpexceptions import HTTPForbidden
from webhelpers2.html import tags, literal

from tailbone import forms
from tailbone.db import Session
from tailbone.views import View
from tailbone.auth import login_user, logout_user


class UserLogin(colander.MappingSchema):

    username = colander.SchemaNode(colander.String())

    password = colander.SchemaNode(colander.String(),
                                   widget=dfwidget.PasswordWidget())


@colander.deferred
def current_password_correct(node, kw):
    user = kw['user']
    def validate(node, value):
        if not authenticate_user(Session(), user.username, value):
            raise colander.Invalid(node, "The password is incorrect")
    return validate


class ChangePassword(colander.MappingSchema):

    current_password = colander.SchemaNode(colander.String(),
                                           widget=dfwidget.PasswordWidget(),
                                           validator=current_password_correct)

    new_password = colander.SchemaNode(colander.String(),
                                       widget=dfwidget.CheckedPasswordWidget())


class AuthenticationView(View):

    def forbidden(self):
        """
        Access forbidden view.

        This is triggered whenever access is not allowed for an otherwise
        appropriate view.
        """
        next_url = self.request.get_referrer()
        msg = literal("You do not have permission to do that.")
        if not self.request.authenticated_userid:
            msg += literal("&nbsp; (Perhaps you should %s?)" %
                           tags.link_to("log in", self.request.route_url('login')))
            # Store current URL in session, for smarter redirect after login.
            self.request.session['next_url'] = self.request.current_route_url()
            next_url = self.request.route_url('login')
        self.request.session.flash(msg, allow_duplicate=False)
        return self.redirect(next_url)

    def login(self, mobile=False):
        """
        The login view, responsible for displaying and handling the login form.
        """
        home = 'mobile.home' if mobile else 'home'
        referrer = self.request.get_referrer(default=self.request.route_url(home))

        # redirect if already logged in
        if self.request.user:
            self.request.session.flash("{} is already logged in".format(self.request.user), 'error')
            return self.redirect(referrer)

        form = forms.Form(schema=UserLogin(), request=self.request)
        form.save_label = "Login"
        form.auto_disable_save = False
        form.auto_disable = False # TODO: deprecate / remove this
        form.show_reset = True
        form.show_cancel = False
        if form.validate(newstyle=True):
            user = self.authenticate_user(form.validated['username'],
                                          form.validated['password'])
            if user:
                # okay now they're truly logged in
                headers = login_user(self.request, user)
                # treat URL from session as referrer, if available
                referrer = self.request.session.pop('next_url', referrer)
                return self.redirect(referrer, headers=headers)

            else:
                self.request.session.flash("Invalid username or password", 'error')

        image_url = self.rattail_config.get(
            'tailbone', 'main_image_url',
            default=self.request.static_url('tailbone:static/img/home_logo.png'))

        return {
            'form': form,
            'referrer': referrer,
            'image_url': image_url,
        }

    def authenticate_user(self, username, password):
        return authenticate_user(Session(), username, password)

    def mobile_login(self):
        return self.login(mobile=True)

    def logout(self, mobile=False):
        """
        View responsible for logging out the current user.

        This deletes/invalidates the current session and then redirects to the
        login page.
        """
        # truly logout the user
        headers = logout_user(self.request)

        # redirect to home page after login, if so configured
        if self.rattail_config.getbool('tailbone', 'home_after_logout', default=False):
            home = 'mobile.home' if mobile else 'home'
            return self.redirect(self.request.route_url(home), headers=headers)

        # otherwise redirect to referrer, with 'login' page as fallback
        login = 'mobile.login' if mobile else 'login'
        referrer = self.request.get_referrer(default=self.request.route_url(login))
        return self.redirect(referrer, headers=headers)

    def mobile_logout(self):
        return self.logout(mobile=True)

    def noop(self):
        """
        View to serve as "no-op" / ping action to reset current user's session timer
        """
        return {'status': 'ok'}

    def change_password(self):
        """
        Allows a user to change his or her password.
        """
        if not self.request.user:
            return self.redirect(self.request.route_url('home'))

        if self.rattail_config.demo() and self.request.user.username == 'chuck':
            self.request.session.flash("Cannot change password for 'chuck' in demo mode", 'error')
            return self.redirect(self.request.get_referrer())

        schema = ChangePassword().bind(user=self.request.user)
        form = forms.Form(schema=schema, request=self.request)
        if form.validate(newstyle=True):
            set_user_password(self.request.user, form.validated['new_password'])
            self.request.session.flash("Your password has been changed.")
            return self.redirect(self.request.get_referrer())

        return {'form': form}

    def become_root(self):
        """
        Elevate the current request to 'root' for full system access.
        """
        if not self.request.is_admin:
            raise HTTPForbidden()
        self.request.user.record_event(self.enum.USER_EVENT_BECOME_ROOT)
        self.request.session['is_root'] = True
        self.request.session.flash("You have been elevated to 'root' and now have full system access")
        return self.redirect(self.request.get_referrer())

    def stop_root(self):
        """
        Lower the current request from 'root' back to normal access.
        """
        if not self.request.is_admin:
            raise HTTPForbidden()
        self.request.user.record_event(self.enum.USER_EVENT_STOP_ROOT)
        self.request.session['is_root'] = False
        self.request.session.flash("Your normal system access has been restored")
        return self.redirect(self.request.get_referrer())

    @classmethod
    def defaults(cls, config):

        # forbidden
        config.add_forbidden_view(cls, attr='forbidden')

        # login
        config.add_route('login', '/login')
        config.add_view(cls, attr='login', route_name='login', renderer='/login.mako')
        config.add_route('mobile.login', '/mobile/login')
        config.add_view(cls, attr='mobile_login', route_name='mobile.login', renderer='/mobile/login.mako')

        # logout
        config.add_route('logout', '/logout')
        config.add_view(cls, attr='logout', route_name='logout')
        config.add_route('mobile.logout', '/mobile/logout')
        config.add_view(cls, attr='mobile_logout', route_name='mobile.logout')

        # no-op
        config.add_route('noop', '/noop')
        config.add_view(cls, attr='noop', route_name='noop', renderer='json')

        # change password
        config.add_route('change_password', '/change-password')
        config.add_view(cls, attr='change_password', route_name='change_password', renderer='/change_password.mako')

        # become/stop root
        config.add_route('become_root', '/root/yes')
        config.add_view(cls, attr='become_root', route_name='become_root')
        config.add_route('stop_root', '/root/no')
        config.add_view(cls, attr='stop_root', route_name='stop_root')


def includeme(config):
    AuthenticationView.defaults(config)
