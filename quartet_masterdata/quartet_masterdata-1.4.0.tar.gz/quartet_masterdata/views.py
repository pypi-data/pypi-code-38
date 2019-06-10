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

from rest_framework.response import Response
from rest_framework import views, status
from quartet_masterdata import models, serializers
from quartet_epcis.models.entries import EntryEvent
from quartet_masterdata.geolocation import GeoEvent, GeoEventSerializer


class LocationByIdentifierView(views.APIView):
    '''
    Returns a Location detail record based on the inbound SGLN identifier.
    The location viewset can return by database primary key.
    '''
    queryset = models.Location.objects.none()

    def get(self, request, format=None, identifier=None):
        try:
            location = models.Location.objects.select_related(
                'location_type',
            ).prefetch_related(
                'locationfield_set',
                'locationidentifier_set'
            ).get(
                SGLN=identifier
            )
            serializer = serializers.LocationSerializer(location)
            return Response(serializer.data)
        except models.Location.DoesNotExist:
            response = Response(
                'The location with identifier %s could not '
                'be found.' % identifier,
                status=status.HTTP_404_NOT_FOUND
            )
        return response


class EntryGeoHistoryView(views.APIView):
    '''
    Returns a list of events and lat/long co-ordinates associated
    with any GLNs in the events.

    To use, specify the URL as such (when used in quartet):

    ..code-block:: text

        http[s]://[hostname]:[port]/masterdata/entry-geohistory-by-epc/[urn value]

    For example:

    ..code-block:: text

        http://localhost:8000/masterdata/entry-geohistory-by-epc/urn:epc:id:sgtin:305555.0555555.1/

    '''
    queryset = models.Location.objects.none()

    def get(self, request, format=None, epc=None, epc_pk=None):
        # get all the events and biz_locations ordered by date
        kwargs = {'identifier': epc} or {'id': epc_pk}
        biz_locations = EntryEvent.objects.order_by(
            'event__event_time'
        ).select_related(
            'event'
        ).filter(**kwargs).only('event__id',
                                'event__event_time',
                                'event__biz_location')
        # now get the GPS info for each biz_location
        ret = []
        for location in biz_locations:
            gl = GeoEvent(
                event_time=location.event.event_time,
                biz_location=location.event.biz_location
            )
            lat, long = models.Location.objects.values_list(
                'latitude', 'longitude').get(
                SGLN=location.event.biz_location
            )
            gl.latitude = lat
            gl.longitude = long
            gl.id = location.event.id
            serializer = GeoEventSerializer(gl)
            ret.append(serializer.data)
        return Response(ret)
