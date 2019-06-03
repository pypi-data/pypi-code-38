""" Abstract view for Account Request
"""
from abc import ABCMeta, abstractmethod

from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

import core_website_app.components.account_request.api as account_request_api
from core_main_app.commons import exceptions
from core_main_app.commons.exceptions import ApiError
from core_main_app.utils.access_control.exceptions import AccessControlError
from core_main_app.utils.decorators import api_staff_member_required


class AbstractActionAccountRequest(APIView):
    """ Action Account request
    """

    __metaclass__ = ABCMeta

    def get_object(self, pk):
        """ Get AccountRequest from db

        Args:

            pk: ObjectId

        Returns:

            Account Request
        """
        try:
            return account_request_api.get(pk)
        except exceptions.DoesNotExist:
            raise Http404

    @abstractmethod
    def perform(self, account_request_object):
        """ Perform an action on the account request
        """
        raise NotImplementedError("action method is not implemented.")

    @method_decorator(api_staff_member_required())
    def patch(self, request, pk):
        """ Deny or Accept

        Args:

            request: HTTP request
            pk: ObjectId

        Returns:

            - code: 200
              content: None
            - code: 400
              content: Validation error / bad request
            - code: 403
              content: Authentication error
            - code: 404
              content: Object was not found
            - code: 500
              content: Internal server error
        """
        try:
            # Get object
            account_request_object = self.get_object(pk)

            # Set current template
            self.perform(account_request_object)

            return Response(status=status.HTTP_200_OK)
        except Http404:
            content = {'message': 'Account Request not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as access_error:
            content = {'message': access_error.message}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as validation_exception:
            content = {'message': validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except ApiError as api_error:
            content = {'message': api_error.message}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
