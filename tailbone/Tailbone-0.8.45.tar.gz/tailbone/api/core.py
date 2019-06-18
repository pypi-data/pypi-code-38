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
Tailbone Web API - Core Views
"""

from __future__ import unicode_literals, absolute_import

from tailbone.views import View


def api(view_meth):
    """
    Common decorator for all API views.  Ideally this would not be needed..but
    for now, alas, it is.
    """
    def wrapped(view, *args, **kwargs):

        # TODO: why doesn't this work here...? (instead we have to repeat this
        # code in lots of other places)
        # if view.request.method == 'OPTIONS':
        #     return view.request.response

        # invoke the view logic first, since presumably it may involve a
        # redirect in which case we don't really need to add the CSRF token.
        # main known use case for this is the /logout endpoint - if that gets
        # hit then the "current" (old) session will be destroyed, in which case
        # we can't use the token from that, but instead must generate a new one.
        result = view_meth(view, *args, **kwargs)

        # explicitly set CSRF token cookie, unless OPTIONS request 
        # TODO: why doesn't pyramid do this for us again?
        if view.request.method != 'OPTIONS':
            view.request.response.set_cookie(name='XSRF-TOKEN',
                                             value=view.request.session.get_csrf_token())

        return result

    return wrapped


class APIView(View):
    """
    Base class for all API views.
    """
