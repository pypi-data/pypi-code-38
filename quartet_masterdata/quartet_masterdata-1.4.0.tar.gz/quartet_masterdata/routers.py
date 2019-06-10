# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

from rest_framework.routers import DefaultRouter
from quartet_masterdata import viewsets

router = DefaultRouter()
router.register(
    r'locations',
    viewsets.LocationViewSet,
    base_name='entries'
)
router.register(
    r'location-fields',
    viewsets.LocationFieldViewSet,
    base_name='location-fields'
)
router.register(
    r'location-types',
    viewsets.LocationTypeViewSet,
    base_name='location-types'
)
router.register(
    r'location-identifiers',
    viewsets.LocationIdentifierViewSet,
    base_name='location-identifiers'
)
router.register(
    r'trade-items',
    viewsets.TradeItemViewSet,
    base_name='trade-items'
)
router.register(
    r'companies',
    viewsets.CompanyViewSet,
    base_name='companies'
)
router.register(
    r'company-types',
    viewsets.CompanyTypeViewSet,
    base_name='company-types'
)
router.register(
    r'trade-item-fields',
    viewsets.TradeItemFieldViewSet,
    base_name='trade-item-fields'
)
