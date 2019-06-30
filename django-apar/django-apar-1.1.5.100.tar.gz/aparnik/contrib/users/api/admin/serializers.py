from rest_framework import serializers

from aparnik.contrib.users.models import User
from aparnik.contrib.users.api.serializers import UserSummaryListSerializer


class UserAdminListSerializer(UserSummaryListSerializer):
    id = serializers.SerializerMethodField()
    sort_count = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(UserAdminListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = UserSummaryListSerializer.Meta.fields + [
            'id',
            'sort_count',
        ]

        read_only_fields = UserSummaryListSerializer.Meta.read_only_fields + [
            'id',
            'sort_count',
        ]

    def get_id(self, obj):
        return obj.pk

    def get_sort_count(self, obj):
        return obj.sort_count if hasattr(obj, 'sort_count') else 0
