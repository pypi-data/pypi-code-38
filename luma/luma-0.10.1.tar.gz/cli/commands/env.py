"""
    These sub-commands and their corresponding logic are both implamented in this file.
    TO DO: Break out the logic for these commands into a seperate behavior file.
"""

from pathlib import Path
from cli import pyke
import click
import json
import os

@click.group(help='An Env tells the CLI where to get valid tokens for calls to the platform.\
Environments are analogous to auth realms.')
def env():
    pass

@click.command('config')
@click.option('--env-name', prompt=True, help='The environment name')
@click.option('--app', prompt=True, help='The App URL')
@click.option('--token', prompt=True, help='The URL for auth tokens')
@click.option('--audience', prompt=True)
@click.option('--client-id', prompt=True)
@click.option('--client-secret', prompt=True)
@click.option('--json', 'json_flag', is_flag=True, help='Return raw json from the platform.')
def config(app, token, audience, client_id, client_secret, env_name, json_flag):
    config_data = pyke.auth.load_config()

    env_data = {
      'app': app,
      'token': token,
      'audience': audience,
      'clientId': client_id,
      'clientSecret': client_secret
    }

    config_data['envs'][env_name] = env_data

    pyke.Util().login_without_context(env_name, config_data=config_data)

    pyke.auth.save_config(config_data)

    if json_flag:
        click.echo(json.dumps(config_data))
        return
    else:
        data = []
        for key in config_data['envs'].keys():
            config_data['envs'][key]['envName'] = str(key)
            data.append(config_data['envs'][key])

        pyke.Util().print_table(data, '{envName} {app} {audience} {token}')

@click.command('ls')
@click.option('--format', '-f', default='{envName} {app} {audience} {token}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json', 'json_flag', is_flag=True, help='Return raw json.')
def list(format, json_flag):
    config = pyke.auth.load_config()

    data = []
    for key in config['envs'].keys():
        config['envs'][key]['envName'] = str(key)
        data.append(config['envs'][key])

    if json_flag:
        click.echo(json.dumps(config['envs']))
        return

    pyke.Util().print_table(data, format)

@click.command('rm')
@click.option('--env-name', prompt=True, help='Environment to delete')
def delete(env_name):
    config_data = pyke.auth.load_config()
    env_data = config_data["envs"][env_name]
    del config_data["envs"][env_name]

    pyke.auth.save_config(config_data)

    click.echo("Deleted env:")
    click.echo(json.dumps(pyke.auth.sanatize_data(env_data)))

env.add_command(config)
env.add_command(list)
env.add_command(delete)
