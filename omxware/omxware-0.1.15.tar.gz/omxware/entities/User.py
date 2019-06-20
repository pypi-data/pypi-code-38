# -*- coding: utf-8 -*-

from omxware.config import Connection
from omxware.entities.Entity import Entity


class User(Entity):
    """OMXWare User Entity Class"""

    _first_name = None  # int
    _last_name = None  # str
    _username = None  # str
    _email = None  # str
    _picture = None  # str
    _locale = None  # str
    _roles = None  # [str]
    _realm_roles = None  # [str]

    def __init__(self, connecthdr: Connection, user):
        """
        Construction

        {id, name, type, json} attributes are read by the super().constructor()
        So just parse and load the remaining attributes
        """

        super().__init__(connecthdr, user)
        self._is_preview_obj = False

        if isinstance(user, dict):
            if not ("id" in user):
                raise Exception("The User id missing")

        # extracting the first_name
            if 'first_name' in user:
                self._first_name = user['first_name']

        # extracting the last_name
            if 'last_name' in user:
                self._last_name = user['last_name']

        # extracting the username
            if 'username' in user:
                self._username = user['username']

        # extracting the email
            if 'email' in user:
                self._email = user['email']

        # extracting the picture
            if 'picture' in user:
                self._picture = user['picture']

        # extracting the locale
            if 'locale' in user:
                self._locale = user['locale']

        # extracting the roles
            if 'roles' in user:
                self._roles = []
                role_lst = user['roles']

                if isinstance(role_lst, list):
                    for role in role_lst:
                        self._roles.append(role)

        # extracting the roles
            if 'realm_roles' in user:
                self._realm_roles = []
                role_lst = user['realm_roles']

                if isinstance(role_lst, list):
                    for role in role_lst:
                        self._realm_roles.append(role)

        self._type = 'user'

    def firstname(self):
        """
        Get the First Name for Current user

        :return: str :   First Name
        """
        return self._first_name

    def lastname(self):
        """
        Get the Last Name for Current user

        :return: str :   Last Name
        """
        return self._last_name

    def username(self):
        """
        Get the username for Current user

        :return: str :   Username
        """
        return self._username

    def email(self):
        """
        Get the email for Current user

        :return: str :   Email
        """
        return self._email

    def locale(self):
        """
        Get the locale for Current user

        :return: str :   Locale
        """
        return self._locale

    def roles(self):
        """
        Get the roles assigned for Current user

        :return: [str] :   User Roles
        """
        return self._roles

    def _isAdmin(self):
        """
        Check if the Current user is an OMX Admin

        :return:    Boolean
        """
        if 'omxware-admin' in self.roles():
            return True
        else:
            return False

    def _role(self, omx_role=None):
        """
        Check if the Current user has a role assigned

        Parameters:
            :param omx_role: OMXWare user role to check
            :type omx_role: str

        Returns:
            :return:    Boolean
        """
        if omx_role is None:
            raise Exception("No 'omx_role' to check!")
        elif omx_role in self.roles():
            return True
        else:
            return False
