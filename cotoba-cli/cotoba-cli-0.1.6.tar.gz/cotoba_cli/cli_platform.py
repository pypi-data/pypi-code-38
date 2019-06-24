import os
import sys

import click

from cotoba_cli.cognito import get_cognito_user
from cotoba_cli import platform

from cotoba_cli import cli_test as test
from cotoba_cli import config


@click.group(help='platform')
@click.option('--endpoint-url', type=str, help='Endpoint URL', default=None)
@click.pass_context
def cli_platform(context, endpoint_url):
    if not context.obj:
        context.obj = {}
    if not endpoint_url:
        if os.environ.get('COTOBA_ENDPOINT_URL'):
            endpoint_url = os.environ.get('COTOBA_ENDPOINT_URL')
        elif config.load()['default'].get('endpoint-url'):
            endpoint_url = config.load()['default'].get('endpoint-url')
        else:
            click.echo('endpoint-url is not set.', err=True)
            sys.exit(1)

    context.obj['endpoint_url'] = endpoint_url


@cli_platform.command(help='Create a bot.')
@click.option('--file', 'file_path', type=str, required=True,
              help='Path to zipped bot file.')
@click.option('--message', type=str, default=None)
@click.option('--nlu-url', type=str, default=None)
@click.pass_context
def create_bot(context, file_path, message, nlu_url):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.create_bot(cognito_user,
                              file_path,
                              message=message,
                              nlu_url=nlu_url,
                              endpoint_url=endpoint_url,)
    res.print()


@cli_platform.command(help='Get a bot by bot id.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--output', 'zipfile_path', type=str,
              help='Download a scenario as zip file format.')
@click.pass_context
def get_bot(context, bot_id, zipfile_path):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.get_bot(cognito_user,
                           bot_id,
                           zipfile_path,
                           endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='List bots.')
@click.pass_context
def list_bots(context):
    endpoint_url = context.obj['endpoint_url']
    cognito_user = get_cognito_user()
    res = platform.list_bots(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Update bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--file', 'filepath', type=str,
              help='File path to scenario zip file.')
@click.option('--message', type=str, default=None)
@click.option('--nlu-url', type=str, default=None)
@click.pass_context
def update_bot(context, bot_id, filepath, message, nlu_url):
    endpoint_url = context.obj['endpoint_url']
    cognito_user = get_cognito_user()
    res = platform.update_bot(cognito_user,
                              bot_id=bot_id,
                              endpoint_url=endpoint_url,
                              filepath=filepath,
                              message=message,
                              nlu_url=nlu_url)
    res.print()


@cli_platform.command(help='Delete bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.pass_context
def delete_bot(context, bot_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.delete_bot(cognito_user, bot_id,
                              endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Run bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.pass_context
def run_bot(context, bot_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.run_bot(cognito_user, bot_id, endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Stop bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.pass_context
def stop_bot(context, bot_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.stop_bot(cognito_user, bot_id, endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Ask bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--user-id', type=str, help='User id to keep conversation.',
              required=True)
@click.option('--utterance', type=str, help='Content of utterance.',
              required=True)
# TODO: add api key option.
# @click.option('--api-key', type=str, help='Api key.')
@click.pass_context
def ask_bot(context, bot_id, user_id, utterance):
    endpoint_url = context.obj['endpoint_url']
    res = platform.ask_bot(bot_id=bot_id,
                           user_id=user_id,
                           utterance=utterance,
                           locale=config.load()['default'].get('locale'),
                           endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Debug bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--user-id', type=str, help='User id to keep conversation.')
# TODO: add api key option.
# @click.option('--api-key', type=str, help='Api key.')
@click.pass_context
def debug_bot(context, bot_id, user_id):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.debug_bot(cognito_user,
                             bot_id=bot_id,
                             user_id=user_id,
                             endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Update API key.')
@click.pass_context
def update_api_key(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.update_api_key(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Update API key.')
@click.pass_context
def update_developer_key(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.update_developer_key(cognito_user,
                                        endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Delete API key.')
@click.pass_context
def delete_api_key(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.delete_api_key(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Delete API key.')
@click.pass_context
def delete_developer_key(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.delete_api_key(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Get API key.')
@click.pass_context
def get_api_key(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.get_api_key(cognito_user, endpoint_url=endpoint_url)
    res.print()


@cli_platform.command(help='Get API key.')
@click.pass_context
def get_developer_key(context):
    cognito_user = get_cognito_user()
    endpoint_url = context.obj['endpoint_url']
    res = platform.get_developer_key(cognito_user,
                                     endpoint_url=endpoint_url)
    res.print()


cli_platform.add_command(test.cli_test, 'test')
