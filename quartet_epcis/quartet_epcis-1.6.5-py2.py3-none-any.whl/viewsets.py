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

from rest_framework import viewsets
from quartet_epcis.models import events, entries, headers
from quartet_epcis import serializers

class EntryViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle the management of Entries.
    '''
    queryset = entries.Entry.objects.all()
    serializer_class = serializers.EntrySerializer
    search_fields = ['=identifier',]

class EntryEventViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle EntryEvents.
    '''
    queryset = entries.EntryEvent.objects.all()
    serializer_class = serializers.EntrySerializer


class EventViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle Events.
    '''
    queryset = events.Event.objects.all()
    serializer_class = serializers.EventSerializer
    search_fields = ['=event_id',]
    filter_fields = '__all__'


class TransformationIDViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle TransformationIDs.
    '''
    queryset = events.TransformationID.objects.all()
    serializer_class = serializers.TransformationIDSerializer


class ErrorDeclarationViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle ErrorDeclarations.
    '''
    queryset = events.ErrorDeclaration.objects.all()
    serializer_class = serializers.ErrorDeclarationSerializer


class QuantityElementViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle QuantityElements.
    '''
    queryset = events.QuantityElement.objects.all()
    serializer_class = serializers.QuantityElementSerializer


class BusinessTransactionViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle BusinessTransactions.
    '''
    queryset = events.BusinessTransaction.objects.all()
    serializer_class = serializers.BusinessTransactionSerializer


class InstanceLotMasterDataViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle InstanceLotMasterData.
    '''
    queryset = events.InstanceLotMasterData.objects.all()
    serializer_class = serializers.InstanceLotMasterDataSerializer


class SourceViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle Sources.
    '''
    queryset = events.Source.objects.all()
    serializer_class = serializers.SourceSerializer


class SourceEventViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle SourceEvents.
    '''
    queryset = events.SourceEvent.objects.all()
    serializer_class = serializers.SourceEventSerializer


class DestinationViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle Destinations.
    '''
    queryset = events.Destination.objects.all()
    serializer_class = serializers.DestinationSerializer


class DestinationEventViewSet(viewsets.ModelViewSet):
    '''
    The default viewset to handle DestinationEvents.
    '''
    queryset = events.DestinationEvent.objects.all()
    serializer_class = serializers.DestinationEventSerializer


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Default view for messages.
    '''
    queryset = headers.Message.objects.all()
    serializer_class = serializers.MessageSerializer
