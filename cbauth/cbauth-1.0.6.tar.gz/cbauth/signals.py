from allauth.account.signals import user_logged_in
# from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login


@receiver(pre_social_login)
def create_jwt_token(sender, request, sociallogin, **kwargs):
    print('----------------- create_jwt_token')
    print('sender %s' % sender)
    print('user %s' % request)
    print('sociallogin %s' % sociallogin)
    print('----------------- END create_jwt_token')
    # dig into the sociallogin object to find the new access token.


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    print('---------------- post_login')
    print('sender: %s' % sender)
    print('user: %s' % user)
    print('request: %s' % request)
    print('---------------- END post_login')
