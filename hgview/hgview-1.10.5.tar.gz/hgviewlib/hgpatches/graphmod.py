# -*- coding: utf-8 -*-
# Copyright (c) 2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
'''
Contains Hg compatibility for older versions
'''

#pylint: disable=E0611
try:
    from mercurial import graphmod
    if not getattr(graphmod, '_fixlongrightedges', None): # because of lazy import
        raise ImportError
    from mercurial.graphmod import (_fixlongrightedges,
                                    _getnodelineedgestail,
                                    _drawedges,
                                    _getpaddingline)
except ImportError: # <2.3
    from hgext.graphlog import (fix_long_right_edges as _fixlongrightedges,
                                get_nodeline_edges_tail as _getnodelineedgestail,
                                draw_edges as _drawedges,
                                get_padding_line as _getpaddingline)
