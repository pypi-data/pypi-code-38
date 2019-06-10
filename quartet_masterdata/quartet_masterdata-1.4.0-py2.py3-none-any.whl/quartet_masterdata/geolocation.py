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
import json
from datetime import datetime
from typing import List
from rest_framework import serializers


class GeoEvent:
    '''
    Used as a result structure for geo history queries
    '''

    def __init__(self, id = None, biz_location: str = None,
                 event_time: datetime = None,
                 longitude: float = None, latitude: float = None):
        self.id = id,
        self.biz_location = biz_location
        self.event_time = event_time
        self.longitude = longitude
        self.latitude = latitude

    def to_json(self):
        return json.dumps(self)


class GeoEventSerializer(serializers.Serializer):
    '''
    Used to serialize GeoEvent during DRF calls to different formats.
    '''
    id = serializers.UUIDField()
    biz_location = serializers.CharField(max_length=150)
    event_time = serializers.DateTimeField()
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()


# typed list for code hints, etc
GeoEventList = List[GeoEvent]
