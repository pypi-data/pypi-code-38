""" Result Serializers
"""
from rest_framework.serializers import JSONField, CharField

from core_main_app.commons.serializers import BasicSerializer


class QueryExecuteSerializer(BasicSerializer):
    query = CharField(required=True)
    options = JSONField(required=False)
    templates = JSONField(required=False)
