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
from quartet_epcis.routers import router
from quartet_epcis import views

app_name = 'quartet_epcis'

urlpatterns = [
    url(r'^event-detail/?$',
        views.EventDetailView.as_view(), name='event-detail'),
    url(r'^event-detail/(?P<event_id>[0-9a-fA-F\-_]{1,50})/$',
        views.EventDetailView.as_view(), name='event-detail'),
    url(r'^events-by-entry-id/?$',
        views.EntryEventHistoryView.as_view(),
        name='events-by-entry-id'),
    url(r'^events-by-entry-id/(?P<entry_identifier>[0-9a-zA-Z\W]{1,100})/$',
        views.EntryEventHistoryView.as_view(),
        name='events-by-entry-id'),
    url(r'^events-by-entry-pk/?$',
        views.EntryEventHistoryView.as_view(),
        name='events-by-entry-pk'),
    url(r'^events-by-entry-pk/(?P<entry_pk>[0-9a-zA-Z\W]{1,100})/$',
        views.EntryEventHistoryView.as_view(),
        name='events-by-entry-pk'),
    url(r'^events-by-ilmd/?$',
        views.EventsByILMDView.as_view(),
        name='events-by-ilmd'),
    url(r'^events-by-ilmd/(?P<ilmd_name>[[\w\s\W]{1,150})/'
        r'(?P<ilmd_value>[[\w\s\W]'
        r'{1,255})/$',
        views.EventsByILMDView.as_view(),
        name='events-by-ilmd'),
    url(r'^message/?$',
        views.MessageDetail.as_view(),
        name='message'
        ),
    url(r'^message/(?P<message_id>[\w-]{1,50})/$',
        views.MessageDetail.as_view(),
        name='message'
        ),
]

urlpatterns += router.urls
