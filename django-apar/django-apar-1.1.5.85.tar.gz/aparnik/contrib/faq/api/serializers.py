from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer

from aparnik.contrib.faq.models import FAQ
from aparnik.contrib.shortblogs.api.serializers import ShortBlogDetailSerializer


class FAQDetailsSerializer(ModelSerializer):

    short_blogs = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(FAQDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = FAQ
        fields = [
            'id',
            'short_blogs',
        ]

    def get_short_blogs(self, obj):
        return ShortBlogDetailSerializer(obj.short_blogs, many=True, read_only=True, context=self.context).data
