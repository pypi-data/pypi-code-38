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
from rest_framework.serializers import ModelSerializer


class EndPointSerializer(ModelSerializer):
    """
    Default serializer for the EndPoint model.
    """

    class Meta:
        model = models.EndPoint
        fields = '__all__'


class AuthenticationInfoSerializer(ModelSerializer):
    """
    Default serializer for the AuthenticationInfo model.
    """

    class Meta:
        model = models.AuthenticationInfo
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class ReadOnlyEPCISOutputCriteriaSerializer(ModelSerializer):
    """
    Default read_only serializer for the EPCISOutputCriteria model.
    """
    end_point = EndPointSerializer(many=False, read_only=True)
    authentication_info = AuthenticationInfoSerializer(many=False,
                                                       read_only=True)

    class Meta:
        model = models.EPCISOutputCriteria
        fields = '__all__'


class EPCISOutputCriteriaSerializer(ModelSerializer):
    """
    Default serializer for the EPCISOutputCriteria model.
    """

    class Meta:
        model = models.EPCISOutputCriteria
        fields = '__all__'
