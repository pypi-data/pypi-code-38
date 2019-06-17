from django.db.models import Model
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.utils.utils import is_app_installed
from aparnik.api.serializers import ModelSerializer

from ..models import BaseModel, Tag


# Base Model List
class TagsDetailsSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()
    resourcetype = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TagsDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Tag
        fields = [
            'id',
            'url',
            'name',
            'resourcetype',
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_resourcetype(self, obj):
        return 'Tag'


class BaseModelListSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    qa_count = serializers.SerializerMethodField()
    url_review = serializers.SerializerMethodField()
    url_qa = serializers.SerializerMethodField()
    # is_bookmark = serializers.SerializerMethodField()
    url_bookmark_set = serializers.SerializerMethodField()
    url_review_add = serializers.SerializerMethodField()
    url_qa_add = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    sort = serializers.SerializerMethodField()

    # qa_count_string = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BaseModelListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseModel
        fields = [
            'id',
            'url',
            'review_count',
            'review_count_string',
            'review_average',
            'qa_count',
            'qa_count_string',
            'url_review',
            'url_review_add',
            'url_qa',
            'url_qa_add',
            # 'is_bookmark',
            'url_bookmark_set',
            'tags',
            'sort',
            'visit_count',
            'visit_count_string',
            'bookmark_count',
            'bookmark_count_string',
        ]

        read_only_fields = ['id', 'url', 'is_bookmark', 'review_average', 'review_count', 'review_count_string' 
                            'qa_count', 'qa_count_string', 'url_review',
                            'url_qa', 'tags', 'sort', 'visit_count', 'visit_count_string',
                            'bookmark_count', 'bookmark_count_string'
                            ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_review_count(self, obj):
        return obj.review_count

    def get_qa_count(self, obj):
        return obj.qa_count

    def get_url_bookmark_set(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_bookmark_set_uri())

    def get_url_review(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_review_uri())

    def get_url_review_add(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_review_add_uri())

    def get_url_qa(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_qa_uri())

    def get_url_qa_add(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_qa_add_uri())

    # def get_is_bookmark(self, obj):
    #     user = self.context['request'].user
    #     return obj.is_bookmark(user=user)
    #

    def get_tags(self, obj):
        # if not obj.tags:
        #     return None
        # return TagsDetailsSerializer(obj.tags, many=True, read_only=True, context=self.context).data
        # worse performance
        return None

    def get_sort(self, obj):
        if 'segment_obj' in self.context:
            objs = self.context['segment_obj'].segment_sort_segment.filter(model_obj=obj)
            if objs.exists():
                return objs.first().sort
        return obj.sort

    def get_bookmark_count(self, obj):
        return obj.bookmark_count


# Base Model Details
class BaseModelDetailSerializer(BaseModelListSerializer):

    # share_string = serializers.SerializerMethodField()
    # url_share = serializers.SerializerMethodField()
    # review_summaries = serializers.SerializerMethodField()
    # is_notify_me = serializers.SerializerMethodField()
    # url_notify_me_set = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BaseModelListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseModel
        fields = BaseModelListSerializer.Meta.fields + [
            # 'share_string',
            # 'url_share',
            # 'review_summaries',
            # 'is_notify_me',
            # 'url_notify_me_set',
        ]
        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + [
            'url_share'
        ]

    # def get_share_string(self, obj):
    #     # TODO: fix it
    #     return 'This content is ready for sharing'
    #
    # def get_url_share(self, obj):
    #     return self.context['request'].build_absolute_uri(obj.get_api_share_uri())
    #
    # def get_review_summaries(self, obj):
    #     from aparnik.contrib.reviews.api.serializers import ReviewSummaryListSerializer
    #     return ReviewSummaryListSerializer(obj.review_summaries, many=True, read_only=True, context=self.context).data
    #
    # def get_is_notify_me(self, obj):
    #     user = self.context['request'].user
    #     return obj.is_notify(user=user)
    #
    # def get_url_notify_me_set(self, obj):
    #     return self.context['request'].build_absolute_uri(obj.get_api_notify_me_set_uri())


# Base Model List Polymorphic
class ModelListPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):

        model_serializer_mapping = {
            BaseModel: BaseModelListSerializer
        }

        # File Fileld
        if is_app_installed('aparnik.contrib.filefields'):
            from aparnik.contrib.filefields.models import FileField
            from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
            model_serializer_mapping[FileField] = FileFieldListSerailizer

        # Page
        if is_app_installed('aparnik.contrib.pages'):
            from aparnik.contrib.pages.models import Page
            from aparnik.contrib.pages.api.serializers import PageListPolymorphicSerializer
            model_serializer_mapping[Page] = PageListPolymorphicSerializer

        # Slider
        if is_app_installed('aparnik.contrib.sliders'):
            from aparnik.contrib.sliders.models import Slider
            from aparnik.contrib.sliders.api.serializers import SliderDetailsPolymorphicSerializer
            model_serializer_mapping[Slider] = SliderDetailsPolymorphicSerializer

        # Review
        if is_app_installed('aparnik.contrib.reviews'):
            from aparnik.contrib.reviews.models import BaseReview
            from aparnik.contrib.reviews.api.serializers import BaseReviewListPolymorphicSerializer
            model_serializer_mapping[BaseReview] = BaseReviewListPolymorphicSerializer

        # user address
        if is_app_installed('aparnik.contrib.addresses'):
            from aparnik.contrib.addresses.models import UserAddress
            from aparnik.contrib.addresses.api.serializers import AddressListSerializer
            model_serializer_mapping[UserAddress] = AddressListSerializer

        # bank accounts
        if is_app_installed('aparnik.contrib.bankaccounts'):
            from aparnik.contrib.bankaccounts.models import BankName, BankAccount
            from aparnik.contrib.bankaccounts.api.serializers import BankNameListSerializer, BankAccountListSerializer
            model_serializer_mapping[BankName] = BankNameListSerializer
            model_serializer_mapping[BankAccount] = BankAccountListSerializer

        # Button
        if is_app_installed('aparnik.contrib.buttons'):
            from aparnik.contrib.buttons.models import Button
            from aparnik.contrib.buttons.api.serializers import ButtonListSerializer
            model_serializer_mapping[Button] = ButtonListSerializer

        # Segments
        if is_app_installed('aparnik.contrib.segments'):
            from aparnik.contrib.segments.models import BaseSegment
            from aparnik.contrib.segments.api.serializers import BaseSegmentListPolymorphicSerializer
            model_serializer_mapping[BaseSegment] = BaseSegmentListPolymorphicSerializer

        # Category
        if is_app_installed('aparnik.contrib.categories'):
            from aparnik.contrib.categories.models import Category
            from aparnik.contrib.categories.api.serializers import CategoryListPolymorphicSerializer
            model_serializer_mapping[Category] = CategoryListPolymorphicSerializer

        # Notification
        if is_app_installed('aparnik.contrib.notifications'):
            from aparnik.contrib.notifications.models import Notification
            from aparnik.contrib.notifications.api.serializers import NotificationListSerializer
            model_serializer_mapping[Notification] = NotificationListSerializer

        # Social Network
        if is_app_installed('aparnik.contrib.socials'):
            from aparnik.contrib.socials.models import SocialNetwork
            from aparnik.contrib.socials.api.serializers import SocialNetworkDestailSerializer
            model_serializer_mapping[SocialNetwork] = SocialNetworkDestailSerializer

        # Prdocut
        if is_app_installed('aparnik.packages.shops.products'):
            from aparnik.packages.shops.products.models import Product
            from aparnik.packages.shops.products.api.serializers import ProductListPolymorphicSerializer
            model_serializer_mapping[Product] = ProductListPolymorphicSerializer

        # Order
        if is_app_installed('aparnik.packages.shops.orders'):
            from aparnik.packages.shops.orders.models import Order, OrderItem
            from aparnik.packages.shops.orders.api.serializers import OrderSummarySerializer, OrderItemDetailSerializer
            model_serializer_mapping[Order] = OrderSummarySerializer
            model_serializer_mapping[OrderItem] = OrderItemDetailSerializer

        # Payment
        if is_app_installed('aparnik.packages.shops.payments'):
            from aparnik.packages.shops.payments.models import Payment
            from aparnik.packages.shops.payments.api.serializers import PaymentSummarySerializer
            model_serializer_mapping[Payment] = PaymentSummarySerializer

        # Co Sale
        if is_app_installed('aparnik.packages.shops.cosales'):
            from aparnik.packages.shops.cosales.models import CoSale
            from aparnik.packages.shops.cosales.api.serializers import CoSaleListSerializer
            model_serializer_mapping[CoSale] = CoSaleListSerializer

        # Teacher
        if is_app_installed('aparnik.packages.educations.teachers'):
            from aparnik.packages.educations.teachers.models import Teacher
            from aparnik.packages.educations.teachers.api.serializers import TeacherListPolymorphicSerializer
            model_serializer_mapping[Teacher] = TeacherListPolymorphicSerializer

        # Base Educations
        if is_app_installed('aparnik.packages.educations.educations'):
            from aparnik.packages.educations.educations.models import BaseEducation
            from aparnik.packages.educations.educations.api.serializers import BaseEducationListPolymorphicSerializer
            model_serializer_mapping[BaseEducation] = BaseEducationListPolymorphicSerializer

        # news
        if is_app_installed('aparnik.packages.news'):
            from aparnik.packages.news.models import News
            from aparnik.packages.news.api.serializers import NewsListSerializer
            model_serializer_mapping[News] = NewsListSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(ModelListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Base Model Details Polymorphic
class ModelDetailsPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):

        model_serializer_mapping = {
            BaseModel: BaseModelDetailSerializer
        }

        # File Fileld
        if is_app_installed('aparnik.contrib.filefields'):
            from aparnik.contrib.filefields.models import FileField
            from aparnik.contrib.filefields.api.serializers import FileFieldDetailsSerailizer
            model_serializer_mapping[FileField] = FileFieldDetailsSerailizer

        # Page
        if is_app_installed('aparnik.contrib.pages'):
            from aparnik.contrib.pages.models import Page
            from aparnik.contrib.pages.api.serializers import PageDetailsPolymorphicSerializer
            model_serializer_mapping[Page] = PageDetailsPolymorphicSerializer

        # Slider
        if is_app_installed('aparnik.contrib.sliders'):
            from aparnik.contrib.sliders.models import Slider
            from aparnik.contrib.sliders.api.serializers import SliderDetailsPolymorphicSerializer
            model_serializer_mapping[Slider] = SliderDetailsPolymorphicSerializer

        # Review
        if is_app_installed('aparnik.contrib.reviews'):
            from aparnik.contrib.reviews.models import BaseReview
            from aparnik.contrib.reviews.api.serializers import BaseReviewDetailsPolymorphicSerializer
            model_serializer_mapping[BaseReview] = BaseReviewDetailsPolymorphicSerializer

        # user address
        if is_app_installed('aparnik.contrib.addresses'):
            from aparnik.contrib.addresses.models import UserAddress
            from aparnik.contrib.addresses.api.serializers import AddressDetailSerializer
            model_serializer_mapping[UserAddress] = AddressDetailSerializer

        # bank accounts
        if is_app_installed('aparnik.contrib.bankaccounts'):
            from aparnik.contrib.bankaccounts.models import BankName, BankAccount
            from aparnik.contrib.bankaccounts.api.serializers import BankNameDetailSerializer, BankAccountDetailSerializer
            model_serializer_mapping[BankName] = BankNameDetailSerializer
            model_serializer_mapping[BankAccount] = BankAccountDetailSerializer

        # Button
        if is_app_installed('aparnik.contrib.buttons'):
            from aparnik.contrib.buttons.models import Button
            from aparnik.contrib.buttons.api.serializers import ButtonDetailsSerializer
            model_serializer_mapping[Button] = ButtonDetailsSerializer

        # Segments
        if is_app_installed('aparnik.contrib.segments'):
            from aparnik.contrib.segments.models import BaseSegment
            from aparnik.contrib.segments.api.serializers import BaseSegmentDetailsPolymorphicSerializer
            model_serializer_mapping[BaseSegment] = BaseSegmentDetailsPolymorphicSerializer

        # Category
        if is_app_installed('aparnik.contrib.categories'):
            from aparnik.contrib.categories.models import Category
            from aparnik.contrib.categories.api.serializers import CategoryDetailsPolymorphicSerializer
            model_serializer_mapping[Category] = CategoryDetailsPolymorphicSerializer

        # Notification
        if is_app_installed('aparnik.contrib.notifications'):
            from aparnik.contrib.notifications.models import Notification
            from aparnik.contrib.notifications.api.serializers import NotificationDetailSerializer
            model_serializer_mapping[Notification] = NotificationDetailSerializer

        # Social Network
        if is_app_installed('aparnik.contrib.socials'):
            from aparnik.contrib.socials.models import SocialNetwork
            from aparnik.contrib.socials.api.serializers import SocialNetworkDestailSerializer
            model_serializer_mapping[SocialNetwork] = SocialNetworkDestailSerializer

        # Prdocut
        if is_app_installed('aparnik.packages.shops.products'):
            from aparnik.packages.shops.products.models import Product
            from aparnik.packages.shops.products.api.serializers import ProductDetailsPolymorphicSerializer
            model_serializer_mapping[Product] = ProductDetailsPolymorphicSerializer

        # Order
        if is_app_installed('aparnik.packages.shops.orders'):
            from aparnik.packages.shops.orders.models import Order, OrderItem
            from aparnik.packages.shops.orders.api.serializers import OrderDetailSerializer, OrderItemDetailSerializer
            model_serializer_mapping[Order] = OrderDetailSerializer
            model_serializer_mapping[OrderItem] = OrderItemDetailSerializer

        # Payment
        if is_app_installed('aparnik.packages.shops.payments'):
            from aparnik.packages.shops.payments.models import Payment
            from aparnik.packages.shops.payments.api.serializers import PaymentDetailSerializer
            model_serializer_mapping[Payment] = PaymentDetailSerializer

        # Co Sale
        if is_app_installed('aparnik.packages.shops.cosales'):
            from aparnik.packages.shops.cosales.models import CoSale
            from aparnik.packages.shops.cosales.api.serializers import CoSaleDetailsSerializer
            model_serializer_mapping[CoSale] = CoSaleDetailsSerializer

        # Teacher
        if is_app_installed('aparnik.packages.educations.teachers'):
            from aparnik.packages.educations.teachers.models import Teacher
            from aparnik.packages.educations.teachers.api.serializers import TeacherDetailsPolymorphicSerializer
            model_serializer_mapping[Teacher] = TeacherDetailsPolymorphicSerializer

        # Base Educations
        if is_app_installed('aparnik.packages.educations.educations'):
            from aparnik.packages.educations.educations.models import BaseEducation
            from aparnik.packages.educations.educations.api.serializers import BaseEducationDetailsPolymorphicSerializer
            model_serializer_mapping[BaseEducation] = BaseEducationDetailsPolymorphicSerializer

        # news
        if is_app_installed('aparnik.packages.news'):
            from aparnik.packages.news.models import News
            from aparnik.packages.news.api.serializers import NewsDetailSerializer
            model_serializer_mapping[News] = NewsDetailSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(ModelDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
