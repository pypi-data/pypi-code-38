from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.api.serializers import ModelSerializer
from aparnik.utils.utils import is_app_installed
from ..models import BaseSegment, SegmentSort, PageSort


# Base Segment ListSegmentReview
class SegmentSortListSerializer(ModelSerializer):

    model = serializers.SerializerMethodField()
    resourcetype = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SegmentSortListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = SegmentSort
        fields = [
            'id',
            'model',
            'sort',
            'resourcetype'
        ]
        read_only_fields = ['id', 'model', 'sort']

    def get_model(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.model_obj.get_real_instance(), many=False, read_only=True, context=self.context).data

    def get_resourcetype(self, obj):
        return 'SegmentSort'


class PageSortListSerializer(ModelSerializer):

    model = serializers.SerializerMethodField()
    resourcetype = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(PageSortListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = PageSort
        fields = [
            'id',
            'model',
            'sort',
            'resourcetype'
        ]
        read_only_fields = ['id', 'model', 'sort']

    def get_model(self, obj):
        from aparnik.contrib.segments.api.serializers import BaseSegmentListPolymorphicSerializer
        return BaseSegmentListPolymorphicSerializer(obj.segment_obj.get_real_instance(), many=False, read_only=True, context=self.context).data

    def get_resourcetype(self, obj):
        return 'PageSort'


class BaseSegmentListSerializer(ModelSerializer):
    url_list = serializers.SerializerMethodField()
    models = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BaseSegmentListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseSegment
        fields = [
            'id',
            'title',
            'models',
            'url_list',
        ]
        read_only_fields = ['id']

    def get_models(self, obj):
        return SegmentSortListSerializer(obj.segment_sort_segment.all()[:10], many=True, read_only=True, context=self.context).data

    def get_url_list(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_list_model_uri())


    # Base Segment Details
class BaseSegmentDetailSerializer(BaseSegmentListSerializer):

    def __init__(self, *args, **kwargs):
        super(BaseSegmentDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseSegment
        fields = BaseSegmentListSerializer.Meta.fields + [

        ]
        read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


# Base Segment List Polymorphic
class BaseSegmentListPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):

        model_serializer_mapping = {
            BaseSegment: BaseSegmentListSerializer
        }

        # Segment Button
        if is_app_installed('aparnik.contrib.buttons'):
            from aparnik.contrib.buttons.models import ButtonSegment
            from aparnik.contrib.buttons.api.serializers import SegmentButtonListSerializer
            model_serializer_mapping[ButtonSegment] = SegmentButtonListSerializer

        # Segment Category
        if is_app_installed('aparnik.contrib.categories'):
            from aparnik.contrib.categories.models import CategorySegment
            from aparnik.contrib.categories.api.serializers import SegmentCategoryListSerializer
            model_serializer_mapping[CategorySegment] = SegmentCategoryListSerializer

        # Segment Slider
        if is_app_installed('aparnik.contrib.sliders'):
            from aparnik.contrib.sliders.models import Slider
            from aparnik.contrib.sliders.api.serializers import SegmentSliderListSerializer
            model_serializer_mapping[Slider] = SegmentSliderListSerializer

        # Segment Review
        if is_app_installed('aparnik.contrib.reviews'):
            from aparnik.contrib.reviews.models import BaseReviewSegment
            from aparnik.contrib.reviews.api.serializers import SegmentBaseReviewListSerializer
            model_serializer_mapping[BaseReviewSegment] = SegmentBaseReviewListSerializer

        # Segment Social network
        if is_app_installed('aparnik.contrib.socials'):
            from aparnik.contrib.socials.models import SocialNetworkSegment
            from aparnik.contrib.socials.api.serializers import SegmentSocialNetworkListSerializer
            model_serializer_mapping[SocialNetworkSegment] = SegmentSocialNetworkListSerializer

        # Segment Course
        if is_app_installed('aparnik.packages.educations.courses'):
            from aparnik.packages.educations.courses.models import CourseSegment
            from aparnik.packages.educations.courses.api.serializers import SegmentCourseListSerializer
            model_serializer_mapping[CourseSegment] = SegmentCourseListSerializer

        # Segment books
        if is_app_installed('aparnik.packages.educations.books'):
            from aparnik.packages.educations.books.models import BookSegment
            from aparnik.packages.educations.books.api.serializers import SegmentBookListSerializer
            model_serializer_mapping[BookSegment] = SegmentBookListSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(BaseSegmentListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Base Segment Details Polymorphic
class BaseSegmentDetailsPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        model_serializer_mapping = {
            BaseSegment: BaseSegmentDetailSerializer
        }

        # Segment Button
        if is_app_installed('aparnik.contrib.buttons'):
            from aparnik.contrib.buttons.models import ButtonSegment
            from aparnik.contrib.buttons.api.serializers import SegmentButtonDetailSerializer
            model_serializer_mapping[ButtonSegment] = SegmentButtonDetailSerializer

        # Segment Category
        if is_app_installed('aparnik.contrib.categories'):
            from aparnik.contrib.categories.models import CategorySegment
            from aparnik.contrib.categories.api.serializers import SegmentCategoryDetailSerializer
            model_serializer_mapping[CategorySegment] = SegmentCategoryDetailSerializer

        # Segment Slider
        if is_app_installed('aparnik.contrib.sliders'):
            from aparnik.contrib.sliders.models import Slider
            from aparnik.contrib.sliders.api.serializers import SegmentSliderDetailSerializer
            model_serializer_mapping[Slider] = SegmentSliderDetailSerializer

        # Segment Review
        if is_app_installed('aparnik.contrib.reviews'):
            from aparnik.contrib.reviews.models import BaseReviewSegment
            from aparnik.contrib.reviews.api.serializers import SegmentBaseReviewDetailSerializer
            model_serializer_mapping[BaseReviewSegment] = SegmentBaseReviewDetailSerializer

        # Segment Social network
        if is_app_installed('aparnik.contrib.socials'):
            from aparnik.contrib.socials.models import SocialNetworkSegment
            from aparnik.contrib.socials.api.serializers import SegmentSocialNetworkDetailSerializer
            model_serializer_mapping[SocialNetworkSegment] = SegmentSocialNetworkDetailSerializer

        # Segment Course
        if is_app_installed('aparnik.packages.educations.courses'):
            from aparnik.packages.educations.courses.models import CourseSegment
            from aparnik.packages.educations.courses.api.serializers import SegmentCourseDetailSerializer
            model_serializer_mapping[CourseSegment] = SegmentCourseDetailSerializer

        # Segment books
        if is_app_installed('aparnik.packages.educations.books'):
            from aparnik.packages.educations.books.models import BookSegment
            from aparnik.packages.educations.books.api.serializers import SegmentBookDetailSerializer
            model_serializer_mapping[BookSegment] = SegmentBookDetailSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(BaseSegmentDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
