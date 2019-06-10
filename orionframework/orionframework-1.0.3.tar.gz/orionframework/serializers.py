from rest_framework import serializers, fields


class AnyField(fields.Field):

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class ListIDSerializer(serializers.Serializer):
    ids = fields.ListField(child=AnyField(required=True))
