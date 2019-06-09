from django.utils.text import Truncator
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

import datetime

from aparnik.api.serializers import ModelSerializer
from aparnik.utils.utils import is_app_installed
from aparnik.settings import Setting
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
from aparnik.contrib.categories.api.serializers import CategoryDetailsPolymorphicSerializer
from aparnik.packages.shops.products.api.serializers import ProductDetailSerializer, ProductListSerializer
from aparnik.packages.shops.files.api.serializers import FileListSerializer, FileDetailSerializer
from aparnik.packages.educations.progresses.api.serializers import ProgressListSerializer
from ..models import Course, CourseFile, BaseCourse, CourseSummary


# Total TIme Details Serializer
class CourseSummaryDetailSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(CourseSummaryDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = CourseSummary
        fields = [
            'total_time',
            'file_count',
            'file_count_preview',
            'type',
        ]


# Base Course Details Serializer
class BaseCourseListSerializer(ProductListSerializer):
    summary = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = BaseCourse
        fields = ProductListSerializer.Meta.fields + [
            'summary',
            'short_description',
        ]
        read_only_fields = ProductListSerializer.Meta.read_only_fields + ['summary',
                                                                          'short_description'
                                                                          ]

    def get_summary(self, obj):
        return CourseSummaryDetailSerializer(obj.total_times.all(), many=True, read_only=True,
                                             context=self.context).data

    def get_short_description(self, obj):
        return Truncator(obj.description).words(30)


# Base Course Details Serializer
class BaseCourseDetailsSerializer(BaseCourseListSerializer, ProductDetailSerializer):
    class Meta:
        model = BaseCourse
        fields = BaseCourseListSerializer.Meta.fields + ProductDetailSerializer.Meta.fields + [
            'description',
        ]
        read_only_fields = ProductDetailSerializer.Meta.read_only_fields + BaseCourseListSerializer.Meta.read_only_fields + []


# Course List Serializer
class CourseListSerializer(BaseCourseListSerializer):
    cover = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    child_count = serializers.SerializerMethodField()
    url_file = serializers.SerializerMethodField()
    url_file_create = serializers.SerializerMethodField()
    url_child = serializers.SerializerMethodField()
    dependency_title = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CourseListSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context']

    class Meta:
        model = Course
        fields = BaseCourseListSerializer.Meta.fields + [
            'cover',
            'banner',
            'child_count',
            'sort',
            'is_free',
            'url_child',
            'depth',
            'url_file',
            'url_file_create',
            'dependency_title',
            'publish_month',
            'publish_week',
            'publish_day',
            'teachers',
            'progress_percentage',
        ]
        read_only_fields = BaseCourseListSerializer.Meta.read_only_fields + ['cover', 'banner',
                                                                             'child_count', 'url_child',
                                                                             'url_file', 'url_file_create',
                                                                             'dependency_title', 'teachers',
                                                                             'progress_percentage'
                                                                             ]

    def get_cover(self, obj):
        return FileFieldListSerailizer(obj.cover, many=False, read_only=True,
                                       context=self.context).data if obj.cover else None

    def get_banner(self, obj):
        return FileFieldListSerailizer(obj.banner, many=False, read_only=True,
                                       context=self.context).data if obj.banner else None

    def get_child_count(self, obj):
        return Course.objects.childs_count(course_obj=obj.id)

    def get_url_child(self, obj):
        if Course.objects.childs_count(obj) > 0:
            return self.context['request'].build_absolute_uri(obj.get_api_child_uri())
        return None

    def get_url_file(self, obj):
        if obj.coursefile_set.count() > 0:
            return self.context['request'].build_absolute_uri(obj.get_api_file_uri())
        return None

    def get_url_file_create(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_file_create_uri())

    # def get_file_count(self, obj):
    #     return obj.get_files_count()

    def get_dependency_title(self, obj):
        return obj.dependency_obj.title if obj.dependency_obj is not None else None

    def get_teachers(self, obj):
        from aparnik.packages.educations.teachers.api.serializers import TeacherListPolymorphicSerializer
        return TeacherListPolymorphicSerializer(obj.teachers, many=True, read_only=True,
                                                context=self.context).data

    def get_progress_percentage(self, obj):
        user = self.context['request'].user
        if user.is_authenticated():
            progress_summary = obj.progress_summaries.this_user(user).last()
            if progress_summary:
                return progress_summary.percentage
        return 0.0


# Course Details Serializer
class CourseDetailSerializer(CourseListSerializer, BaseCourseDetailsSerializer):
    parent = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CourseDetailSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Course
        fields = CourseListSerializer.Meta.fields + BaseCourseDetailsSerializer.Meta.fields + [
            'category',
            'parent',
        ]
        read_only_fields = CourseListSerializer.Meta.read_only_fields + BaseCourseDetailsSerializer.Meta.read_only_fields + [
            'category',
            'parent']

    def get_category(self, obj):
        return CategoryDetailsPolymorphicSerializer(obj.category_obj, many=False, read_only=True,
                                                    context=self.context).data

    def get_parent(self, obj):
        return BaseCourseListPolymorphicSerializer(obj.parent_obj, many=False, read_only=True,
                                                   context=self.context).data if obj.parent_obj is not None else None

    def get_share_string(self, obj):
        url = Setting.objects.get(key='APP_LANDING_PAGE_URL').get_value()
        return '%s \n %s \n %s' % (url, obj.title, self.get_short_description(obj))


class CourseCreateSerializer(CourseDetailSerializer, BaseCourseDetailsSerializer):
    parent_obj_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    banner_id = serializers.IntegerField(required=True, write_only=True)
    cover_id = serializers.IntegerField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super(CourseCreateSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Course
        fields = CourseDetailSerializer.Meta.fields + BaseCourseDetailsSerializer.Meta.fields + [
            'parent_obj_id',
            'banner_id',
            'cover_id',
        ]
        read_only_fields = CourseDetailSerializer.Meta.read_only_fields + BaseCourseDetailsSerializer.Meta.read_only_fields + [
        ]


# File List Serializer
class CourseFileListSerializer(FileListSerializer):
    url_progress_set = serializers.SerializerMethodField()
    progress_status = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CourseFileListSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = CourseFile
        fields = FileListSerializer.Meta.fields + [
            'sort',
            'time',
            'url_progress_set',
            'progress_status',
        ]
        read_only_fields = FileListSerializer.Meta.read_only_fields + ['url_progress_set',
                                                                       'progress_status', 'time']

    def get_url_progress_set(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_progress_set_uri())

    def get_progress_status(self, obj):
        user = self.context['request'].user
        progress = obj.progresses_set.this_user(user)
        if progress.count() > 0:
            return ProgressListSerializer(progress.last(), many=False, read_only=True, context=self.context).data
        return None

    def get_time(self, obj):
        return str(datetime.timedelta(seconds=obj.seconds))


# File Details Serializer
class CourseFileDetailSerializer(CourseFileListSerializer, FileDetailSerializer):
    course = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CourseFileDetailSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = CourseFile
        fields = CourseFileListSerializer.Meta.fields + FileDetailSerializer.Meta.fields + [
            'course',
        ]
        read_only_fields = CourseFileListSerializer.Meta.read_only_fields + FileDetailSerializer.Meta.read_only_fields + [
            'course']

    def get_course(self, obj):
        return BaseCourseListPolymorphicSerializer(obj.course_obj, many=False, read_only=True,
                                                   context=self.context).data


class CourseFileCreateSerializer(CourseFileDetailSerializer, FileDetailSerializer):
    file_obj_id = serializers.IntegerField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super(CourseFileCreateSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = CourseFile
        fields = CourseFileDetailSerializer.Meta.fields + FileDetailSerializer.Meta.fields + [
            'password',
            'iv',
            'file_obj_id'
        ]
        extra_kwargs = {'course_obj_id': {'write_only': True}}
        read_only_fields = CourseFileDetailSerializer.Meta.read_only_fields + FileDetailSerializer.Meta.read_only_fields + \
                           []


# Base Course List Polymorphic
class BaseCourseListPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            BaseCourse: BaseCourseListSerializer,
            Course: CourseListSerializer,
        }
        super(BaseCourseListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Base Course Details Polymorphic
class BaseCourseDetailsPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            BaseCourse: BaseCourseDetailsSerializer,
            Course: CourseDetailSerializer,
        }
        super(BaseCourseDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.api.serializers import BaseSegmentListSerializer, BaseSegmentDetailSerializer
    from ..models import CourseSegment


    # Base Segment ListSegmentReview
    class SegmentCourseListSerializer(BaseSegmentListSerializer):
        class Meta:
            model = CourseSegment
            fields = BaseSegmentListSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


    # Book Segment Details
    class SegmentCourseDetailSerializer(BaseSegmentDetailSerializer, SegmentCourseListSerializer):
        class Meta:
            model = CourseSegment
            fields = SegmentCourseListSerializer.Meta.fields + BaseSegmentDetailSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentDetailSerializer.Meta.read_only_fields + SegmentCourseListSerializer.Meta.read_only_fields + []
