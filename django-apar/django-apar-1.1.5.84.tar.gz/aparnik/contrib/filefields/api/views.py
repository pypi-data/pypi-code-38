# -*- coding: utf-8 -*-


from django.conf import settings

from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAdminUser)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from s3direct.utils import get_s3direct_destinations
import os, json, boto3

from .serializers import FileFieldDetailsSerailizer, FileFieldListSerailizer
from ..models import FileField


class FileFieldListAPIView(ListAPIView):
    serializer_class = FileFieldListSerailizer
    permission_classes = [IsAdminUser]
    queryset = FileField.objects.active()


class SignS3(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None, *args, **kwargs):
        # Load necessary information into the application
        S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME

        # Load required data from the request
        file_name = request.POST.get('file-name')
        file_type = request.POST.get('file-type')

        # Initialise the S3 client
        s3 = boto3.client('s3')
        key = get_s3direct_destinations().get('file').get('key')(file_name)
        endpoint = 'https://' + settings.AWS_S3_CUSTOM_DOMAIN + '/' + key

        # Generate and return the presigned URL
        presigned_post = s3.generate_presigned_post(
            Bucket=S3_BUCKET,
            # Key='upload_file/' + file_name,
            Key=key,
            Fields={"acl": "public-read", "Content-Type": file_type},
            Conditions=[
              {"acl": "public-read"},
              {"Content-Type": file_type}
            ],
            ExpiresIn=3600
        )

        # Return the data to the client
        status = HTTP_200_OK
        content = {
            'data': presigned_post,
            'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, key),
            'endpoint': endpoint,
        }

        return Response(content, status=status)


class FileFieldCreateAPIView(CreateAPIView):
    serializer_class = FileFieldDetailsSerailizer
    permission_classes = [IsAuthenticated]

