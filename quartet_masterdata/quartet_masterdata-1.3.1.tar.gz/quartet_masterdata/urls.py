# -*- coding: utf-8 -*-
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

from django.conf.urls import url
from django.views.generic import TemplateView

from . import views
from quartet_masterdata.routers import router

urlpatterns = [
    url(
        regex="^location-by-identifier/(?P<identifier>[[\w\s\W]{1,150})/$",
        view=views.LocationByIdentifierView.as_view(),
        name='location-by-identifier',
    ),
    url(
        regex="^entry-geohistory-by-epc/(?P<epc>[[\w\s\W]{1,150})/$",
        view=views.EntryGeoHistoryView.as_view(),
        name='entry-geohistory-by-epc',
    )
    # url(
    #     regex="^Location/(?P<pk>\d+)/~delete/$",
    #     view=views.LocationDeleteView.as_view(),
    #     name='Location_delete',
	]
urlpatterns += router.urls
