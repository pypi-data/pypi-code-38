#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Core interface for the userinfo metadata objects to interface with CherryPy."""
from peewee import DoesNotExist
from cherrypy import HTTPError
from pacifica.metadata.rest.user_queries.user_search import UserSearch
from pacifica.metadata.rest.user_queries.user_lookup import UserLookup
from pacifica.metadata.orm import Users


def user_exists_decorator(func):
    """Wrap a method with user existence checking."""
    def func_wrapper(*args, **kwargs):
        """Wrapper to check for user existence."""
        try:
            user_id = args[0]
        except IndexError:
            user_id = kwargs['user_id']
        try:
            Users.get(Users.id == user_id)
            ret = func(*args, **kwargs)
            return ret
        except DoesNotExist:
            raise HTTPError(
                '404 User Does Not Exist',
                'No User with ID:{0} exists in the system'.format(user_id)
            )
    return func_wrapper


# pylint: disable=too-few-public-methods
class UserInfoAPI(object):
    """UserInfo API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.search = UserSearch()
        self.by_id = UserLookup()
        self.by_user_id = UserLookup()
