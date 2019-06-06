from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.utils.decorators import classonlymethod

from djangoldp.models import Model
from djangoldp_account.errors import LDPLoginError


class Solid(object):

    @classonlymethod
    def confirm_webid(cls, webid, iss):
        """
        See https://github.com/solid/webid-oidc-spec/blob/master/README.md#webid-provider-confirmation
        :param webid:
        :return:
        """
        url = urlparse(iss)
        webid_url = urlparse(webid)
        if webid_url.netloc == url.netloc:
            pass
        else:
            raise LDPLoginError('cannot_confirm_webid')
        # TODO : add the other cases

    @classonlymethod
    def get_or_create_user(cls, userinfo, webid):
        if webid.startswith(settings.SITE_URL):
            existing_user = Model.resolve_id(userinfo['sub'][len(settings.SITE_URL):])
        else:
            try:
                existing_user = get_user_model().objects.get(username=webid)
            except get_user_model().DoesNotExist:
                existing_user = None
        if existing_user is not None:
            user = existing_user
        else:
            user = get_user_model().objects.create_user(username=webid,
                                                        first_name=userinfo['given_name'],
                                                        last_name=userinfo['family_name'],
                                                        email=userinfo['email'])
        return user
