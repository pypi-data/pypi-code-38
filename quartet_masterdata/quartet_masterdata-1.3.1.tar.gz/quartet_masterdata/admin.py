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
# Copyright 2019 SerialLab Corp.  All rights reserved.
from django.contrib import admin
from quartet_masterdata import models


@admin.register(models.LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'description')


class LocationFieldInline(admin.StackedInline):
    model = models.LocationField
    extra = 0

@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company'
    )
    inlines = [
        LocationFieldInline
    ]


@admin.register(models.CompanyType)
class CompanyTypeAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'description')


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'gs1_company_prefix')


class TradeItemFieldInline(admin.StackedInline):
    model = models.TradeItemField
    extra = 0


@admin.register(models.TradeItem)
class TradeItemAdmin(admin.ModelAdmin):
    list_display = (
        'GTIN14',
        'NDC',
        'functional_name',
        'manufacturer_name',
        'regulated_product_name'
    )
    ordering = ['GTIN14']
    inlines = [TradeItemFieldInline]


def register_to_site(admin_site):
    admin_site.register(models.Location, LocationAdmin)
    admin_site.register(models.LocationType, LocationTypeAdmin)
    admin_site.register(models.Company, CompanyAdmin)
    admin_site.register(models.CompanyType, CompanyTypeAdmin)
    admin_site.register(models.TradeItem, TradeItemAdmin)
