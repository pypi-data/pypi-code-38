# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Pyramid scaffold templates
"""

from __future__ import unicode_literals, absolute_import

from rattail.files import resource_path
from rattail.util import prettify

from pyramid.scaffolds import PyramidTemplate


class RattailTemplate(PyramidTemplate):
    _template_dir = resource_path('rattail:data/project')
    summary = "Starter project based on Rattail / Tailbone"

    def pre(self, command, output_dir, vars):
        """
        Adds some more variables to the template context.
        """
        vars['project_title'] = prettify(vars['project'])
        vars['package_title'] = vars['package'].capitalize()
        return super(RattailTemplate, self).pre(command, output_dir, vars)
