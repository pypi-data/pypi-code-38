"""
Django Rest Framework Auth provides very simple & quick way to adopt
authentication APIs' to your django project.


Rationale
---------

django-rest-framework's `Serializer` is nice idea for detaching
business logic from view functions. It's very similar to django's
``Form``, but serializer is not obligible for rendering response data,
and should not. - django forms also do this, seriously!!!
some expert beginners just know form is ONLY FOR `html form rendering` :(

Unluckily, even though django already provides forms and views
for authentication, We cannot use these for REST-APIs. It uses forms!!
(rest_framework does not use forms.)

We think there should be some serializers & views (or viewsets)
to use ``rest_framework``'s full features.
(such as throttling, pagination, versioning or content-negotiations)

Let's have a good taste of these elegant implementations.


API Endpoints
-------------

Below API endpoints can be re-configured if you write your urls.py

* POST /login/
    * username
    * password

    authenticate user and persist him/her to website

* POST /logout/
    let a user logged out.

.. NOTE::
    Logout from HTTP GET is not implemented.

* POST /forgot/
    * email

    send a link for resetting password to user


* GET /reset/{uid64}/{token}/
    * uid64, token - automatically generated tokens (when email is sent)
    * new_password
    * new_password (confirm)

    reset a password for user

* GET /reset/d/
    a view seen by user after resetting password

* POST /change-password/
    * old_password
    * new_password
    * new_password (confirm)

    change a password for user

* GET /api-root/
    * see api lists
"""

__version__ = '0.8.0'
