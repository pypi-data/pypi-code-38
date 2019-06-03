""" OaiProviderMetadataFormat rest api
"""
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core_main_app.commons import exceptions
from core_main_app.utils.decorators import api_staff_member_required
from core_oaipmh_common_app.commons import exceptions as exceptions_oai
from core_oaipmh_common_app.commons.messages import OaiPmhMessage
from core_oaipmh_provider_app.components.oai_provider_metadata_format import api as \
    oai_provider_metadata_format_api
from core_oaipmh_provider_app.components.oai_xsl_template import api as oai_xsl_template_api
from core_oaipmh_provider_app.rest import serializers


class MetadataFormatsList(APIView):
    """ List all MetadataFormat, or create a new one
    """

    @method_decorator(api_staff_member_required())
    def get(self, request):
        """ Return all MetadataFormat

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of MetadataFormat
            - code: 500
              content: Internal server error
        """
        try:
            metadata_formats = oai_provider_metadata_format_api.get_all()
            serializer = serializers.OaiProviderMetadataFormatSerializer(metadata_formats, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def post(self, request):
        """ Add a new MetadataFormat

        Parameters:

            {
                "metadata_prefix" : "value",
                "schema_url" : "URL"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 201
              content: Success Label
            - code: 400
              content: Bad request
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            serializer = serializers.OaiProviderMetadataFormatSerializer(data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Save data
            return serializer.save()
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MetadataFormatDetail(APIView):
    @method_decorator(api_staff_member_required())
    def get(self, request, metadata_format_id):
        """ Get a MetadataFormat

        Parameters:

            {
                "metadata_prefix" : "value",
                "schema_url" : "URL"
            }

        Args:

            request: HTTP request
            metadata_format_id: ObjectId

        Returns:

            - code: 200
              content: MetadataFormat
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            metadata_format = oai_provider_metadata_format_api.get_by_id(metadata_format_id)
            serializer = serializers.OaiProviderMetadataFormatSerializer(metadata_format)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except exceptions.DoesNotExist:
            content = OaiPmhMessage.\
                get_message_labelled('No Metadata Format found with the given id.')
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def delete(self, request, metadata_format_id):
        """ Delete a MetadataFormat

        Args:

            request: HTTP request
            metadata_format_id: ObjectId

        Returns:

            - code: 204
              content: Deletion succeed
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            metadata_format = oai_provider_metadata_format_api.get_by_id(metadata_format_id)
            oai_provider_metadata_format_api.delete(metadata_format)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except exceptions.DoesNotExist:
            content = OaiPmhMessage.get_message_labelled(
                'No Metadata Format found with the given id.')
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def patch(self, request, metadata_format_id):
        """ Update a MetadataFormat

        Parameters:

            {
                "metadata_prefix" : "value"
            }

        Args:

            request: HTTP request
            metadata_format_id: ObjectId

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
            metadata_format = oai_provider_metadata_format_api.get_by_id(metadata_format_id)
            # Build serializer
            serializer = serializers.UpdateMetadataFormatSerializer(instance=metadata_format,
                                                                    data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Save data
            serializer.save()
            content = OaiPmhMessage.get_message_labelled('Metadata Format updated with success.')

            return Response(content, status=status.HTTP_200_OK)
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DoesNotExist:
            content = OaiPmhMessage.get_message_labelled(
                'No Metadata Format found with the given id.')
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateAsMetadataFormat(APIView):
    @method_decorator(api_staff_member_required())
    def post(self, request):
        """ Add a new Template as MetadataFormat

        Parameters:

            {
                "metadata_prefix" : "value",
                "template_id":"value"
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
            serializer = serializers.TemplateMetadataFormatSerializer(data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Save data
            return serializer.save()
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateMetadataFormatXSLT(APIView):
    @method_decorator(api_staff_member_required())
    def post(self, request):
        """ Map a template, a metadata format and a XSLT. Used for the transformation of the
        template toward the metadata format thanks to the XSLT.

        Parameters:

            {
                "template": "value",
                "oai_metadata_format": "value",
                "xslt": "value"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: Success Label
            - code: 400
              content: Validation error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            serializer = serializers.TemplateToMFMappingXSLTSerializer(data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Try to set the instance
            serializer.init_instance()
            # Save data
            serializer.save()
            content = OaiPmhMessage.get_message_labelled('Mapping configured with success.')

            return Response(content, status=status.HTTP_200_OK)
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DoesNotExist as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def delete(self, request):
        """ Remove the mapping between a template, a metadata format and a XSLT

        Parameters:

            {
                "template_id": "value",
                "metadata_format_id": "value"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 204
              content: Deletion succeed
            - code: 400
              content: Validation error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            serializer = serializers.TemplateToMFUnMappingXSLTSerializer(data=request.data)
            # Validate data
            serializer.is_valid(True)
            # Get template id
            template_id = serializer.data.get('template_id')
            # Get metadata format id
            metadata_format_id = serializer.data.get('metadata_format_id')
            # Get mapping
            oai_xsl_template = oai_xsl_template_api.\
                get_by_template_id_and_metadata_format_id(template_id, metadata_format_id)
            # Delete the mapping
            oai_xsl_template_api.delete(oai_xsl_template)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as validation_exception:
            content = OaiPmhMessage.get_message_labelled(validation_exception.detail)
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DoesNotExist as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except exceptions_oai.OAIAPIException as e:
            return e.response()
        except Exception as e:
            content = OaiPmhMessage.get_message_labelled(e.message)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
