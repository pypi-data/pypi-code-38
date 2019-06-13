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
appy.pod integration
"""

from __future__ import unicode_literals, absolute_import

import os
import warnings


def render_document(config, template, context, output, force=False, **kwargs):
    """
    Render a document using appy.pod
    """
    from appy.pod.renderer import Renderer

    if force and os.path.exists(output):
        os.remove(output)

    kwargs.setdefault('pythonWithUnoPath', config.get('rattail', 'uno_python'))
    renderer = Renderer(template, context, output, **kwargs)
    renderer.run()


def suppress_md5_warning():
    """
    Apply a filter to ignore some md5-related warning which comes up whenever
    we need to ``import appy``.
    """
    warnings.filterwarnings(
        'ignore',
        r"^the md5 module is deprecated; use hashlib instead$",
        DeprecationWarning, r'^appy\.shared\.dav$')
