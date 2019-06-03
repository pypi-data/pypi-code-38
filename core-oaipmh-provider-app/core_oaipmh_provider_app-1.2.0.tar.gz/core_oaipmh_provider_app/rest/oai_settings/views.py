""" OaiSettings rest api
"""
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

import core_oaipmh_provider_app.components.oai_settings.api as oai_settings_api
from core_main_app.utils.decorators import api_staff_member_required
from core_main_app.utils.requests_utils.requests_utils import send_get_request
from core_oaipmh_common_app.commons import exceptions as exceptions_oai
from core_oaipmh_common_app.commons.messages import OaiPmhMessage
from core_oaipmh_provider_app.rest import serializers


class Settings(APIView):
    @method_decorator(api_staff_member_required())
    def get(self, request):
        """ Return the OAI-PMH server settings

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of Registries
            - code: 500
              content: Internal server error
        """
        try:
            settings_ = oai_settings_api.get()
            serializer = serializers.SettingsSerializer(settings_)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def patch(self, request):
        """ Edit the OAI-PMH server settings

        Parameters:

            {
                "repository_name":"value",
                "repository_identifier":"value",
                "enable_harvesting":"True or False"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: Success message
            - code: 400
              content: Validation error
            - code: 500
              content: Internal server error
        """
        try:
            settings_ = oai_settings_api.get()
            # Build serializer
            serializer = serializers.SettingsSerializer(instance=settings_, data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Save data
            serializer.save()
            content = OaiPmhMessage.get_message_labelled('OAI-PMH Settings updated with success.')

            return Response(content, status=status.HTTP_200_OK)
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Check(APIView):
    @method_decorator(api_staff_member_required())
    def get(self, request):
        """ Check if the registry is available to answer OAI-PMH requests

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: Success label
            - code: 500
              content: Internal server error
        """
        try:
            base_url = request.build_absolute_uri(reverse("core_oaipmh_provider_app_server_index"))
            http_response = send_get_request(base_url)
            is_available = http_response.status_code == status.HTTP_200_OK
            content = OaiPmhMessage.get_message_labelled('Registry available? : {0}.'.format(
                is_available))

            return Response(content, status=http_response.status_code)
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
