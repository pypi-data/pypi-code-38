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

from quartet_masterdata import models
from quartet_masterdata import serializers
from rest_framework.viewsets import ModelViewSet


class LocationViewSet(ModelViewSet):
    '''
    CRUD ready model view for the Location model.
    '''
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    search_fields = ['GLN13', 'SGLN', 'address1', 'address2',
                     'address3', 'city', 'country', 'name',
                     'postal_code', 'state_province']


class LocationTypeViewSet(ModelViewSet):
    '''
    CRUD ready model view for the LocationType model.
    '''
    queryset = models.LocationType.objects.all()
    serializer_class = serializers.LocationTypeSerializer


class LocationIdentifierViewSet(ModelViewSet):
    '''
    CRUD ready model view for the LocationIdentifier model.
    '''
    queryset = models.LocationIdentifier.objects.all()
    serializer_class = serializers.LocationIdentifierSerializer


class LocationFieldViewSet(ModelViewSet):
    '''
    CRUD ready model view for the LocationField model.
    '''
    queryset = models.LocationField.objects.all()
    serializer_class = serializers.LocationFieldSerializer


class MeasurementViewSet(ModelViewSet):
    '''
    CRUD ready model view for the Measurement model.
    '''
    queryset = models.Measurement.objects.all()
    serializer_class = serializers.MeasurementSerializer


class CompanyViewSet(ModelViewSet):
    '''
    CRUD ready model view for the Company model.
    '''
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    search_fields = ['GLN13', 'SGLN', 'address1', 'address2', 'address3',
                     'city', 'country', 'gs1_company_prefix', 'name',
                     'postal_code', 'state_province']


class CompanyTypeViewSet(ModelViewSet):
    '''
    CRUD ready model view for the Company Type model.
    '''
    queryset = models.CompanyType.objects.all()
    serializer_class = serializers.CompanyTypeSerializer


class TradeItemViewSet(ModelViewSet):
    '''
    CRUD ready model view for the TradeItem model.
    '''
    queryset = models.TradeItem.objects.all()
    serializer_class = serializers.TradeItemSerializer
    search_fields = ['GTIN14', 'NDC', 'additional_id', 'country_of_origin',
                     'description_short', 'dosage_form_type', 'drained_weight',
                     'drained_weight_uom', 'functional_name', 'gross_weight',
                     'gross_weight_uom', 'label_description', 'manufacturer_name',
                     'net_content_description', 'net_weight', 'net_weight_uom',
                     'regulated_product_name', 'strength_description',
                     'trade_item_description']


class TradeItemFieldViewSet(ModelViewSet):
    '''
    CRUD ready model view for the TradeItemField model.
    '''
    queryset = models.TradeItemField.objects.all()
    serializer_class = serializers.TradeItemFieldSerializer
