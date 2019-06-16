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
Threading Extras
"""

from __future__ import unicode_literals

import sys
import threading


class Thread(threading.Thread):
    """
    Subclass of ``threading.Thread`` which exists only for the sake of ensuring
    the registered system exception hook (``sys.excepthook``) is invoked if an
    uncaught exception occurs within the context of the thread.
    """

    def run(self):
        try:
            super(Thread, self).run()
        except:
            sys.excepthook(*sys.exc_info())
