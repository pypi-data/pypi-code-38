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
Event Subscribers
"""

from __future__ import unicode_literals, absolute_import

import six
import json
import datetime

import rattail
from rattail.db import model
from rattail.db.auth import cache_permissions

import colander
import deform
from pyramid import threadlocal
from webhelpers2.html import tags

import tailbone
from tailbone import helpers
from tailbone.db import Session
from tailbone.menus import make_simple_menus


def new_request(event):
    """
    Identify the current user, and cache their current permissions.  Also adds
    the ``rattail_config`` attribute to the request.

    A global Rattail ``config`` should already be present within the Pyramid
    application registry's settings, which would normally be accessed via::
    
       request.registry.settings['rattail_config']

    This function merely "promotes" that config object so that it is more
    directly accessible, a la::

       request.rattail_config

    .. note::
       This of course assumes that a Rattail ``config`` object *has* in fact
       already been placed in the application registry settings.  If this is
       not the case, this function will do nothing.
    """
    request = event.request
    rattail_config = request.registry.settings.get('rattail_config')
    if rattail_config:
        request.rattail_config = rattail_config

    request.user = None
    uuid = request.authenticated_userid
    if uuid:
        request.user = Session.query(model.User).get(uuid)
        if request.user:
            # assign user to the session, for sake of versioning
            Session().set_continuum_user(request.user)

    # assign client IP address to the session, for sake of versioning
    Session().continuum_remote_addr = request.client_addr

    request.is_admin = bool(request.user) and request.user.is_admin()
    request.is_root = request.is_admin and request.session.get('is_root', False)

    request.tailbone_cached_permissions = cache_permissions(Session(), request.user)


def before_render(event):
    """
    Adds goodies to the global template renderer context.
    """

    request = event.get('request') or threadlocal.get_current_request()

    renderer_globals = event
    renderer_globals['h'] = helpers
    renderer_globals['url'] = request.route_url
    renderer_globals['rattail'] = rattail
    renderer_globals['tailbone'] = tailbone
    renderer_globals['enum'] = request.rattail_config.get_enum()
    renderer_globals['six'] = six
    renderer_globals['json'] = json
    renderer_globals['datetime'] = datetime
    renderer_globals['colander'] = colander
    renderer_globals['deform'] = deform

    # theme  - we only want do this for classic web app, *not* API
    # TODO: so, clearly we need a better way to distinguish the two
    if 'tailbone.theme' in request.registry.settings:
        renderer_globals['theme'] = request.registry.settings['tailbone.theme']
        # note, this is just a global flag; user still needs permission to see picker
        expose_picker = request.rattail_config.getbool('tailbone', 'themes.expose_picker',
                                                       default=False)
        renderer_globals['expose_theme_picker'] = expose_picker
        if expose_picker:
            available = request.rattail_config.getlist('tailbone', 'themes',
                                                       default=['bobcat'])
            if 'default' not in available:
                available.insert(0, 'default')
            options = [tags.Option(theme) for theme in available]
            renderer_globals['theme_picker_options'] = options

        # heck while we're assuming the classic web app here...
        # (we don't want this to happen for the API either!)
        # TODO: just..awful *shrug*
        # note that we assume "simple" menus nowadays
        if request.rattail_config.getbool('tailbone', 'menus.simple', default=True):
            renderer_globals['menus'] = make_simple_menus(request)

        # TODO: ugh, same deal here
        renderer_globals['messaging_enabled'] = request.rattail_config.getbool(
            'tailbone', 'messaging.enabled', default=False)

        # background color may be set per-request, by some apps
        if hasattr(request, 'background_color') and request.background_color:
            renderer_globals['background_color'] = request.background_color
        else: # otherwise we use the one from config
            renderer_globals['background_color'] = request.rattail_config.get(
                'tailbone', 'background_color')

        # here we globally declare widths for grid filter pseudo-columns
        widths = request.rattail_config.get('tailbone', 'grids.filters.column_widths')
        if widths:
            widths = widths.split(';')
            if len(widths) < 2:
                widths = None
        if not widths:
            widths = ['15em', '15em']
        renderer_globals['filter_fieldname_width'] = widths[0]
        renderer_globals['filter_verb_width'] = widths[1]


def add_inbox_count(event):
    """
    Adds the current user's inbox message count to the global renderer context.

    Note that this is not enabled by default; to turn it on you must do this:

       config.add_subscriber('tailbone.subscribers.add_inbox_count', 'pyramid.events.BeforeRender')
    """
    request = event.get('request') or threadlocal.get_current_request()
    if request.user:
        renderer_globals = event
        enum = request.rattail_config.get_enum()
        renderer_globals['inbox_count'] = Session.query(model.Message)\
                                                 .outerjoin(model.MessageRecipient)\
                                                 .filter(model.MessageRecipient.recipient == Session.merge(request.user))\
                                                 .filter(model.MessageRecipient.status == enum.MESSAGE_STATUS_INBOX)\
                                                 .count()


def context_found(event):
    """
    Attach some goodies to the request object.

    The following is attached to the request:

    * The currently logged-in user instance (if any), as ``user``.

    * ``is_admin`` flag indicating whether user has the Administrator role.

    * ``is_root`` flag indicating whether user is currently elevated to root.

    * A shortcut method for permission checking, as ``has_perm()``.

    * A shortcut method for fetching the referrer, as ``get_referrer()``.
    """

    request = event.request

    def has_perm(name):
        if name in request.tailbone_cached_permissions:
            return True
        return request.is_root
    request.has_perm = has_perm

    def has_any_perm(*names):
        for name in names:
            if has_perm(name):
                return True
        return False
    request.has_any_perm = has_any_perm

    def get_referrer(default=None, mobile=False):
        if request.params.get('referrer'):
            return request.params['referrer']
        if request.session.get('referrer'):
            return request.session.pop('referrer')
        referrer = request.referrer
        if (not referrer or referrer == request.current_route_url()
            or not referrer.startswith(request.host_url)):
            if default:
                referrer = default
            elif mobile:
                referrer = request.route_url('mobile.home')
            else:
                referrer = request.route_url('home')
        return referrer
    request.get_referrer = get_referrer

    def get_session_timeout():
        """
        Returns the timeout in effect for the current session
        """
        return request.session.get('_timeout')
    request.get_session_timeout = get_session_timeout


def includeme(config):
    config.add_subscriber(new_request, 'pyramid.events.NewRequest')
    config.add_subscriber(before_render, 'pyramid.events.BeforeRender')
    config.add_subscriber(context_found, 'pyramid.events.ContextFound')
