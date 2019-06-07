# -*- coding: utf-8 -*-
# Copyright (c) 2013 LOGILAB S.A. (Paris, FRANCE).
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

#
# make sure the Qt rc files are converted into python modules, then load them
# this must be done BEFORE other hgview qt4 modules are loaded.
"""This module contains qt4 specific function for hgview configuration."""
from PyQt4.QtGui import QFont

def get_font(cfg):
    """Return a QFont instance initialized using parameters of the hgview
    configuration ``cfg``"""
    fontstr = cfg.getFont()
    fontsize = cfg.getFontSize()
    font = QFont()
    try:
        if not repr(font.fromString(fontstr)):
            raise Exception
        font.setPointSize(fontsize)
    except:
        print "bad font name '%s'" % fontstr
        font.setFamily("Monospace")
        font.setFixedPitch(True)
        font.setPointSize(10)
    return font
