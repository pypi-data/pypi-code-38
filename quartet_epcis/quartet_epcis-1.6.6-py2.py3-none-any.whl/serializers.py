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

from rest_framework.serializers import ModelSerializer
from quartet_epcis.models import entries, events, headers


class EntrySerializer(ModelSerializer):
    class Meta:
        model = entries.Entry
        fields = '__all__'


class EntryEventSerialzier(ModelSerializer):
    class Meta:
        model = entries.EntryEvent
        fields = '__all__'


class EventSerializer(ModelSerializer):
    class Meta:
        model = events.Event
        fields = '__all__'


class TransformationIDSerializer(ModelSerializer):
    class Meta:
        model = events.TransformationID
        fields = '__all__'


class ErrorDeclarationSerializer(ModelSerializer):
    class Meta:
        model = events.ErrorDeclaration
        fields = '__all__'


class QuantityElementSerializer(ModelSerializer):
    class Meta:
        model = events.QuantityElement
        fields = '__all__'


class BusinessTransactionSerializer(ModelSerializer):
    class Meta:
        model = events.BusinessTransaction
        fields = '__all__'


class InstanceLotMasterDataSerializer(ModelSerializer):
    class Meta:
        model = events.InstanceLotMasterData
        fields = '__all__'


class SourceSerializer(ModelSerializer):
    class Meta:
        model = events.Source
        fields = '__all__'


class SourceEventSerializer(ModelSerializer):
    class Meta:
        model = events.SourceEvent
        fields = '__all__'


class DestinationSerializer(ModelSerializer):
    class Meta:
        model = events.Destination
        fields = '__all__'


class DestinationEventSerializer(ModelSerializer):
    class Meta:
        model = events.DestinationEvent
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    class Meta:
        model = headers.Message
        fields = '__all__'
