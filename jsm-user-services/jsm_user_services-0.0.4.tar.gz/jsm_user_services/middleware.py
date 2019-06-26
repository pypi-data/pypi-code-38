import logging
import re
from typing import Optional

from django.http import HttpRequest
from jsm_user_services import local_threading
from jsm_user_services.services.user import get_jsm_user_data_from_jwt

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


logger = logging.getLogger(__name__)


class JsmJwtService(MiddlewareMixin):
    def process_request(self, request):

        authorization_token = self._get_jwt_token_from_request(request)
        if authorization_token:
            local_threading.authorization_token = authorization_token

            try:
                user_data = get_jsm_user_data_from_jwt()
                logger.info("User: %s", user_data)
            except BaseException:
                pass

        logger.info("No token found.")

    def process_response(self, request, response):

        try:
            delattr(local_threading, "authorization_token")
        except:
            pass

        return response

    @staticmethod
    def _get_jwt_token_from_request(request: HttpRequest) -> Optional[str]:
        """
        Extracts JWT token from a Django request object.
        """
        authorization_token = request.META.get("HTTP_AUTHORIZATION", "")

        match = re.match("Bearer", authorization_token)

        if not match:
            return None

        auth_type_beginning = match.span()[1]
        jwt_token = authorization_token[auth_type_beginning:].strip()

        return jwt_token
