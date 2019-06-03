""" REST views for the data API
"""
from urlparse import urljoin

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.decorators import schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

import core_federated_search_app.components.instance.api as instance_api
from core_explore_common_app.utils.protocols.oauth2 import send_get_request as oauth2_request
from core_explore_common_app.utils.result.result import get_result_from_rest_data_response
from core_explore_federated_search_app.rest.result.serializers import ResultDetailSerializer


@schema(None)
class ResultDetail(APIView):
    """ Result Detail API view
    """
    def get(self, request):
        """ Access data, Return Result, Expect a data ID and a Remote name in parameters

        Parameters:

            {
                "id" : "data_id",
                "instance_name" : "endpoint_name"
            }

        Args:

            request:

        Returns:

            - code: 200
              content: Data
            - code: 400
              content: Validation error
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            serializer = ResultDetailSerializer(data=request.query_params)
            # Validation
            serializer.is_valid(True)
            # reverse url for accessing data
            url_get_data = reverse("core_main_app_rest_data_detail",
                                   kwargs={'pk': serializer.validated_data['id']})
            # requests the remote instance
            instance = instance_api.get_by_name(serializer.validated_data['instance_name'])
            response = oauth2_request(urljoin(instance.endpoint, url_get_data),
                                      instance.access_token)
            # if got a response from data
            if response.status_code == 200:
                # Serialize results
                return_value = get_result_from_rest_data_response(response)
                # Returns the response
                return Response(return_value, status=status.HTTP_200_OK)
            # if there no data we return the response given by the remote
            else:
                return Response(status=response.status_code)
        except ValidationError as validation_exception:
            content = {'message': validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # if something went wrong, return an internal server error
            content = {'message': e.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
