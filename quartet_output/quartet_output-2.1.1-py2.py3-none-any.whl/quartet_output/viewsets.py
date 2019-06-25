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
from quartet_output import models
from quartet_output import serializers
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class EndPointViewSet(ModelViewSet):
    '''
    CRUD ready model view for the EndPoint model.
    '''
    queryset = models.EndPoint.objects.all()
    serializer_class = serializers.EndPointSerializer


class EPCISOutputCriteriaViewSet(ModelViewSet):
    '''
    CRUD ready model view for the EPCISOutputCriteria model.
    '''
    queryset = models.EPCISOutputCriteria.objects.all()
    serializer_class = serializers.EPCISOutputCriteriaSerializer

class AuthenticationInfoViewSet(ModelViewSet):
    '''
    CRUD ready model view for the AuthenticationInfo model.
    '''
    queryset = models.AuthenticationInfo.objects.all()
    serializer_class = serializers.AuthenticationInfoSerializer

class ReadOnlyCriteriaViewSet(ReadOnlyModelViewSet):
    queryset = models.EPCISOutputCriteria.objects.all()
    serializer_class = serializers.ReadOnlyEPCISOutputCriteriaSerializer

