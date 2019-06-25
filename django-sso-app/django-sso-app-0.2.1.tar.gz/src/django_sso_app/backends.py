import logging

from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

from . import settings
from .utils import (get_sso_id,
                    get_profile_from_sso,
                    create_local_profile_from_sso,
                    update_local_profile_from_sso,
                    get_profile_model,
                    create_local_profile_from_headers,
                    get_user_groups_from_header,
                    update_user_groups)


logger = logging.getLogger("django_sso_app")
UserProfileModel = get_profile_model()


class SsoBackend(ModelBackend):
    """
    See django.contrib.auth.backends.RemoteUserBackend.

    The jwt has an expected payload such as the following

        {
          "iss": "nxhnkMPKcpRWaTKwNOvGcLcs5MHJINOg",
          "user_id": 1,
          "rev": 0,
          "exp": 1528376222,
          "fp": "b28493a6a29a5a38973a8a3e3abe7f34"
        }
    """

    def authenticate(self, request, consumer_username, encoded_jwt,
                     decoded_jwt):
        logger.info("Authenticating consumer {}".format(consumer_username))

        if consumer_username is None:
            return None

        if settings.DJANGO_SSO_REPLICATE_PROFILE:
            if encoded_jwt is None:
                return None

        sso_id = get_sso_id(consumer_username)

        try:
            user_profile = UserProfileModel.objects.get(sso_id=sso_id)
            user = user_profile
            if settings.DJANGO_SSO_HAS_EXTERNAL_USER_PROFILE_MODEL:
                user = user_profile.user

            if settings.DJANGO_SSO_REPLICATE_PROFILE:
                # must replicate user profile
                logger.info("Replicating user profile for {}".format(user))
                rev_changed = user_profile.sso_rev != decoded_jwt["rev"]
                first_access = not user.is_active and not user_profile.is_unsubscribed
                if rev_changed or first_access:
                    if rev_changed:
                        logger.info("Rev changed from {} to {} for {}, updating ..."
                                    .format(user_profile.sso_rev, decoded_jwt["rev"],
                                            consumer_username))
                    if first_access:
                        logger.info("{}'s first access, updating ...".format(
                            consumer_username))

                    # update local profile from SSO
                    sso_profile = get_profile_from_sso(sso_id=sso_id,
                                                       encoded_jwt=encoded_jwt)
                    update_local_profile_from_sso(sso_profile=sso_profile,
                                                  profile=user_profile)

                    logger.info("{} updated with latest data from SSO"
                                .format(consumer_username))
                else:
                    logger.info("Nothing changed for {}".format(consumer_username))
            else:
                # just updates user groups
                logger.info("Got user from headers {}".format(user))

            if settings.DJANGO_SSO_MANAGE_USER_GROUPS:
                # update user groups
                logger.info("Updating user groups for {}".format(user))

                consumer_groups = request.META.get(
                    settings.DJANGO_SSO_CONSUMER_GROUPS_HEADER, None)
                user_groups = get_user_groups_from_header(consumer_groups)

                update_user_groups(user, user_groups)

        except ObjectDoesNotExist:
            if settings.DJANGO_SSO_REPLICATE_PROFILE:
                # create local profile from SSO
                sso_profile = get_profile_from_sso(sso_id=sso_id,
                                                   encoded_jwt=encoded_jwt)

                user_profile = create_local_profile_from_sso(sso_profile=sso_profile)
                user = user_profile
                if settings.DJANGO_SSO_HAS_EXTERNAL_USER_PROFILE_MODEL:
                    user = user_profile.user
            else:
                # create local profile from headers
                user = create_local_profile_from_headers(request)

        return user
