from rest_framework import serializers

from aparnik.contrib.basemodels.models import BaseModel


class BaseModelAdminSerializer(serializers.ModelSerializer):
    sort_count = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BaseModelAdminSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseModel
        fields = [
            'id',
            'sort_count',
        ]

        read_only_fields = [
            'id',
            'sort_count',
        ]

    def get_sort_count(self, obj):
        return obj.sort_count if hasattr(obj, 'sort_count') else 0
