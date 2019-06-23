# -*- coding: utf-8 -*-


from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer
from aparnik.contrib.users.api.serializers import UserSummaryListSerializer
from aparnik.packages.educations.progresses.models import Progresses, ProgressSummary
# from aparnik.packages.educations.courses.models import File


class ProgressSummaryListSerializer(BaseModelListSerializer):

    def __init__(self, *args, **kwargs):
        super(ProgressSummaryListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ProgressSummary
        fields = [
            'percentage',
        ]
        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + ['percentage']


class ProgressListSerializer(BaseModelListSerializer):

    def __init__(self, *args, **kwargs):
        super(ProgressListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Progresses
        fields = BaseModelListSerializer.Meta.fields + [
            'status',
        ]
        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + ['status']


# from aparnik.packages.educations.courses.api.serializers import BaseFileListSerializer
# class BaseProgressListSerializer(BaseModelListSerializer):
#     user = serializers.SerializerMethodField()
#     overall_progress = serializers.SerializerMethodField()
#
#     def __init__(self, *args, **kwargs):
#         super(BaseProgressListSerializer, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = Progresses
#         fields = BaseModelListSerializer.Meta.fields + [
#             'user',
#             'overall_progress',
#         ]
#         read_only_fields = BaseModelListSerializer.Meta.read_only_fields + []
#
#     def get_user(self, obj):
#         return UserSummaryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data
#
#     def get_overall_progress(self, obj):
#         return Progresses.objects.get_overall_progress(obj.user_obj)
#
#
# class BaseProgressDetailsSerializer(BaseProgressListSerializer, BaseModelDetailSerializer):
#     course = serializers.SerializerMethodField()
#
#     def __init__(self, *args, **kwargs):
#         super(BaseProgressDetailsSerializer, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = BaseProgresses
#         fields = BaseModelDetailSerializer.Meta.fields + BaseProgressListSerializer.Meta.fields + []
#         read_only_fields = BaseProgressListSerializer.Meta.read_only_fields + BaseModelDetailSerializer.Meta.read_only_fields + []
#
#
# class ProgressListSerializer(BaseProgressListSerializer):
#
#     class Meta:
#         model = Progresses
#         fields = BaseProgressListSerializer.Meta.fields + []
#
#
# class ProgressDetailsSerilizer(ProgressListSerializer, BaseProgressDetailsSerializer):
#     # file = serializers.SerializerMethodField()
#     #
#     # file_obj_id = serializers.IntegerField(required=True, write_only=True)
#
#     def __init__(self, *args, **kwargs):
#         super(ProgressDetailsSerilizer, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = Progresses
#         fields = ProgressListSerializer.Meta.fields + BaseProgressDetailsSerializer.Meta.fields + [
#             'file_obj',
#             # 'file_obj_id',
#             'status',
#             'is_manual',
#         ]
#
#         validators = []
#
#     # def get_file(self, obj):
#     #     return BaseFileListSerializer(obj.file_obj, many=False, read_only=True,
#     #                                   context=self.context).data
#     #
#     # def create(self, validated_data):
#     #     file_obj = File.objects.filter(id=validated_data.pop('file_obj_id')).first()
#     #     progress = Progresses.objects.create(file_obj=file_obj, **validated_data)
#     #     return progress
#     #
#     # def update(self, instance, validated_data):
#     #     instance.file_obj = File.objects.filter(id=validated_data.get('file_obj_id', None)).get()
#     #     instance.status = validated_data.get('status', None)
#     #     instance.is_manual = validated_data.get('is_manual', None)
#     #     instance.save()
#     #
#     #     return instance
#

# Polymorphic
class BaseProgressListPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            # BaseProgresses: BaseProgressListSerializer,
            # Progresses: ProgressListSerializer,
        }
        super(BaseProgressListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


class BaseProgressDetailsPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            # BaseProgresses: BaseProgressDetailsSerializer,
            # Progresses: ProgressDetailsSerilizer,
        }
        super(BaseProgressDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
