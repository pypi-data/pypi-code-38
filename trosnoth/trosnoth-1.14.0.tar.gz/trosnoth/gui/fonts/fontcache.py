# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import logging

import pygame

log = logging.getLogger(__name__)

_cache = {}

def get(filename, size, bold = False):
    try:
        return _cache[filename, size, bold]
    except KeyError:
        try:
            result = pygame.font.Font(filename, size)
        except IOError:
            log.error('Font Cache: unable to load font %r' % (filename,))
            result = pygame.font.Font(None, size)

        if bold:
            result.set_bold(True)

        _cache[filename, size, bold] = result
        return result
