import urllib.request
from .api_meta import api_meta

authhandler = urllib.request.HTTPDigestAuthHandler()


def install_auth_handlers(config):
    '''Authentication handler installation function
    '''
    for service in ['movida', 'sequence']:
        for env, creds in config.items():
            env = api_meta[service][env]
            authhandler.add_password(env.realm, env.base_url, creds['name'], creds['password'])
            opener = urllib.request.build_opener(authhandler)
            urllib.request.install_opener(opener)
