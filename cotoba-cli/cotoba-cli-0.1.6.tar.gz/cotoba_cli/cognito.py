import sys

import click
import warrant

from cotoba_cli import session
from cotoba_cli import config
from cotoba_cli import platform

ACCESS_KEY = 'dummy'
SECRET_KEY = 'dummy'
USER_POOL_REGION = 'ap-northeast-1'


def get_cognito_user(email='default'):
    session_dict = session.load()['default']
    if 'id_token' not in session_dict \
       or 'refresh_token' not in session_dict \
       or 'access_token' not in session_dict:
        click.echo('Not logged in.', err=True)
        sys.exit(1)

    config_dict = config.load()['default']
    if 'authorization' not in config_dict:
        click.echo('Set authorization ID.', err=True)
        sys.exit(1)
    authorization = config_dict['authorization']
    user_pool_id, client_id = platform.decode_cognito_setting(
        authorization)

    cognito_user = warrant.Cognito(
        user_pool_id,
        client_id,
        id_token=session_dict['id_token'],
        refresh_token=session_dict['refresh_token'],
        access_token=session_dict['access_token'],
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        user_pool_region=USER_POOL_REGION)

    try:
        if cognito_user.check_token():
            session.save(
                email=cognito_user.username,
                id_token=cognito_user.id_token,
                refresh_token=cognito_user.refresh_token,
                access_token=cognito_user.access_token)
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)

    return cognito_user
