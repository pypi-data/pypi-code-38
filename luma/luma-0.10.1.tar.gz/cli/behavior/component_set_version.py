"""
    This behavior file contains the logic for a subset of commands. Logic specific to
    commands should be implamented in corresponding behavior files.
"""

from pathlib import Path
from cli import pyke
import requests
import click
import time
import json
import sys
import os

class ComponentSetVersionBehavior:
    def __init__(self, profile=None, component_set=None, format=None, filter=None, page=None, pagesize=None, json=False):
        self.util = pyke.Util(profile=profile)
        if profile is not None:
            self.context = pyke.auth.load_cache()
        self.object_type = 'component-set'
        self.json = json
        self.profile = profile
        self.component_set = component_set
        self.format = format
        self.filter = filter
        self.page = page
        self.pagesize = pagesize

    def list(self, component_set):
      component_set_id = self.util.lookup_object_id(self.object_type, component_set)

      click.echo(component_set_id)
      data = {'filter': self.filter, 'page': self.page, 'pagesize': self.pagesize}

      titles = {
          'directIncludes': '# Inc',
          'directCssIncludes': '# Css Inc',
          'expand__experiences': '# Exp',
          'expand__components': '# Comp',
      }

      handlers = {
          'directIncludes': lambda x: str(len(x)),
          'directCssIncludes': lambda x: str(len(x)),
          'expand__experiences': lambda x: str(len(x)),
          'expand__components': lambda x: str(len(x))
      }

      resp = self.util.cli_request('GET',
          self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions?expand=experiences&page={page}&pagesize={pagesize}&{filter}',
          {'component_set_id': component_set_id, **data}))

      if not self.json:
        self.util.print_table(resp['payload']['data'], self.format, titles=titles, handlers=handlers)
        self.util.print_record_count(resp)
      else:
        click.echo(json.dumps(resp))

    def list_components(self, component_set, version):
        component_set_id = self.util.lookup_object_id(self.object_type, component_set)
        version_id = self.util.get_version_id(self.object_type, component_set_id, version)

        resp = self.util.cli_request('GET',
            self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions/{version_id}?expand=components',\
            {'component_set_id': component_set_id, 'version_id': version_id}))

        click.echo(json.dumps(resp))

    def create(self, component_set, component_set_file_path, from_version, version_number,
        version_bump, css_includes, direct_includes, label):
        component_set_id = self.util.lookup_object_id(self.object_type, component_set)

        if from_version != '' and from_version is not None:
            try:
                from_version_id = int(from_version)
                version = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions/{from_version_id}',\
                    {'component_set_id': component_set_id, 'from_version_id': from_version_id} ))['payload']['data']
            except:
                version = self.util.get_version(self.object_type, component_set_id, from_version)

            if version is None:
                raise click.BadParameter(click.style("Component Set version not found", fg='red'), param_hint="--version-number")

            version[version_bump] = version[version_bump] + 1
            if version_bump in ['major', 'minor']:
                version['patch'] = 0
            if version_bump == 'major':
                version['minor'] = 0

        else:
            version = {}
            if label is None or label == '':
                label = input("Label: ")
                if label is None or label == '':
                    raise click.BadParameter(click.style("If you don't create from an old version then you must provide a --label", fg='red'), param_hint="--label")

            if version_number is None or version_number == '':
                version_number = input("Version Number: ")
                if version_number is None or version_number == '':
                    raise click.BadParameter(click.style("If you don't create from an old version then you must provide a --version-number in the format\
                        '<major: int>.<minor: int>.<patch: int>' ", fg='red'), param_hint="--version-number")

            major, minor, patch = self.util.parse_version_number(version_number)

            version['major'] = major
            version['minor'] = minor
            version['patch'] = patch

        if not self.json:
            click.echo('Image Size: {}'.format(self.util.get_size(component_set_file_path, image=False)))
            click.echo("Uploading Component Set Version to Lumavate")

        version['ephemeralKey'] = self.util.upload_ephemeral(component_set_file_path, 'application/zip')

        if label != '' and label is not None:
            version['label'] = label

        if css_includes:
            if 'directCssIncludes' not in version.keys():
                version['directCssIncludes'] = [x for x in css_includes]
            else:
                version['directCssIncludes'].extend([x for x in css_includes])

        if direct_includes:
            if 'directIncludes' not in version.keys():
                version['directIncludes'] = [x for x in direct_includes]
            else:
                version['directIncludes'].extend([x for x in direct_includes])

        resp = self.util.cli_request('POST',
            self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions',
            {'component_set_id': component_set_id}), data=json.dumps(version))

        if self.json:
            click.echo(json.dumps(resp))
            return

        handlers = {
          'directIncludes': lambda x: str(len(x)),
          'directCssIncludes': lambda x: str(len(x))
        }

        self.util.print_table([resp['payload']['data']], self.format, handlers=handlers)

    def update(self, component_set, version, label):
        component_set_id = self.util.lookup_object_id(self.object_type, component_set)
        version_id = self.util.get_version_id(self.object_type, component_set_id, version)

        post_data = {
          'componentSetId': component_set_id,
          'id': version_id,
          'label': label
        }

        resp = self.util.cli_request('PUT',
          self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions/{version_id}',
          {'component_set_id': component_set_id, 'version_id': version_id}), data=json.dumps(post_data))

        if self.json:
            click.echo(json.dumps(resp))
            return

        handlers = {
          'directIncludes': lambda x: str(len(x)),
          'directCssIncludes': lambda x: str(len(x))
        }

        self.util.print_table([resp['payload']['data']], self.format, handlers=handlers)

    def delete(self, component_set, version, version_mask):
        component_set_id = self.util.lookup_object_id(self.object_type, component_set)

        if version is None and version_mask is None:
            version = str(input("Version: "))
            if version is None or version == '':
                raise click.BadParameter(click.style('You must provide either a --version or a --version-mask', fg='red'))

        if version is not None:
            version_id = self.util.get_version_id(self.object_type, component_set_id, version)

            resp = self.util.cli_request('DELETE',
              self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions/{version_id}',
                {'component_set_id': component_set_id, 'version_id': version_id}))

            if self.json:
                click.echo(json.dumps(resp))
                return

            handlers = {
              'directIncludes': lambda x: str(len(x)),
              'directCssIncludes': lambda x: str(len(x))
            }

            self.util.print_table([resp['payload']['data']], self.format, handlers=handlers)

        else:
            versions = self.util.get_versions_from_mask(self.object_type, component_set_id, version_mask)
            if self.json:
                resp_list = {}
                resp_list['responses'] = []
                for v in versions:
                    resp = self.util.cli_request('DELETE',
                        self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions/{version_id}', {'component_set_id': component_set_id, 'version_id': v['id']}))
                    resp_list['responses'].append(resp)
                click.echo(json.dumps(resp_list))
                return

            with click.progressbar(versions, label='Deleting Versions') as bar:
                for v in bar:
                    resp = self.util.cli_request('DELETE',
                        self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/versions/{version_id}', {'component_set_id': component_set_id, 'version_id': v['id']}))

            handlers = {
                  'directIncludes': lambda x: str(len(x)),
                  'directCssIncludes': lambda x: str(len(x))
            }

            self.util.print_table(versions, self.format, handlers=handlers)
