"""
    These sub-commands and their corresponding logic are both implamented in this file.
    TO DO: Break out the logic for these commands into a seperate behavior file.
"""

from pathlib import Path
from cli import pyke
import requests
import urllib3
import click
import json
import os

verify_tls = os.environ.get('LUMA_CLI_VERIFY_TLS', None)
if verify_tls == 'false' or verify_tls == 'False':
  verify_tls = False
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
else:
  verify_tls = None

@click.group('org', help='Get information about Orgs such as parent-child org relationships')
def organization():
  pass

@click.command('ls', help="List the Orgs you can make profiles for. \
The 'isTest' column in the returned table indicates if a studio is a test org or a prod org.")
@click.option('--env', prompt=True, help='The Env to point to')
@click.option('--format', '-f', default='{id} {name} {instanceType} {isTest}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--filter', default='')
@click.option('--json', 'json_flag', is_flag=True, help='Return raw json from the platform.')
def list(env, format, filter, json_flag):
  handlers = {
    'instanceType': lambda x: 'dev' if x == 'cc' else x
  }

  if 'instanceType=dev' in filter:
    filter = filter.replace('instanceType=dev', 'instanceType=cc')

  if 'isTest=None' in filter:
    filter = filter.replace('isTest=None', 'instanceType=cc')

  config = pyke.auth.load_config()

  headers = {
      'Authorization': 'Bearer ' + pyke.Util().login_without_context(env),
      'Content-Type': 'application/json'
  }
  try:
      app_name = config['envs'][env]['app'].replace(" ", "")
  except:
      raise click.ClickException(click.style("Env not configured", fg='red'))

  resp = requests.get('{}/auth/v1/me/companies?sort=name&{}'.format(app_name, filter), headers=headers, verify=verify_tls)

  if json_flag:
      click.echo(resp.text)
      return

  pyke.Util().print_table(resp.json()['payload']['data'], format, handlers=handlers)

@click.command('child-orgs', help='List the Orgs that a parent Org can share objects with')
@click.option('--profile', '-p', prompt=True, help='The org whose children you want to list', autocompletion=pyke.auth.get_profile_names)
@click.option('--format', '-f', default='{id} {name} {instanceType} {isTest}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--filter', default='')
@click.option('--json', 'json_flag', is_flag=True, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def child_companies(profile, format, filter, json_flag):
  util = pyke.Util()

  if 'instanceType=dev' in filter:
    filter = filter.replace('instanceType=dev', 'instanceType=cc')

  if 'isTest=None' in filter:
      filter = filter.replace('isTest=None', 'instanceType=cc')

  handlers = {
    'instanceType': lambda x: 'dev' if x == 'cc' else x
  }

  resp = util.cli_request('GET',
    util.build_url('{app}/auth/v1/company/child-companies?{filter}', {'filter': filter}))

  if json_flag:
    click.echo(json.dumps(resp))
    return

  util.print_table(resp['payload']['data'], format, handlers=handlers)

@click.command()
@click.option('--name', prompt=True)
@click.option('--type', default='studio', type=click.Choice(['studio', 'dev']), prompt=True)
@click.option('--format', '-f', default='{id} {name} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json', 'json_flag', is_flag=True, help='Return raw json from the platform.')
def provision(name, type, format, json_flag):
  if type == 'dev':
    type = 'cc'

  resp = check_response(requests.get(build_url('{app}/auth/v1/context'), headers=get_headers(), verify=verify_tls)).json()

  domain_prefix = name.replace(' ', '-').lower()

  data = {
    'name': name,
    'domainPrefix': domain_prefix,
    'experienceCloudId': 1,
    'authRealmId': 1,
    'instanceType': type
  }

  resp = check_response(requests.post(build_url('{app}/auth/v1/admin/companies'), json=data, headers=get_headers(), verify=verify_tls))

  if json_flag:
    click.echo(resp.text)
    return

  print_table([resp.json()['payload']['data']], format)

organization.add_command(list)
organization.add_command(child_companies)

# To Do: Finish this
#organization.add_command(provision)
