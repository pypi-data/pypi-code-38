from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer
from aparnik.contrib.segments.api.serializers import BaseSegmentListPolymorphicSerializer
from aparnik.settings import aparnik_settings
from ..models import Teacher

UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


# Teacher List
class TeacherListSerializer(BaseModelListSerializer):
    user_obj = serializers.SerializerMethodField()
    models_api = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TeacherListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Teacher
        fields = BaseModelListSerializer.Meta.fields + [
            'user_obj',
            'start_date',
            'models_api',
        ]

    def get_user_obj(self, obj):
        return UserSummeryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data

    def get_models_api(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_models_uri())

# Teacher details
# TODO: use teacher details in base polymorphic serializers
class TeacherDetailsSerializers(TeacherListSerializer, BaseModelDetailSerializer):
    slider_segment = serializers.SerializerMethodField()
    models = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TeacherListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Teacher
        fields = TeacherListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'biography',
            'slider_segment',
            'models',
        ]

    def get_slider_segment(self, obj):
        return BaseSegmentListPolymorphicSerializer(obj.slider_segment_obj, many=False, read_only=True, context=self.context).data

    def get_models(self, obj):
        # teacher.course_set.active()
        return 1212


# Teacher List Polymorphic
class TeacherListPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            Teacher: TeacherListSerializer,
        }
        super(TeacherListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Teacher Details Polymorphic
class TeacherDetailsPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            Teacher: TeacherDetailsSerializers,
        }
        super(TeacherDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
