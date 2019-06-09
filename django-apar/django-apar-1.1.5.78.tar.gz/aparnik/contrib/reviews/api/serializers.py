# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.settings import aparnik_settings
from aparnik.utils.utils import is_app_installed
from aparnik.contrib.reviews.models import Review, Like, BaseReview, ReviewSummary
from aparnik.contrib.basemodels.models import BaseModel
from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer

UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


# Base Review List Serializer
class BaseReviewListSerializer(BaseModelListSerializer):
    url_like = serializers.SerializerMethodField()
    url_dislike = serializers.SerializerMethodField()
    url_action_like = serializers.SerializerMethodField()
    url_action_dislike = serializers.SerializerMethodField()
    url_action_base_review_status_set = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    childs = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()
    is_dislike = serializers.SerializerMethodField()
    has_permit_change_status = serializers.SerializerMethodField()
    has_permit_replay = serializers.SerializerMethodField()
    has_permit_edit = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BaseReviewListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseReview
        fields = BaseModelListSerializer.Meta.fields + [
            'title',
            'description',
            'url_like',
            'url_dislike',
            'url_action_like',
            'url_action_dislike',
            'url_action_base_review_status_set',
            'like_count',
            'dislike_count',
            'user',
            'is_published',
            'created_at',
            'childs',
            'has_permit_change_status',
            'has_permit_replay',
            'has_permit_edit',
            'is_like',
            'is_dislike',
        ]
        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + ['like_count', 'dislike_count', 'childs',
                                                                            'is_like',
                                                                            'is_dislike',
                                                                            ]

    def get_url_like(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_like_uri())

    def get_url_dislike(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_dislike_uri())

    def get_url_action_like(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_action_like())

    def get_url_action_dislike(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_action_dislike())

    def get_like_count(self, obj):
        return Like.objects.likes_count(review_obj=obj.id)

    def get_dislike_count(self, obj):
        return Like.objects.dislikes_count(review_obj=obj.id)

    def get_user(self, obj):
        return UserSummeryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data

    def get_childs(self, obj):
        return BaseReviewListPolymorphicSerializer(obj.child.all()[:2], many=True, read_only=True, context=self.context).data if obj.child.all() else None

    def get_url_action_base_review_status_set(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_action_base_review_status_set())

    def get_has_permit_change_status(self, obj):
        user = self.context['request'].user
        return obj.has_permit_change_status(user)

    def get_has_permit_replay(self, obj):
        user = self.context['request'].user
        return obj.has_permit_replay(user)

    def get_has_permit_edit(self, obj):
        user = self.context['request'].user
        return obj.has_permit_edit(user)

    def get_is_like(self, obj):
        user = self.context['request'].user
        return obj.is_like(user)

    def get_is_dislike(self, obj):
        user = self.context['request'].user
        return obj.is_dislike(user)



# Base Review Details Serializer
class BaseReviewDetailsSerializer(BaseReviewListSerializer, BaseModelDetailSerializer):
    model = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BaseReviewDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseReview
        fields = BaseReviewListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'model',
        ]
        read_only_fields = BaseReviewListSerializer.Meta.read_only_fields + BaseModelDetailSerializer.Meta.read_only_fields + ['is_published']

    # def get_url(self, obj):
    #     return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_model(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.model_obj.get_real_instance(), many=False, read_only=True, context=self.context).data


class ReviewSummaryListSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(ReviewSummaryListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ReviewSummary
        fields = [
            'id',
            'rate',
            'count',
            'percentage',
        ]
        read_only_fields = []


# Review List Serializer
class ReviewListSerializer(BaseReviewListSerializer):

    def __init__(self, *args, **kwargs):
        super(ReviewListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Review
        fields = BaseReviewListSerializer.Meta.fields + [
            'rate'
        ]
        read_only_fields = BaseReviewListSerializer.Meta.read_only_fields + []


# Review Details Serializer
class ReviewDetailsSerializer(ReviewListSerializer, BaseReviewDetailsSerializer):

    def __init__(self, *args, **kwargs):
        super(ReviewDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Review
        fields = ReviewListSerializer.Meta.fields + BaseReviewDetailsSerializer.Meta.fields + [

        ]
        read_only_fields = ReviewListSerializer.Meta.read_only_fields + BaseReviewDetailsSerializer.Meta.read_only_fields + []


# Review Create Serializer
class ReviewCreateSerializer(ReviewDetailsSerializer):
    model_obj_id = serializers.IntegerField(write_only=True, required=True)
    parent_obj_id = serializers.IntegerField(write_only=True, required=False)
    resourcetype = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ReviewDetailsSerializer.Meta.fields + [
            'model_obj_id',
            'parent_obj_id',
            'resourcetype',
        ]
        read_only_fields = ReviewDetailsSerializer.Meta.read_only_fields + []

    def validate_rate(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(_("The rate should be between 1 and 5"))
        return value

    def validate_model_obj_id(self, value):
        try:
            basemodel = get_object_or_404(BaseModel.objects.all(), id=value)
            return value
        except Exception as e:
            raise serializers.ValidationError(_("Base Model not found"))

    def validate_parent_obj_id(self, value):
        try:
            review = get_object_or_404(Review.objects.all(), id=value)
            return value
        except Exception as e:
            raise serializers.ValidationError(_("Review Parent not found"))

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_resourcetype(self, obj):
        return 'Review'


# Like List Serializer
class LikeListSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(LikeListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Like
        fields = [
            'id',
            'url',
            'is_like',
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())


# Like Details Serializer
class LikeDetailsSerializer(LikeListSerializer):
    user = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(LikeDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Like
        fields = LikeListSerializer.Meta.fields + [
            'user',
            'review',
        ]

    def get_user(self, obj):
        return UserSummeryListSerializer(obj.user_obj, many=False, read_only=True, context=self.context).data

    def get_review(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.review_obj, many=False, read_only=True, context=self.context).data


# Review List Polymorphic
class BaseReviewListPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        from aparnik.contrib.questionanswers.api.serializers import QAListSerializer
        from aparnik.contrib.questionanswers.models import QA

        self.model_serializer_mapping = {
            BaseReview: BaseReviewListSerializer,
            Review: ReviewListSerializer,
            QA: QAListSerializer
        }
        super(BaseReviewListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Review Details Polymorphic
class BaseReviewDetailsPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        from aparnik.contrib.questionanswers.api.serializers import QADetailSerializer
        from aparnik.contrib.questionanswers.models import QA

        self.model_serializer_mapping = {
            BaseReview: BaseReviewDetailsSerializer,
            Review: ReviewDetailsSerializer,
            QA: QADetailSerializer
        }
        super(BaseReviewDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.api.serializers import BaseSegmentListSerializer, BaseSegmentDetailSerializer
    from ..models import BaseReviewSegment

    # Base Segment ListSegmentReview
    class SegmentBaseReviewListSerializer(BaseSegmentListSerializer):

        class Meta:
            model = BaseReviewSegment
            fields = BaseSegmentListSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentListSerializer.Meta.read_only_fields + []


    # Book Segment Details
    class SegmentBaseReviewDetailSerializer(BaseSegmentDetailSerializer, SegmentBaseReviewListSerializer):

        class Meta:
            model = BaseReviewSegment
            fields = SegmentBaseReviewListSerializer.Meta.fields + BaseSegmentDetailSerializer.Meta.fields + [

            ]
            read_only_fields = BaseSegmentDetailSerializer.Meta.read_only_fields + SegmentBaseReviewListSerializer.Meta.read_only_fields + []