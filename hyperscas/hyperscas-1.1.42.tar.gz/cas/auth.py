import requests

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import \
    TokenAuthentication as _TokenAuthentication
from rest_framework.authentication import get_authorization_header

User = get_user_model()


class OAuth2Authentication(_TokenAuthentication):
    keyword = "bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        if len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _(
                "Invalid token header. Token string should not contain invalid characters."
            )
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    def authenticate_credentials(self, key, request=None):
        url = request.domain.auth.oauth2
        params = {"token": key}

        try:
            response = requests.get(url, params=params).json()
        except Exception:
            response = {}
        email = response.get("userEmail", "")

        # 若AccessToken校验未通过, 返回401, 转发AS端返回的错误信息
        if not email:
            raise exceptions.NotAuthenticated(response)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.PermissionDenied(_("用户不存在"))

        return user, None

    def authenticate_header(self, request):
        return self.keyword
