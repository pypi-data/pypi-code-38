from .request import request
from . import validator


__all__ = ['User']


class User:
    def __init__(self, config):
        """
        :param config:, PRSConfig
        """
        self.config = config

    def get_by_address(self, address):
        return request(
            self.config.get_host(),
            method='GET',
            path=f'/users/{address}',
            debug=self.config.debug
        )

    def edit_profile(self, profile):
        """
        {
            'name': str,
            'title': str,
            'bio': str,
            'bigoneAccountId': str,
            'committee': str,
            'investor': str,
            'participant': str,
            'announcement': str,
            'reward_allowed': bool,
            'rewardDescription': str,
        }
        """
        validator.assert_exc(profile, 'profile cannot be null')
        auth_opts = self.config.get_auth_opts()
        return request(
            self.config.get_host(),
            method='POST',
            data=profile,
            path='/users',
            auth_opts=auth_opts,
            debug=self.config.debug
        )

    def upload_avatar(self, avatar_base64_str):
        validator.assert_exc(
            avatar_base64_str, 'avatar_base64_str cannot be null'
        )
        auth_opts = self.config.get_auth_opts()
        data = {'avatar': avatar_base64_str}
        return request(
            self.config.get_host(),
            method='POST',
            data=data,
            path='/users/avatar',
            auth_opts=auth_opts,
            debug=self.config.debug
        )
