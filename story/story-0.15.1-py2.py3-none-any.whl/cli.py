# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys
import time
import typing
from urllib.parse import urlencode
from uuid import uuid4

import click
import click_help_colors
import emoji
from blindspin import spinner
from raven import Client
from requests import Session

from .helpers.didyoumean import DYMGroup
from .version import version as story_version
from .version import compiler_version
from .storage import config, cache
from .support import echo_support
from .utils import find_story_yml, get_app_name_from_yml, get_asyncy_yaml
from .ensure import ensure_latest

# Initiate requests session, for connection pooling.
requests = Session()

# Typing hints.
Content = typing.Union[str, typing.Mapping, typing.List]

if not os.getenv('TOXENV'):
    enable_reporting = True
    sentry = Client(
        'https://007e7d135737487f97f5fe87d5d85b55@sentry.io/1206504'
    )
else:
    enable_reporting = False
    sentry = Client()

data = None


def get_access_token():
    return data['access_token']


def get_user_id():
    """Returns the current user id, if any is available."""
    return data.get('id')


def track_profile():
    _make_tracking_http_request(
        'https://stories.storyscriptapp.com/track/profile',
        {
            'id': str(get_user_id()),
            'profile': {
                'Name': data['name'],
                'Email': data.get('email'),
                'GitHub Username': data.get('username'),
                'Timezone': time.tzname[time.daylight],
            },
        },
    )


def _make_tracking_http_request(url, json_data):
    """
    Forks the HTTP call into the background.
    The caller does not make the call, and this method returns just after
    forking the process.

    The child makes the call, and does not return back to the caller,
    but instead just exits (sys.exit(0)). This is to ensure that whatever
    needs to happen after this method is called, does not happen twice.
    """
    if not enable_reporting:
        return
    if sys.platform != 'linux' and sys.platform != 'darwin':
        try:
            requests.post(url, json=json_data)
        except Exception:
            # ignore issues with tracking
            pass

        return

    pid = os.fork()
    if pid > 0:
        # This is the parent process.
        return

    try:
        requests.post(url, json=json_data)
    except Exception:
        # ignore issues with tracking
        pass

    # This is the child process. Exit now.
    sys.exit(0)


def track(event_name, extra: dict = None):
    if extra is None:
        extra = {}

    extra['CLI version'] = story_version
    _make_tracking_http_request(
        'https://stories.storyscriptapp.com/track/event',
        {
            'id': str(get_user_id()),
            'event_name': event_name,
            'event_props': extra,
        },
    )


def initiate_login():
    global data

    click.echo(
        'Hi! Thank you for using '
        + click.style('Storyscript Cloud', fg='magenta')
        + '.'
    )
    click.echo('Please login with GitHub to get started.')

    state = uuid4()

    query = {'state': state}

    url = f'https://stories.storyscriptapp.com/github?{urlencode(query)}'

    click.launch(url)
    click.echo()
    click.echo("Visit this link if your browser doesn't open automatically:")
    click.echo(url)
    click.echo()

    while True:
        with spinner():
            try:
                url = (
                    'https://stories.storyscriptapp.com'
                    '/github/oauth_callback'
                )
                r = requests.get(url=url, params={'state': state})

                if r.text == 'null':
                    raise IOError()

                r.raise_for_status()
                break

            except IOError:
                time.sleep(0.5)

            except KeyboardInterrupt:
                click.echo('Login failed. Please try again.')
                sys.exit(1)

    if r.json().get('beta') is False:
        click.echo('Hello! Storyscript Cloud is in private beta at this time.')
        click.echo(
            'We\'ve added you to our beta testers queue, '
            'and you should hear from us\nshortly via email'
            ' (which is linked to your GitHub account).'
        )
        sys.exit(1)

    data = r.json()
    for k, v in data.items():
        config.store(k, v)

    init()

    click.echo(emoji.emojize(':waving_hand:') + f'  Welcome {data["name"]}!')
    click.echo()
    click.echo('Create a new app with:')
    print_command('story apps create')

    click.echo()

    click.echo('To list all your apps:')
    print_command('story apps')

    click.echo()
    track('Login Completed')
    track_profile()


