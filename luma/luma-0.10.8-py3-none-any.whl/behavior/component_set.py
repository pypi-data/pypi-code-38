"""
    This behavior file contains the logic for a subset of commands. Logic specific to
    commands should be implamented in corresponding behavior files.
"""

from pathlib import Path
from cli import pyke
import click
import time
import json
import sys
import os

class ComponentSetBehavior:
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


    def list(self):
        data = {'filter': self.filter, 'page': self.page, 'pagesize': self.pagesize}

        resp = self.util.cli_request('GET',
            self.util.build_url('{app}/iot/v1/component-sets?page={page}&pagesize={pagesize}&{filter}', {**data} ))

        if self.json:
            click.echo(json.dumps(resp))
            return

        self.util.print_table(resp['payload']['data'], self.format)
        self.util.print_record_count(resp)

    def delete(self, component_set):
        component_set_id = self.util.lookup_object_id(self.object_type, component_set)

        resp = self.util.cli_request('DELETE',
            self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}', {'component_set_id': component_set_id}))

        if self.json:
            click.echo(json.dumps(resp))
            return

        self.util.print_table([resp['payload']['data']], self.format)

    def create(self, name, url_ref, icon_file):
        if icon_file is None or icon_file == '':
            icon_file = self.util.resolve_default_icon_path()

        post_data = {
          'name': name,
          'urlRef': url_ref,
          'ephemeralKey': self.util.upload_ephemeral(icon_file, 'image/svg+xml')
        }

        resp = self.util.cli_request('POST', self.util.build_url('{app}/iot/v1/component-sets'), data=json.dumps(post_data))

        if self.json:
            click.echo(json.dumps(resp))
            return

        self.util.print_table([resp['payload']['data']], self.format)

    def update(self, component_set, name, icon_file):
        component_set_id = self.util.lookup_object_id(self.object_type, component_set)
        post_data = {}

        if len(name) > 1:
            post_data['name'] = name

        if len(icon_file) > 1:
            post_data['ephemeralKey'] = self.util.upload_ephemeral(icon_file, 'image/svg+xml')

        resp = self.util.cli_request('PUT',
          self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}', {'component_set_id': component_set_id}),
          data=json.dumps(post_data))

        if self.json:
            click.echo(json.dumps(resp))
            return

        self.util.print_table([resp['payload']['data']], self.format)

    def share(self, component_set, add, rm, absolute, current):
        component_set_id = self.util.lookup_object_id(self.object_type, component_set)

        if current:
            if self.json:
                resp = self.util.cli_request('GET',
                    self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/access',
                    {'component_set_id': component_set_id}))

                click.echo(resp)
                return
            else:
                resp = self.util.cli_request('GET',
                    self.util.build_url('{app}/auth/v1/company/child-companies'))['payload']['data']

                recs = self.util.get_current_access_records('component-set', component_set_id)
                org_names = [self.util.get_company_name(x.get('granteeCompanyId'), resp) for x in recs if x.get('granteeCompanyId') != int(self.util.context.get('orgId'))]
                click.echo(org_names)

                return

        resp = self.util.cli_request('GET',
            self.util.build_url('{app}/auth/v1/company/child-companies'))['payload']['data']

        handlers = {
          'sharedWith': lambda x: x.get('granteeId') if x is not None else '',
          'unsharedWith': lambda x: x.get('granteeId') if x is not None else ''
        }

        if absolute:
          absolute_ids = [self.util.get_company_id(x, resp) for x in absolute]
          data = {
            "id": component_set_id,
            "granteeCompanyIds": [x for x in absolute_ids]
          }

          access_resp = self.util.cli_request('PUT', self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/access',\
            {'component_set_id': component_set_id}), data=json.dumps(data))

          if self.json:
            click.echo(json.dumps(access_resp))
            return

          recs = self.util.get_current_access_records('component-set', component_set_id)
          access_resp['payload']['data']['resultingGrantees'] =\
            [self.util.get_company_name(x.get('granteeCompanyId'), resp) for x in recs if x.get('granteeCompanyId') != int(self.util.context.get('orgId'))]

          self.util.print_table([access_resp['payload']['data']], self.format)
          return

        recs = self.util.get_current_access_records('component-set', component_set_id)
        sharees = [x.get('granteeCompanyId') for x in recs if x.get('granteeCompanyId') != int(self.context.get('orgId'))]
        if add:
          add_ids = [self.util.get_company_id(x, resp) for x in add]
          sharees.extend(add_ids)

        if rm:
          rm_ids = [self.util.get_company_id(x, resp) for x in rm]
          sharees = [x for x in sharees if x not in rm_ids]

        data = {
          "id": component_set_id,
          "granteeCompanyIds": sharees
        }

        access_resp = self.util.cli_request('PUT',
            self.util.build_url('{app}/iot/v1/component-sets/{component_set_id}/access', {'component_set_id': component_set_id}), data=json.dumps(data))

        if self.json:
          click.echo(json.dumps(access_resp))
          return

        recs = self.util.get_current_access_records('component-set', component_set_id)

        access_resp['payload']['data']['resultingGrantees'] =\
          [self.util.get_company_name(x.get('granteeCompanyId'), resp) for x in recs if x.get('granteeCompanyId') != int(self.context.get('orgId'))]

        self.util.print_table([access_resp['payload']['data']], self.format)
