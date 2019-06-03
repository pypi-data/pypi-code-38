""" Rest views for the contact message API
"""
import logging

from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

import core_website_app.components.contact_message.api as contact_message_api
from core_main_app.commons import exceptions
from core_main_app.utils.decorators import api_staff_member_required
from core_website_app.rest.contact_message.serializers import ContactMessageSerializer

logger = logging.getLogger("core_website_app.rest.contact_message.views")


class ContactMessageList(APIView):
    """ Create or get all Contact Message
    """

    @method_decorator(api_staff_member_required())
    def get(self, request):
        """ Get all Contact Message

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: List of contact messages
            - code: 500
              content: Internal server error
        """
        try:
            contact_message_list = contact_message_api.get_all()

            # Serialize object
            serializer = ContactMessageSerializer(contact_message_list, many=True)

            # Return response
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """ Create a message

        Parameters:

            {
                "name": "name",
                "content": "message",
                "email": "email"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: Contact message
            - code: 400
              content: Validation error / missing parameters
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            serializer = ContactMessageSerializer(data=request.data)

            # Validate message
            serializer.is_valid(True)

            # Save message
            serializer.save()

            # Return the serialized message
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as validation_exception:
            content = {'message': validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactMessageDetail(APIView):
    """ Get or delete a Contact Message
    """

    def get_object(self, pk):
        """ Get Contact Message from db

        Args:

            pk: ObjectId

        Returns:

            Contact Message
        """
        try:
            return contact_message_api.get(pk)
        except exceptions.DoesNotExist:
            raise Http404

    @method_decorator(api_staff_member_required())
    def get(self, request, pk):
        """ Retrieve a Contact Message

        Parameters:

            {
                "pk": "message_id"
            }

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: Contact message
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            contact_message_object = self.get_object(pk)

            # Serialize object
            serializer = ContactMessageSerializer(contact_message_object)

            # Return response
            return Response(serializer.data)
        except Http404:
            content = {'message': 'Contact message not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def delete(self, request, pk):
        """ Delete a Contact Message

        Parameters:

            {
                "pk": "message_id"
            }

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
            contact_message_object = self.get_object(pk)

            # delete object
            contact_message_api.delete(contact_message_object)

            # Return response
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            content = {'message': 'Data not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
