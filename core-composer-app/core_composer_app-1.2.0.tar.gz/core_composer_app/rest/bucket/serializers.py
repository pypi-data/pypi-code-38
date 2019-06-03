"""Serializers used throughout the bucket Rest API
"""
from django.http import Http404
from rest_framework_mongoengine.serializers import DocumentSerializer

from core_composer_app.components.bucket import api as bucket_api
from core_composer_app.components.bucket.models import Bucket
from rest_framework.fields import CharField

from core_main_app.commons.exceptions import DoesNotExist


class BucketSerializer(DocumentSerializer):
    """ Bucket serializer
    """
    class Meta:
        """ Meta
        """
        model = Bucket
        fields = '__all__'
        read_only_fields = ('id', 'color', )

    def create(self, validated_data):
        """
        Create and return a new `Bucket` instance, given the validated data.
        """
        # Create data
        bucket = Bucket(label=validated_data['label'],
                        types=validated_data.get('types', None))
        # Save the data
        return bucket_api.upsert(bucket)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Bucket` instance, given the validated data.
        """
        instance.label = validated_data.get('label', instance.label)
        return bucket_api.upsert(instance)


class BucketsSerializer(DocumentSerializer):
    """ Buckets serializer.
    """
    id = CharField()

    class Meta:
        model = Bucket
        fields = ('id', )

    def validate_id(self, id):
        """ Validate id field

        Args:
            id:

        Returns:

        """
        try:
            bucket_api.get_by_id(id)
            return id
        except DoesNotExist:
            raise Http404
