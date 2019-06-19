"""Settings for rest_auth.

Settings used by rest_auth can be overriden from your *settings.py* file.
"""

REST_AUTH_EMAIL_OPTIONS = {
}
"""Default: ``{}``

Options for email, which is sent to reset password.
Detail options guide `here. <>`_
"""

REST_AUTH_LOGIN_EMPTY_RESPONSE = True
"""Default: ``True``

Set this to ``False`` if your LoginView should return non-empty response.
"""

REST_AUTH_LOGIN_SERIALIZER_CLASS = 'rest_auth.serializers.LoginSerializer'
"""Default: ``"rest_auth.serializers.LoginSerializer"``

Serializer to log in. Update this if you use customized auth backend.
"""

REST_AUTH_SIGNUP_REQUIRE_EMAIL_CONFIRMATION = False
"""Default: ``False``

If your sign-up process has verification-via-email, set this flag to
``True`` to send email.

.. WARNING::
    This functionality is not implemented yet.
"""

prefix = 'REST_AUTH'
