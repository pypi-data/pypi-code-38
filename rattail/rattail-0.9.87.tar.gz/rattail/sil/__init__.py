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
Standard Interchange Language

Please see the `Standard Interchange Language Specifications
<http://productcatalog.gs1us.org/Store/tabid/86/CategoryID/21/List/1/catpageindex/2/Level/a/ProductID/46/Default.aspx>`_
for more information.
"""

from rattail.sil.columns import *
from .batches import consume_batch_id
from rattail.sil.writer import Writer
