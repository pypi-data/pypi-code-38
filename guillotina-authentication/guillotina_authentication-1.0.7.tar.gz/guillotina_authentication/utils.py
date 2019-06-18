import os
from hashlib import sha1
from urllib.parse import urlencode

import aioauth_client
from guillotina import app_settings
from guillotina_authentication import cache, exceptions

aioauth_client.TwitterClient.authentication_url = 'https://api.twitter.com/oauth/authenticate'  # noqa


class HydraClient(aioauth_client.OAuth2Client):

    @property
    def user_info_url(self):
        return os.path.join(self.base_url, 'userinfo')

    @staticmethod
    def user_parse(data):
        return {
            'id': data['sub'],
            'allowed_scopes': data.get('allowed_scopes') or [],
            'data': data.get('data') or {},
            'email': data.get('email'),
            'phone': data.get('phone'),
            'username': data.get('username')
        }


config_mappings = {
    'twitter': aioauth_client.TwitterClient,
    'facebook': aioauth_client.FacebookClient,
    'github': aioauth_client.GithubClient,
    'google': aioauth_client.GoogleClient,
    'hydra': HydraClient
}

oauth1_providers = ('twitter', )


def get_client(provider, **kwargs):
    if provider not in app_settings['auth_providers']:
        raise exceptions.ProviderNotConfiguredException(provider)
    provider_config = app_settings['auth_providers'][provider]
    if 'configuration' not in provider_config:
        raise exceptions.ProviderMisConfiguredException(provider)
    configuration = provider_config['configuration']
    if provider not in config_mappings:
        # in this case, make sure we have all necessary config to build
        if ('authorize_url' not in configuration or
                'access_token_url' not in configuration):
            raise exceptions.ProviderNotSupportedException(provider)
    kwargs.update(configuration)
    if provider not in config_mappings:
        ProviderClass = aioauth_client.OAuth2Client
    else:
        ProviderClass = config_mappings[provider]
    client = ProviderClass(**kwargs)
    client.provider = provider
    client.send_state = provider_config.get('state') or False
    return client


async def get_authorization_url(client, *args, callback=None, **kwargs):
    config = app_settings['auth_providers'][client.provider]
    if 'scope' in config:
        if 'scope' not in config:
            kwargs['scope'] = config['scope']
        else:
            kwargs['scope'] += ' ' + config['scope']

    args = list(args)
    url = kwargs.pop('url', client.authorize_url)
    if client.provider in oauth1_providers:
        request_token, request_token_secret, _ = await client.get_request_token(  # noqa
            oauth_callback=callback
        )
        args.append(request_token)
        params = {'oauth_token': request_token or client.oauth_token}
        await cache.put(request_token, request_token_secret)
        return url + '?' + urlencode(params)
    else:
        params = dict(client.params, **kwargs)
        params.update({
            'access_type': 'offline',
            'prompt': 'consent',
            'client_id': client.client_id,
            'response_type': 'code',
            'redirect_uri': callback
        })
        if client.send_state:
            params['state'] = sha1(str(
                aioauth_client.RANDOM()).encode('ascii')).hexdigest()
            await cache.put(params['state'], 'nonce')
        return url + '?' + urlencode(params)


async def get_authentication_url(client, *args, callback=None, **kwargs):
    if not hasattr(client, 'authentication_url'):
        return await get_authorization_url(
            client, *args, callback=callback, **kwargs)
    kwargs['url'] = client.authentication_url
    return await get_authorization_url(
        client, *args, callback=callback, **kwargs)
