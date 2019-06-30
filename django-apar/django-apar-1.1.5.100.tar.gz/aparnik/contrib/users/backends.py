from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.contrib.auth.models import Permission
from aparnik.settings import aparnik_settings
from aparnik.contrib.users.models import DeviceLogin
from aparnik.utils.utils import convert_iran_phone_number_to_world_number
import logging

User = get_user_model()


class AuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:

            username = kwargs.get(User.USERNAME_FIELD)
        try:
            username = convert_iran_phone_number_to_world_number(username)
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            User().set_password(password)
        else:
            # return user
            is_correct_password = False
            if aparnik_settings.USER_LOGIN_WITH_PASSWORD:
                # SMS
                is_correct_password = user.passwd == password
            else:
                is_correct_password = user.OTAVerify(password)

            if user.is_can_login() and is_correct_password:
                user.last_login = now()
                user.save()
                # because we can access the request in jwt :| we use device login to find last login
                # device_id = request.data.get('device_id', None)
                # if device_id is not None:

                return user
        return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(sys_id=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            logging.getLogger("error_logger").error("user with %(user_id)d not found")
            return None