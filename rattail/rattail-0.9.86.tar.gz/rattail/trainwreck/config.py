# -*- coding: utf-8; -*-
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
Trainwreck Config
"""

from __future__ import unicode_literals, absolute_import

try:
    from rattail.trainwreck.db import Session as TrainwreckSession
except ImportError:
    TrainwreckSession = None

from rattail.config import ConfigExtension
from rattail.db.config import get_engines


class TrainwreckConfig(ConfigExtension):
    """
    Configures any Trainwreck database connections
    """
    key = 'rattail.trainwreck'

    def configure(self, config):
        if TrainwreckSession:
            engines = get_engines(config, section='trainwreck.db')
            config.trainwreck_engines = engines
            config.trainwreck_engine = engines.get('default')
            TrainwreckSession.configure(bind=config.trainwreck_engine)