def user() -> dict:
    """Get the active user."""

    global data

    if data:
        return data
    else:
        initiate_login()
        return data


def print_command(command):
    """Prints a command to the CLI."""

    click.echo('  $ ' + click.style(command, fg='magenta'))


def assert_project(command, app, default_app, allow_option):
    if app is None:
        click.echo(
            click.style('No StoryScript Cloud application found.', fg='red')
        )
        click.echo()
        click.echo('Create an application with:')

        print_command('story apps create')

        sys.exit(1)

    elif not allow_option and app != default_app:
        click.echo(
            click.style(
                'The --app option is not allowed with the {} command.'.format(
                    command
                ),
                fg='red',
            )
        )
        sys.exit(1)
    return app


def settings_set(content: Content, location: str):
    """Overwrites settings, to given location and content."""

    # Ensure the path is created and exists..
    loc_dir = os.path.abspath(location)
    loc_dir = os.path.dirname(loc_dir)

    os.makedirs(loc_dir, exist_ok=True)

    # If content is an object-like...
    if isinstance(content, (list, dict)):
        content = json.dumps(content, indent=2)

    # Write to the file.
    with open(location, 'w+') as file:
        file.write(content)


def init(config_path=None):
    global data

    if config_path:
        config.change_path(config_path)

    data = config.as_dict()

    try:
        sentry.user_context({'id': get_user_id(), 'email': data['email']})
    except Exception:
        pass


def stream(cmd: str):
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)

    while True:

        output = process.stdout.readline()

        if output == b'' and process.poll() is not None:
            break

        if output:
            click.echo(output.strip())


def echo_version(*args, **kwargs):
    click.echo(
        click.style('Storyscript CLI', fg='magenta')
        + ': v'
        + story_version
        + click.style(', ', dim=True)
        + click.style('Storyscript Compiler', fg='cyan')
        + ': v'
        + compiler_version
        + '.'
    )


class CLIGroup(DYMGroup, click_help_colors.HelpColorsGroup):
    pass


# @click.option('--url', callback=version)
@click.group(
    cls=CLIGroup,
    help_headers_color='yellow',
    help_options_color='magenta',
    add_help_option=True,
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "auto_envvar_prefix": "STORY",
    },
)
@click.option('--version', 'do_version', is_flag=True)
@click.option('--config', 'do_config', is_flag=True, hidden=True)
@click.option('--config_path', 'config_path', hidden=True)
@click.option('--cache', 'do_cache', is_flag=True, hidden=True)
@click.option(
    '--disable-version-check', 'dont_check', is_flag=True, hidden=True
)
@click.option('--completion', 'do_completion', is_flag=True, hidden=True)
@click.option('--reset', 'do_reset', is_flag=True, hidden=True)
@click.option('--support', 'do_support', is_flag=True, hidden=True)
def cli(
    do_version=False,
    do_config=False,
    do_cache=False,
    do_reset=False,
    do_support=False,
    do_completion=False,
    dont_check=False,
    config_path=False,
):
    """
    Hello! Welcome to Storyscript.

    We hope you enjoy, & we look forward to your feedback!

    Documentation: https://docs.storyscript.io/
    """

    # Check for new versions, if allowed.
    if not dont_check:
        ensure_latest()

    if do_version:
        echo_version()
        sys.exit(0)

    elif do_cache:
        click.echo(cache.path)
        sys.exit(0)

    elif do_config:
        click.echo(config.path)
        sys.exit(0)

    elif do_reset:
        os.remove(cache.path)
        os.remove(config.path)
        click.echo('Storyscript CLI installation reset.')
        sys.exit(0)

    elif do_support:
        echo_support()

    else:
        init(config_path=config_path)
