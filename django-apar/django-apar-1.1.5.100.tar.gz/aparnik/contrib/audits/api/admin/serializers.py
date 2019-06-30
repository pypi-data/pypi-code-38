from rest_framework import serializers

from aparnik.contrib.audits.models import Audit
from aparnik.contrib.basemodels.api.admin.serializers import BaseModelAdminSerializer


class AuditAdminListSerializer(BaseModelAdminSerializer):

    def __init__(self, *args, **kwargs):
        super(AuditAdminListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Audit
        fields = BaseModelAdminSerializer.Meta.fields + [
            'ip',
        ]

        read_only_fields = BaseModelAdminSerializer.Meta.read_only_fields + [
            'ip',
        ]
