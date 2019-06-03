""" OaiProviderSet rest api
"""
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

import core_oaipmh_provider_app.components.oai_provider_set.api as oai_provider_set_api
from core_main_app.commons import exceptions
from core_main_app.utils.decorators import api_staff_member_required
from core_oaipmh_common_app.commons import exceptions as exceptions_oai
from core_oaipmh_common_app.commons.messages import OaiPmhMessage
from core_oaipmh_provider_app.rest import serializers


class SetsList(APIView):
    @method_decorator(api_staff_member_required())
    def get(self, request):
        """ Get all OaiProviderSet

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of OaiProviderSet
            - code: 500
              content: Internal server error
        """
        try:
            sets = oai_provider_set_api.get_all()
            serializer = serializers.OaiProviderSetSerializer(sets, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def post(self, request):
        """ Create a OaiProviderSet

        Parameters:

            {
                "set_spec": "value", 
                "set_name":"value", 
                "templates_manager": ["id1", "id2"], 
                "description":"value"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Success Label
            - code: 400
              content: Validation error
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            serializer = serializers.OaiProviderSetSerializer(data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Save data
            serializer.save()
            content = OaiPmhMessage.get_message_labelled('Set added with success.')

            return Response(content, status=status.HTTP_201_CREATED)
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SetDetail(APIView):
    @method_decorator(api_staff_member_required())
    def get(self, request, set_id):
        """ Get a OaiProviderSet

        Args:

            request: HTTP request
            set_id: ObjectId

        Returns:

            - code: 200
              content: Registry
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            set_ = oai_provider_set_api.get_by_id(set_id)
            serializer = serializers.OaiProviderSetSerializer(set_)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except exceptions.DoesNotExist:
            content = OaiPmhMessage.get_message_labelled('No Set found with the given id.')
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def delete(self, request, set_id):
        """ Delete a OaiProviderSet

        Args:

            request: HTTP request
            set_id: ObjectId

        Returns:

            - code: 204
              content: Deletion succeed
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            set_ = oai_provider_set_api.get_by_id(set_id)
            oai_provider_set_api.delete(set_)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except exceptions.DoesNotExist:
            content = OaiPmhMessage.get_message_labelled('No Set found with the given id.')
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def patch(self, request, set_id):
        """ Update a OaiProviderSet

        Parameters:

            {
                "set_spec":"value",
                "set_name":"value",
                "templates_manager": ["id1", "id2"],
                "description":"value"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: Success message
            - code: 400
              content: Validation error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            set_ = oai_provider_set_api.get_by_id(set_id)
            # Build serializer
            serializer = serializers.OaiProviderSetSerializer(instance=set_, data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Save data
            serializer.save()
            content = OaiPmhMessage.get_message_labelled('Set updated with success.')

            return Response(content, status=status.HTTP_200_OK)
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DoesNotExist:
            content = OaiPmhMessage.get_message_labelled('No Set found with the given id.')
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
