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
Database API
"""

from __future__ import unicode_literals, absolute_import

from rattail.db.api.people import get_employee_by_id
from rattail.db.api.products import (
    get_product_by_upc, get_product_by_item_id, get_product_by_code, get_product_by_vendor_code,
    set_regular_price, set_current_sale_price)
from rattail.db.api.settings import get_setting, save_setting
from rattail.db.api.org import get_department, get_subdepartment
from rattail.db.api.stores import get_store
from rattail.db.api.vendors import get_vendor

from .users import make_username
