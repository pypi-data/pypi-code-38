# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from .. import settings

grid_instance = None

SNAP_RESOLUTIONS = {
    'Grid': 1, 'Subgrid': 0.25
}


class Grid(object):
    def __init__(self):
        self._enabled = None
        self._spacing = None

    def reload_settings(self):
        snap = settings.instance()['Gui/snap_type']
        if snap in SNAP_RESOLUTIONS:
            self._enabled = True
            self._resolution = SNAP_RESOLUTIONS[snap]
        else:
            self._enabled = False

    @property
    def enabled(self):
        if self._enabled is None:
            self.reload_settings()
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def spacing(self):
        if self._spacing is None:
            self._spacing = settings.instance()['Gui/grid_spacing']
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        self._spacing = value

    def snap_to_grid(self, point):
        if self._enabled:
            snap = self._spacing * self._resolution
            point.setX(round(point.x() / snap) * snap)
            point.setY(round(point.y() / snap) * snap)
        return point


def create_grid():
    global grid_instance
    if grid_instance is not None:
        raise RuntimeError('Theme already instantiated')
    grid_instance = Grid()


def instance():
    """Returns the global grid instance"""
    if grid_instance is None:
        create_grid()
    return grid_instance
