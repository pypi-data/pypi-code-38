from rest_framework import serializers
from aparnik.api.serializers import ModelSerializer

from ..models import TermsAndConditions
from aparnik.contrib.shortblogs.api.serializers import ShortBlogDetailSerializer


class TermsAndCondtionsDestailSerializer(ModelSerializer):

    short_blogs = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TermsAndCondtionsDestailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = TermsAndConditions
        fields = [
            'id',
            'short_blogs',
        ]

    def get_short_blogs(self, obj):
        return ShortBlogDetailSerializer(obj.short_blogs, many=True, read_only=True, context=self.context).data
