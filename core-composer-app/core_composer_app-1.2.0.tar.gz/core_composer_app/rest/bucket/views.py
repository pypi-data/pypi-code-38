""" Views for the Bucket REST API
"""
from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core_composer_app.components.bucket import api as bucket_api
from core_composer_app.rest.bucket.serializers import BucketSerializer, BucketsSerializer
from core_main_app.commons.exceptions import DoesNotExist
from core_main_app.rest.template_version_manager.abstract_views import AbstractTemplateVersionManagerDetail
from core_main_app.utils.access_control.exceptions import AccessControlError
from core_main_app.utils.decorators import api_staff_member_required


class BucketList(APIView):
    """ List all buckets, or create a new one.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Get all buckets

        Url Parameters:

            label: label

        Examples:

            ../bucket/
            ../bucket?label=[label]

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of buckets
            - code: 500
              content: Internal server error
        """
        try:
            # Get objects
            object_list = bucket_api.get_all()

            # Apply filters
            label = self.request.query_params.get('label', None)
            if label is not None:
                object_list = object_list.filter(label=label)

            # Serialize object
            serializer = BucketSerializer(object_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def post(self, request):
        """ Create a bucket

        Parameters:

            {
                "label": "label",
                "types": ["<type_version_manager_id>"]
            }

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Created bucket
            - code: 400
              content: Validation error
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            bucket_serializer = BucketSerializer(data=request.data)

            # Validate data
            bucket_serializer.is_valid(True)
            # Save data
            bucket_serializer.save()

            # Return the serialized data
            return Response(bucket_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as validation_exception:
            content = {'message': validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BucketDetail(APIView):
    """ Retrieve, update or delete a bucket
    """

    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        """ Get bucket from db

        Args:

            pk: ObjectId

        Returns:

            Bucket
        """
        try:
            return bucket_api.get_by_id(pk)
        except DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """ Retrieve a bucket

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: Bucket
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            bucket = self.get_object(pk)

            # Serialize object
            serializer = BucketSerializer(bucket)

            # Return response
            return Response(serializer.data)
        except Http404:
            content = {'message': 'Bucket not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def delete(self, request, pk):
        """ Delete a bucket

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 204
              content: Deletion succeed
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            bucket = self.get_object(pk)

            # delete object
            bucket_api.delete(bucket)

            # Return response
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            content = {'message': 'Bucket not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def patch(self, request, pk):
        """ Update bucket

        Parameters:

            {
                "label": "<label>"
            }

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: Updated bucket
            - code: 400
              content: Validation error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            bucket = self.get_object(pk)

            # Build serializer
            bucket_serializer = BucketSerializer(instance=bucket,
                                                 data=request.data,
                                                 partial=True)

            # Validate data
            bucket_serializer.is_valid(True)
            # Save data
            bucket_serializer.save(user=request.user)

            return Response(bucket_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as validation_exception:
            content = {'message': validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            content = {'message': 'Bucket not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TypeVersionManagerBuckets(AbstractTemplateVersionManagerDetail):
    """ Set new list of buckets for a type version manager
    """

    @method_decorator(api_staff_member_required())
    def patch(self, request, pk):
        """ Set new list of buckets for a type version manager

        Parameters:

            [
                {
                    "id":"<bucket_id>"
                },
                {
                    "id":"<bucket_id>"
                }
            ]

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: None
            - code: 400
              content: Validation error
            - code: 403
              content: Authentication error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            type_version_manager = self.get_object(pk)

            # Serialize data
            serializer = BucketsSerializer(data=request.data, many=True)

            # Validate data
            serializer.is_valid(True)

            # Get list of unique ids
            bucket_ids = set([bucket['id'] for bucket in serializer.validated_data])

            # act
            bucket_api.update_type_buckets(type_version_manager, bucket_ids)

            return Response(status=status.HTTP_200_OK)
        except Http404:
            content = {'message': 'Object not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as access_error:
            content = {'message': access_error.message}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as validation_exception:
            content = {'message': validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

