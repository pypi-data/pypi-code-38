"""
    This behavior file contains the logic for a subset of commands. Logic specific to
    commands should be implamented in corresponding behavior files.
"""

from ast import literal_eval
from pathlib import Path
from cli import pyke, behavior
import click
import time
import json
import sys
import os

class MicroserviceVersionBehavior:
    def __init__(self, profile=None, microservice=None, format=None, filter=None, page=None, pagesize=None, json=False):
        self.util = pyke.Util(profile=profile)
        self.object_type = 'microservice'
        self.json = json
        self.profile = profile
        self.microservice = microservice
        self.format = format
        self.filter = filter
        self.page = page
        self.pagesize = pagesize

    def list(self, microservice):
        microservice_id = self.util.lookup_object_id(self.object_type, microservice)
        data = {'filter': self.filter, 'page': self.page, 'pagesize': self.pagesize}

        handlers = {
          'actualState': lambda x: click.style(x, fg='red') if x not in ['running'] else click.style(x, fg='green')
        }

        resp = self.util.cli_request('GET',
            self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions?page={page}&pagesize={pagesize}&{filter}',
            {'microservice_id': microservice_id, **data}))

        if self.json:
            click.echo(json.dumps(resp))
            return

        self.util.print_table(resp['payload']['data'], self.format, handlers=handlers)
        self.util.print_record_count(resp)

    def start_stop(self, action, microservice, version):
        microservice_id = self.util.lookup_object_id(self.object_type, microservice)
        version_data = None

        try:
            version_id = int(version)
        except:
            major, minor, patch = self.util.parse_version_number(version)

            version_data = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions?major={major}&minor={minor}&patch={patch}',\
                { 'microservice_id': microservice_id, 'major': major, 'minor': minor, 'patch': patch }))['payload']['data']

            if version_data is None or len(version_data) < 1:
                raise click.ClickException(click.style("Version not found", fg='red'))
            else:
                version_id = version_data[0].get('id')
                current_state = version_data[0].get('actualState')

        if version_data is None:
            version_data = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}',\
                {'microservice_id': microservice_id, 'version_id': version_id} ))['payload']['data']

            if version_data is None or len(version_data) < 1:
                raise click.ClickException(click.style("Version not found", fg='red'))

            current_state = version_data.get('actualState')

        if current_state not in ['stopped', 'running', 'error']:
            raise click.ClickException(click.style("To start or stop a version it must have a 'stopped', 'running' or 'error' state. The current state of this version is {}. \
                A version goes through several states after being uploaded to Lumavate. It must finish this process before this command can be run. \
                To check its current state, run 'luma microservice-version ls'.".format(current_state), fg='yellow'))

        if action == 'stop' and current_state != 'running':
            raise click.ClickException(click.style("This version is not running", fg='yellow'))
        if action == 'start' and current_state == 'running':
            raise click.ClickException(click.style("This version is already running", fg='yellow'))

        titles = {
            'id': 'id',
            'actualState': 'Current State',
            'versionNumber': 'Version #',
            'createdAt': 'Created At',
            'createdBy': 'Created By'
        }

        data = {
            "action": action,
            "containerId": microservice_id,
            "id": version_id
        }

        resp = self.util.cli_request('POST', self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}/{action}',\
            {'microservice_id': microservice_id, 'version_id': version_id, 'action': action}), data=data)

        if self.json:
            click.echo(json.dumps(resp))
            return

        status_id = resp['payload']['data']['results']['statusId']
        progress = 0
        error = None
        if action == 'start':
            bar_name = "Starting microservice"
        else:
            bar_name = "Stopping microservice"

        with click.progressbar(length=100, label=bar_name) as bar:
            while progress < 100 and error is None:
                status_resp = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/statuses/{status_id}', {'status_id': status_id}))
                progress = status_resp['payload']['data']['overallPercent']
                error = status_resp['payload']['data']['errorMessage']
                bar.update(progress)

        click.echo(' ')
        ver_resp = self.util.cli_request('GET',
            self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}', {'microservice_id': microservice_id, 'version_id': version_id}))

        handlers = {
          'actualState': lambda x: click.style(x, fg='red') if x not in ['running'] else click.style(x, fg='green')
        }

        self.util.print_table([ver_resp['payload']['data']], self.format, handlers=handlers, titles=titles)

    def run(self, microservice, version, command):
        microservice_id = self.util.lookup_object_id(self.object_type, microservice)
        version_id = self.util.get_version_id(self.object_type, microservice_id, version)

        data = {
            "command": command
        }

        resp = self.util.cli_request('POST', self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}/exec',\
            {'microservice_id': microservice_id, 'version_id': version_id}), json=data)

        if self.json:
            click.echo(json.dumps(resp))
            return

        status_id = resp['payload']['data']['statusId']
        progress = 0
        error = None
        with click.progressbar(length=100, label='Executing command') as bar:
            while progress < 100:
                status_resp = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/statuses/{status_id}', {'status_id': status_id}))
                progress = status_resp['payload']['data']['overallPercent']
                bar.update(progress)
                if status_resp['payload']['data']['errorMessage'] is not None:
                    click.echo('There was an error running the command')
                    raise click.ClickException('Status: {}'.format(status_resp['payload']['data']))

        click.echo(' ')
        click.echo('Command Output: ')
        click.echo(' ')
        try:
            status_resp = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/statuses/{status_id}', {'status_id': status_id}))['payload']['data']
            summary = status_resp['summary']['results']
            if 'output' in summary[0].keys():
                if isinstance(summary[0]['output'], list):
                    for x in summary[0]['output']:
                        click.echo(x)
                else:
                    click.echo(summary)

        except:
            click.echo(status_resp)

    def logs(self, microservice, version):
        microservice_id = self.util.lookup_object_id(self.object_type, microservice)
        version_id = self.util.get_version_id(self.object_type, microservice_id, version)

        resp = self.util.cli_request('GET', self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}/logs',\
            {'microservice_id': microservice_id, 'version_id': version_id}))

        if self.json:
            click.echo(json.dumps(resp))
            return

        for x in resp['payload']['data']:
            click.echo(x)

    def update(self, microservice, version, label, format):
        microservice_id = self.util.lookup_object_id(self.object_type, microservice)
        version_id = self.util.get_version_id(self.object_type, microservice_id, version)

        post_data = {
          'microserviceId': microservice_id,
          'id': version_id,
          'label': label
        }

        resp = self.util.cli_request('PUT',\
          self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}',
          {'microservice_id': microservice_id, 'version_id': version_id}), data=json.dumps(post_data))

        if self.json:
            click.echo(json.dumps(resp))
            return

        self.util.print_table([resp['payload']['data']], format)

    def delete(self, microservice, version, version_mask, format):
        if version is None and version_mask is None:
            version = str(input("Version: "))
            if version is None or version == '':
                raise click.BadParameter(click.style('You must provide either a --version or a --version-mask', fg='red'))

        microservice_id = self.util.lookup_object_id(self.object_type, microservice)

        if version is not None:
            version_id = self.util.get_version_id(self.object_type, microservice_id, version)

            resp = self.util.cli_request('DELETE',\
              self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}', {'microservice_id': microservice_id, 'version_id': version_id}))

            if self.json:
                click.echo(json.dumps(resp))
                return

            self.util.print_table([resp['payload']['data']], format)

        else:
            versions = self.util.get_versions_from_mask(self.object_type, microservice_id, version_mask)

            if self.json:
                resp_list = {}
                resp_list['responses'] = []
                for v in versions:
                    resp = self.util.cli_request('DELETE',
                        self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}', {'microservice_id': microservice_id, 'version_id': v['id']}))
                    resp_list['responses'].append(resp)
                click.echo(json.dumps(resp_list))
                return

            with click.progressbar(versions, label='Deleting Versions') as bar:
                for v in bar:
                    resp = self.util.cli_request('DELETE',
                        self.util.build_url('{app}/iot/v1/containers/{microservice_id}/versions/{version_id}', {'microservice_id': microservice_id, 'version_id': v['id']}))

            self.util.print_table(versions, format)
