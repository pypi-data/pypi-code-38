from rest_framework import serializers

from aparnik.contrib.basemodels.api.admin.serializers import BaseModelAdminSerializer


from aparnik.contrib.users.api.serializers import UserSummaryListSerializer
from aparnik.packages.educations.teachers.models import Teacher


class TeacherAdminListSerializer(BaseModelAdminSerializer):

    user = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TeacherAdminListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Teacher
        fields = BaseModelAdminSerializer.Meta.fields + [
            'user',
        ]

        read_only_fields = BaseModelAdminSerializer.Meta.read_only_fields + [
            'user',
        ]

    def get_user(self, obj):
        return UserSummaryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data