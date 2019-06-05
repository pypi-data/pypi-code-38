from django.dispatch import Signal

user_created = Signal(providing_args=['instance', 'oauth_info'])
"""Sent when a user is created by logging in via Blender ID.

:param instance: the user model instance.
:param oauth_info: the info dict received from Blender ID, contains
    'id', 'nickname', 'email', 'full_name', and possibly other keys.
"""
