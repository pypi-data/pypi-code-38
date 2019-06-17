#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API classes to access beeswax admin information
"""
from __future__ import unicode_literals

import ujson

from beeswax_wrapper.core.base_classes import BaseAPI


class Authentication(BaseAPI):
    """Beeswax Authentication API class"""

    paths = ['authenticate']

    def create(self, password, **kwargs):
        """
        :type password: str
        :param dict kwargs: user_id, email, account_id, keep_logged_in
        """
        parameters = dict(password=password, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, user_id, password, new_password):
        """
        :type user_id: int
        :type password: str
        :type new_password: str
        """
        parameters = dict(user_id=user_id, password=password, new_password=new_password)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self):
        # TODO: check this is correct
        return self._call('DELETE')


class Password(BaseAPI):
    """Beeswax Password API class"""

    paths = ['change_password']

    def create(self, user_id, email):
        """
        :type user_id: int
        :type email: str
        """
        parameters = dict(user_id=user_id, email=email)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, login_token, new_password, **kwargs):
        """
        :type login_token: str
        :type new_password: str
        :param dict kwargs: user_id, email
        """
        parameters = dict(login_token=login_token, new_password=new_password, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))


class Role(BaseAPI):
    """Beeswax Role API class"""

    paths = ['role']

    def retrieve(self, role_id, **kwargs):
        """
        :type role_id:
        :param dict kwargs: role_name, is_global, parent_role_id, active
        """
        parameters = dict(role_id=role_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: role_id, role_name, is_global, parent_role_id, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, role_name, parent_role_id, permissions, **kwargs):
        """
        :type role_name: str
        :type parent_role_id: int
        :type permissions: str
        :param dict kwargs: global, notes, active
        """
        parameters = dict(role_name=role_name, parent_role_id=parent_role_id, permissions=permissions, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, role_id, **kwargs):
        """
        :type role_id: int
        :param dict kwargs: role_name, global, parent_role_id, permissions, notes, active
        """
        parameters = dict(role_id=role_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, role_id):
        """
        :type role_id: int
        """
        parameters = dict(role_id=role_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class User(BaseAPI):
    """Beeswax User API class"""

    paths = ['user']

    def retrieve(self, user_id, **kwargs):
        """
        :type user_id: int
        :param dict kwargs: email, first_name, last_name, role_id, active
        """
        parameters = dict(user_id=user_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: user_id, email, first_name, last_name, role_id, active
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, email, role_id, **kwargs):
        """
        :type email: str
        :type role_id: int
        :param dict kwargs: first_name, last_name, notes, active, super_user, multi_account, send_product_comms
        """
        parameters = dict(email=email, role_id=role_id, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, user_id, **kwargs):
        """
        :type user_id: int
        :param dict kwargs: email, first_name, last_name, role_id, notes, active, super_user, multi_account,
            send_product_comms
        """
        parameters = dict(user_id=user_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, user_id):
        """
        :type user_id: int
        """
        parameters = dict(user_id=user_id)
        return self._call('DELETE', data=ujson.dumps(parameters))
