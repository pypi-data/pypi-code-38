import re
from typing import Union
import requests
import random

from aspace import base_client
from aspace import constants
from aspace.client_extensions import record_streams

VALID_USER_URI_RE = re.compile(constants.VALID_USER_URI_REGEX)


class UserManagementService(object):
    """
    Contains methods that can be used to perform batch updates on user records
    using different components of the ArchivesSpace API.
    """

    def __init__(self, client: base_client.BaseASpaceClient):
        self._client = client
        self._record_streams = record_streams.RecordStreamingService(client)

    def get_all(self) -> list:
        """
        Returns a list of all of the non-system user records in the
        ArchivesSpace instance.
        """
        num_users_resp = self._client.get('/users', params={'all_ids': True})

        assert num_users_resp, num_users_resp.text
        num_users = len(num_users_resp.json())

        all_users_resp = self._client.get(
            '/users',
            params={
                'page': 1,
                'page_size': num_users,
            },
        )

        assert all_users_resp, all_users_resp.text
        return all_users_resp.json().get('results', [])

    def stream(self) -> iter:
        """
        Streams all non-system user records from the ArchivesSpace instance.
        Please see the RecordStreamingService extensions for other streaming
        methods.
        """
        return self._record_streams.users()

    def _change_password(self, user_record: dict,
                         new_password: Union[str, callable],):
        """
        Changes the password for the user record. Returns the response from
        the ArchivesSpace server. Only to be used internally.
        """
        password = (
            new_password(user_record) if callable(new_password) else
            new_password
        )

        assert (password is not None), (
            'Unable to create a new password for the current user: "%s"' %
            user_record['username']
        )

        return self._client.post(
            user_record['uri'],
            json=user_record,
            params={'password': password}
        )

    def change_password(self, user: Union[int, str, dict],
                        new_password: Union[str, callable],):
        """
        Changes the password for the user specified by the URI. Returns the
        response from the ArchivesSpace API.

        :user: The identifier for the user, which can be a URI, user ID,
        username, or a dict representation of the user object. NOTE: The user
        record will be downloaded and reuploaded, which will increment the
        user's lock_version.

        :new_password: The new password to set for the user. If a string is
        passed, that string will be used to set the password for the user. If
        new_password is callable, new_password should accept the user record
        dict and should return a string.
        """

        user_record = self.get(user)
        return self._change_password(user_record, new_password)

    def change_all_passwords(self, new_password: Union[str, callable],
                             include_admin=False) -> list:
        """
        Changes the passwords for all of the users in the ArchivesSpace
        instance, not including any of the system users.

        Returns a list of all of the responses from the ArchivesSpace server.

        :new_password: The new password to set for all users. If a string is
        passed, that string will be used to set the password for all users. If
        new_password is callable, new_password should accept a user record
        dict and should return a string, which can be used to set a unique
        password for each user.

        :include_admin: Determines whether the `admin` user should be
        included in the global password reset.
        """
        return [
            self._change_password(user, new_password)

            for user in self.get_all()

            if (not user['username'] == 'admin') or include_admin
        ]

    def randomize_all_passwords(self, password_characters: str = None,
                                password_length: int = 16,
                                new_admin_password: str = None,
                                ):
        """
        Resets all of the non-admin user passwords on the target ArchivesSpace
        instance, using a random character generator. If `password_characters`
        is `None`, `constants.DEFAULT_PASSWORD_CHARACTER_SET` will be used.

        Sets the admin password to a specific value, if a value is specified.
        If no specific value is specified for the new admin password, the admin
        password will not be changed.
        """

        rng = random.Random()

        password_characters = (
            password_characters or constants.DEFAULT_PASSWORD_CHARACTER_SET
        )

        for resp in self.change_all_passwords(
            lambda _: ''.join(rng.sample(
                password_characters,
                password_length,
            ))
        ):
            assert resp.ok, resp.text

        if new_admin_password:
            resp = self.change_password('admin', new_admin_password)
            assert resp.ok, resp.text

    def get(self, user: Union[int, str, dict]) -> dict:
        """
        Gets a user based on a URI, user ID, username, or a dict
        representation of the user object. Returns the dict representation of
        the user's JSON model object returned by the API.

        :user: A uri, integer user id, or username for the user record that
        will be retrieved.
        """
        if isinstance(user, str):
            if VALID_USER_URI_RE.match(user):
                resp = self._client.get(user)
                assert resp.ok, resp.text
                return resp.json()

            return self.get_by_username(user)

        if isinstance(user, int):
            resp = self._client.get('/users/{}'.format(user))
            assert resp.ok, resp.text
            return resp.json()

        if isinstance(user, dict):
            identifier = (
                user['uri'] if 'uri' in user else
                user['id'] if 'id' in user else
                user['username'] if 'username' in user else
                None
            )

            assert identifier, 'Not a valid user object: {}'.format(user)
            return self.get(user)

        assert False, 'Unable to find user: "{}"'.format(user)

    def get_by_username(self, user: str) -> dict:
        """
        Attempts to get a user record using a username through the following
        steps:

        1. Determine the number of users
        2. Get all user accounts as a list of dicts
        3. Filter the list based on the username property, returning the first
           one that matches the username
        4. Raise if None, otherwise return the result
        """

        user_record = next(filter(
            lambda u_rec: u_rec.get('username', None) == user,
            self.get_all()
        ), None)

        assert user_record, 'No user found with username: "{}"'.format(user)
        return user_record

    def create(self, user: dict, password: str) -> requests.Response:
        """
        Creates a new user and returns the HTTP response from the server.

        :user: A dict representation of a user record.

        :password: The password for the new user.
        """

        return self._client.post(
            '/users',
            json=user,
            params={'password': password},
        )

    def current_user(self) -> requests.Response:
        """
        Returns the HTTP response from the `/users/current-user` endpoint.
        """
        return self._client.get('/users/current-user')
