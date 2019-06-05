from datetime import datetime
from pathlib import Path
from cli import pyke
import subprocess
import platform
import click
import json
import os

verify_tls = os.environ.get('LUMA_CLI_VERIFY_TLS', None)
if verify_tls == 'false' or verify_tls == 'False':
  verify_tls = False
else:
  verify_tls = None

class ContainerVersionBehavior:
  def __init__(self, profile=None):
    self.util = pyke.Util(profile=profile)
    self.object_type = 'container'

  def force_update (self, container, version):
    container_id = self.util.lookup_object_id(self.object_type, container)
    version_id = self.util.get_version_id(self.object_type, container, version)

    req_data = {'force': True}
    resp = self.util.cli_request('PUT',
        self.util.build_url('{app}/iot/v1/containers/{container_id}/versions/{version_id}',
          {'container_id': container_id, 'version_id': version_id}), json=req_data)

    click.echo(resp)

  def create_editable_version(self, container_id, from_version, env, format):
    if from_version is None:
      raise click.ClickException(click.style("An editable version must come from an exsisting version", fg='red'))

    version = self.util.get_container_version(container_id, from_version)

    if not version.get('editorPort'):
      raise click.ClickException(click.style("An editable version must come from an exsisting version with an editor port", fg='red'))

    versions = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/containers/{container_id}/versions?major={major}&minor={minor}&sort=patch+desc',\
          { 'container_id': version['containerId'], 'major': version['major'], 'minor': version['minor'] }))['payload']['data']

    if versions is not None and len(versions) > 0:
      latest_version = versions[0]

    version['patch'] = latest_version['patch'] + 1
    version['isEditable'] = True
    version['label'] = 'dev'

    del version['versionNumber']

    if 'env' not in version.keys():
      version['env'] = {}

    for var in env:
      try:
        env_dict = json.loads(var)
        version['env'] = { **version['env'], **env_dict}
      except Exception as e:
        print("Could not serialize {}".format(var))
        print(e)

    resp = self.util.cli_request('POST', self.util.build_url('{app}/iot/v1/containers/{container_id}/versions',\
      {'container_id': container_id}), data=json.dumps(version))

    # TO DO: Add progress bar after create for loading/validating microservice
    status_id = None

    if 'results' in resp['payload']['data'].keys():
      status_id = resp['payload']['data']['results']['statusId']
    if status_id:
      status_resp = self.util.show_progress(status_id, label='Creating Editable Version')
      error_msg = status_resp.get('payload', {}).get('data', {}).get('errorMessage')
      if error_msg is not None:
        raise pyke.CliException('Create version failed. {}'.format(error_msg))

    handlers = {
        'actualState': lambda x: click.style(x, fg='red') if x not in ['running'] else click.style(x, fg='green')
    }

    click.echo(click.style("Using the --is-editable flag ignores all options other than --format and --env", fg='yellow'))
    click.echo(click.style("The editable version will increment the patch number to the first available", fg='yellow'))

    self.util.print_table([resp['payload']['data']], format, handlers=handlers)

  def download_app_zip(self, container, version, path):
    home = str(Path.home())
    if path is None:
      path = home
    else:
      path = '{}/{}'.format(home, path)

    container_id = self.util.lookup_object_id(self.object_type, container)

    try:
      container = self.util.cli_request('GET',
          self.util.build_url('{app}/iot/v1/containers?id={id}', {'id': container_id} ))['payload']['data']
    except:
      raise click.ClickException('Container not found')

    url_ref = container[0].get('urlRef')
    version_id = self.util.get_version_id(self.object_type, container_id, version)

    resp = self.util.cli_request('POST',
        self.util.build_url('{app}/iot/v1/containers/{container_id}/versions/{version_id}/token',
          {'container_id': container_id, 'version_id': version_id}), json={'type': 'editor'})

    token = resp.get('payload', {}).get('data', {}).get('token')

    service_url = self.util.context.get('experienceCloudUri')

    # TODO: Dynamically get integration cloud
    editor_url = '{}/ic/{}/luma-editor/download/application.zip'.format(service_url, url_ref)

    time = datetime.now().microsecond

    if platform.system() == 'Windows':
      zip_path = '{}\\application.{}.zip'.format(path, time)
    else:
      zip_path = '{}/application.{}.zip'.format(path, time)

    command_list = 'curl -L -f --create-dirs --output {} {} -H '.format(zip_path, editor_url).split()
    command_list.append("Authorization: Bearer {}".format(token))
    if verify_tls is False:
      command_list.extend(['--insecure', '--proxy-insecure'])

    subprocess.run(command_list)
    click.echo("File Location: {}".format(zip_path))

  def tail_logs(self, container, version, tail_number=None):
    container = self.util.get_container(container)
    container_id = container.get('id')

    version = self.util.get_container_version(container_id, version)
    version_id = version.get('id')

    url_ref = container.get('urlRef')

    editorPort = version.get('editorPort')
    if not editorPort:
      return self.old_logs(container_id, version_id)

    resp = self.util.cli_request('POST',
        self.util.build_url('{app}/iot/v1/containers/{container_id}/versions/{version_id}/token',
          {'container_id': container_id, 'version_id': version_id}), json={'type': 'editor'})

    token = resp.get('payload', {}).get('data', {}).get('token')
    service_url = self.util.context.get('experienceCloudUri')

    if not tail_number:
      tail_number = 100

    # TODO: Dynamically get integration cloud
    editor_url = '{}/ic/{}/luma-editor/logs?tail={}'.format(service_url, url_ref, tail_number)

    command_list = 'curl {} -H '.format(editor_url).split()
    command_list.append("Authorization: Bearer {}".format(token))
    if verify_tls is False:
      command_list.extend(['--insecure', '--proxy-insecure'])

    subprocess.run(command_list)

  def old_logs(self, container_id, version_id):
    resp = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/containers/{container_id}/versions/{version_id}/logs',\
      {'container_id': container_id, 'version_id': version_id}))

    for x in resp['payload']['data']:
      click.echo(x)


