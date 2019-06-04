# -*- coding:utf-8 -*- 

from rest_framework import serializers, viewsets, mixins, decorators
from . import models


class TempFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TempFile
        fields = ('url', 'name', 'file', 'id')

class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Image
        fields = ('content_type', 'object_id', 'file', 'id')
