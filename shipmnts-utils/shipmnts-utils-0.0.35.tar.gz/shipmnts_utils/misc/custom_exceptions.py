from rest_framework import status
from rest_framework.exceptions import APIException


class TriggerInternalServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal Server Error"
    default_code = "internal_server_error"


class UnauthorizedUserException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized"
    default_code = "unauthorized"
