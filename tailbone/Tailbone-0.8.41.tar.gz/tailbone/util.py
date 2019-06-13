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
Utilities
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import pytz
import humanize

from rattail.time import timezone, make_utc
from rattail.files import resource_path

import colander
from pyramid.renderers import get_renderer
from webhelpers2.html import HTML, tags


def csrf_token(request, name='_csrf'):
    """
    Convenience function. Returns CSRF hidden tag inside hidden DIV.
    """
    token = request.session.get_csrf_token()
    if token is None:
        token = request.session.new_csrf_token()
    return HTML.tag("div", tags.hidden(name, value=token), style="display:none;")


def should_use_buefy(request):
    """
    Returns a flag indicating whether or not the current theme supports (and
    therefore should use) the Buefy JS library.
    """
    # first check theme-specific setting, if one has been defined
    theme = request.registry.settings['tailbone.theme']
    buefy = request.rattail_config.getbool('tailbone', 'themes.{}.use_buefy'.format(theme))
    if buefy is not None:
        return buefy

    # TODO: should not hard-code this surely, but works for now...
    if theme == 'falafel':
        return True

    # TODO: probably should not use this fallback? it was the first setting
    # i tested with, but is poorly named to say the least
    return request.rattail_config.getbool('tailbone', 'grids.use_buefy', default=False)


def pretty_datetime(config, value):
    """
    Formats a datetime as a "pretty" human-readable string, with a tooltip
    showing the ISO string value.

    :param config: Reference to a config object.

    :param value: A ``datetime.datetime`` instance.  Note that if this instance
       is not timezone-aware, its timezone is assumed to be UTC.
    """
    if not value:
        return ''

    # Make sure we're dealing with a tz-aware value.  If we're given a naive
    # value, we assume it to be local to the UTC timezone.
    if not value.tzinfo:
        value = pytz.utc.localize(value)

    # Calculate time diff using UTC.
    time_ago = datetime.datetime.utcnow() - make_utc(value)

    # Convert value to local timezone.
    local = timezone(config)
    value = local.normalize(value.astimezone(local))

    return HTML.tag('span',
                    title=value.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                    c=humanize.naturaltime(time_ago))


def raw_datetime(config, value, verbose=False):
    """
    Formats a datetime as a "raw" human-readable string, with a tooltip
    showing the more human-friendly "time since" equivalent.

    :param config: Reference to a config object.

    :param value: A ``datetime.datetime`` instance.  Note that if this instance
       is not timezone-aware, its timezone is assumed to be UTC.
    """
    if not value:
        return ''

    # Make sure we're dealing with a tz-aware value.  If we're given a naive
    # value, we assume it to be local to the UTC timezone.
    if not value.tzinfo:
        value = pytz.utc.localize(value)

    # Calculate time diff using UTC.
    time_ago = datetime.datetime.utcnow() - make_utc(value)

    # Convert value to local timezone.
    local = timezone(config)
    value = local.normalize(value.astimezone(local))

    kwargs = {}

    # Avoid strftime error when year falls before epoch.
    if value.year >= 1900:
        kwargs['c'] = value.strftime('%Y-%m-%d %I:%M:%S %p')
    else:
        kwargs['c'] = six.text_type(value)

    # avoid humanize error when calculating huge time diff
    time_diff = None
    if abs(time_ago.days) < 100000:
        time_diff = humanize.naturaltime(time_ago)

        # by "verbose" we mean the result text to look like "YYYY-MM-DD (X days ago)"
        if verbose:
            kwargs['c'] = "{} ({})".format(kwargs['c'], time_diff)

        # vs. if *not* verbose, text is "YYYY-MM-DD" but we add "X days ago" as title
        else:
            kwargs['title'] = time_diff

    return HTML.tag('span', **kwargs)


def set_app_theme(request, theme, session=None):
    """
    Set the app theme.  This modifies the *global* Mako template lookup
    directory path, i.e. theme for all users will change immediately.

    This also saves the setting for the new theme, and updates the running app
    registry settings with the new theme.
    """
    from rattail.db import api

    theme = get_effective_theme(request.rattail_config, theme=theme, session=session)
    theme_path = get_theme_template_path(request.rattail_config, theme=theme, session=session)

    # there's only one global template lookup; can get to it via any renderer
    # but should *not* use /base.mako since that one is about to get volatile
    renderer = get_renderer('/menu.mako')
    lookup = renderer.lookup

    # overwrite first entry in lookup's directory list
    lookup.directories[0] = theme_path

    # clear template cache for lookup object, so it will reload each (as needed)
    lookup._collection.clear()

    api.save_setting(session, 'tailbone.theme', theme)
    request.registry.settings['tailbone.theme'] = theme


def get_theme_template_path(rattail_config, theme=None, session=None):
    """
    Retrieves the template path for the given theme.
    """
    theme = get_effective_theme(rattail_config, theme=theme, session=session)
    theme_path = rattail_config.get('tailbone', 'theme.{}'.format(theme),
                                    default='tailbone:templates/themes/{}'.format(theme))
    return resource_path(theme_path)


def get_effective_theme(rattail_config, theme=None, session=None):
    """
    Validates and returns the "effective" theme.  If you provide a theme, that
    will be used; otherwise it is read from database setting.
    """
    from rattail.db import api

    if not theme:
        theme = api.get_setting(session, 'tailbone.theme') or 'default'

    # confirm requested theme is available
    available = rattail_config.getlist('tailbone', 'themes',
                                       default=['bobcat'])
    available.append('default')
    if theme not in available:
        raise ValueError("theme not available: {}".format(theme))

    return theme


def validate_email_address(address):
    """
    Perform basic validation on the given email address.  This leverages the
    ``colander`` package for actual validation logic.
    """
    node = colander.SchemaNode(typ=colander.String)
    validator = colander.Email()
    validator(node, address)
    return address


def email_address_is_valid(address):
    """
    Returns boolean indicating whether the address can validate.
    """
    try:
        validate_email_address(address)
    except colander.Invalid:
        return False
    return True
