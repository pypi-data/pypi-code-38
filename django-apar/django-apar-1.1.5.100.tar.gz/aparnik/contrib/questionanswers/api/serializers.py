from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from aparnik.contrib.reviews.api.serializers import BaseReviewDetailsSerializer, BaseReviewListSerializer
from ..models import QA
from aparnik.contrib.basemodels.models import BaseModel


# QA List Serializer
class QAListSerializer(BaseReviewListSerializer):
    files = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(QAListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = QA
        fields = BaseReviewListSerializer.Meta.fields + [
            'files',
        ]
        read_only_fields = BaseReviewListSerializer.Meta.read_only_fields + []

    def get_files(self, obj):
        from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
        return FileFieldListSerailizer(obj.files, many=True, read_only=True, context=self.context).data if not None else None


# QA Details Serializer
class QADetailSerializer(QAListSerializer, BaseReviewDetailsSerializer):

    def __init__(self, *args, **kwargs):
        super(QADetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = QA
        fields = QAListSerializer.Meta.fields + BaseReviewDetailsSerializer.Meta.fields + [

        ]
        read_only_fields = QAListSerializer.Meta.read_only_fields + BaseReviewDetailsSerializer.Meta.read_only_fields + []


# QA Create Serializer
class QACreateSerializer(QADetailSerializer):
    model_obj_id = serializers.IntegerField(write_only=True, required=True)
    parent_obj_id = serializers.IntegerField(write_only=True, required=False)
    resourcetype = serializers.SerializerMethodField()

    class Meta:
        model = QA
        fields = QADetailSerializer.Meta.fields + [
            'model_obj_id',
            'parent_obj_id',
            'resourcetype',

        ]
        read_only_fields = QADetailSerializer.Meta.read_only_fields + []

    def validate_model_obj_id(self, value):
        try:
            basemodel = get_object_or_404(BaseModel.objects.all(), id=value)
            return value
        except Exception as e:
            raise serializers.ValidationError(_("Base Model not found"))

    def validate_parent_obj_id(self, value):
        try:
            qa = get_object_or_404(QA.objects.all(), id=value)
            return value
        except Exception as e:
            raise serializers.ValidationError(_("QA Parent not found"))

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_resourcetype(self, obj):
        return 'QA'
