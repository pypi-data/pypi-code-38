import getpass
import sys
import locale as loc

import click

from cotoba_cli import platform
from cotoba_cli import session
from cotoba_cli import cli_platform
from cotoba_cli import cli_nlu
from cotoba_cli import config


@click.group(help='Cotoba-CLI')
def cli_root():
    pass


@cli_root.command(help='Sign up')
@click.option('--email', type=str, help='Email address.', required=True)
@click.option('--password', type=str, help='Password.')
def sign_up(email, password):
    if not password:
        password = getpass.getpass('Enter password: ')
        password_confirm = getpass.getpass('Enter password again: ')
        if password != password_confirm:
            click.echo('Password do not match.', err=True)
            sys.exit(1)
    try:
        user = platform.sign_up(email, password)
        session.initialize()
        session.save(
            email=email,
            id_token=user.id_token,
            access_token=user.access_token,
            refresh_token=user.refresh_token)
    except platform.SignUpEmailExistsException:
        click.echo('Email address already exists.', err=True)
        sys.exit(1)
    except platform.SignUpPasswordInvalidException:
        click.echo('Password is invalid.', err=True)
        sys.exit(1)


@cli_root.command(help='Login and renews session token.')
@click.option('--email', type=str, help='Email address', required=True)
@click.option('--password', type=str, help='Password.')
def login(email, password):
    if not password:
        password = getpass.getpass('Enter password: ')
    try:
        user = platform.login(email, password)
        session.initialize()
        session.save(
            email=email,
            id_token=user.id_token,
            access_token=user.access_token,
            refresh_token=user.refresh_token)
    except platform.LoginEmailNotFoundException:
        click.echo('Email address or password is not correct.', err=True)
        sys.exit(1)


@cli_root.command(help='Config setting.')
# @click.option('--x-api-key', type=str, help='X-Api-Key.')
# @click.option('--dev-key', type=str, help='Developer-Key.')
# @click.option('--api-key', type=str, help='Api-Key.')
# @click.option('--user', type=str, help='User ID.')
@click.option('--locale', type=str, help='Locale.')
@click.option('--endpoint-url', 'url', type=str, help='Endpoint URL.')
@click.option('--authorization', type=str, help='Authorization ID.')
@click.option('--show-config', 'show_config', is_flag=True,
              help='Show Config.')
def configure(locale,
              url,
              authorization,
              show_config):

    config.initialize()
    config_dict = config.load()['default']

    if show_config:
        # コンソール上に現在の設定値一覧表示
        # click.echo('x-api-key:' + config_dict['x-api-key'])
        # click.echo('developer-key:' + config_dict['developer-key'])
        # click.echo('api-key:' + config_dict['api-key'])
        # click.echo('user-id:' + config_dict['user-id'])
        click.echo('locale:' + config_dict['locale'])
        click.echo('endpoint-url:' + config_dict['endpoint-url'])
        click.echo('authorization:' + config_dict['authorization'])
        return

    if any(
            [
                # x_api_key,
                # dev_key,
                # api_key,
                # user,
                locale,
                url,
                authorization
            ]
    ):
        # オプション設定時は指定されたものだけ上書きする
        # x_api_key = (x_api_key if x_api_key is not None
        #              else config_dict['x-api-key'])
        # dev_key = (dev_key if dev_key is not None
        #            else config_dict['developer-key'])
        # api_key = (api_key if api_key is not None
        #            else config_dict['api-key'])
        # user_id = (user if user is not None
        #            else config_dict['user-id'])
        locale = (locale if locale is not None
                  else config_dict['locale'])
        url = (url if url is not None
               else config_dict['endpoint-url'])
        authorization = (authorization if authorization is not None
                         else config_dict['authorization'])
    else:
        # オプションで未指定の場合のみコンソールで入力を行う
        click.secho('<leave blank in case unchanged>',
                    fg='bright_cyan')
        # x_api_key = show_current_and_input_value('x-api-key', config_dict)
        # dev_key = show_current_and_input_value('developer-key', config_dict)
        # api_key = show_current_and_input_value('api-key', config_dict)
        # user_id = show_current_and_input_value('user-id', config_dict)
        locale = show_current_and_input_value('locale', config_dict)
        url = show_current_and_input_value('endpoint-url', config_dict)
        authorization = show_current_and_input_value('authorization',
                                                     config_dict)

    available_locales_values = loc.windows_locale.values()
    available_locales = [
        v.replace('_', '-') for v in available_locales_values
    ]
    if locale not in available_locales:
        # 不正なロケール指定時はエラーの旨を表示し変更しない
        click.secho('Invalid locale.', fg='red')
        locale = config_dict['locale']
    # 設定した値をファイルに保存
    config.save(
        # x_api_key=x_api_key,
        # dev_key=dev_key,
        # api_key=api_key,
        # user_id=user_id,
        locale=locale,
        url=url,
        authorization=authorization
    )


# 現在の設定値の表示と値の入力
def show_current_and_input_value(key_name, config_dict):
    key_and_colon = key_name + ':'
    # 現在の設定値を緑色で表示
    click.echo(click.style(key_and_colon
                           + config_dict[key_name],
                           fg='green')
               )
    input_value = input(key_and_colon)
    # 未入力時は設定しない
    input_value = (input_value if len(str(input_value)) != 0
                   else config_dict[key_name])
    return input_value


cli_root.add_command(cli_platform.cli_platform, 'platform')
cli_root.add_command(cli_nlu.cli_nlu, 'nlu')


if __name__ == '__main__':
    cli_root()
