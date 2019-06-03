# -*- coding: utf-8 -*-

import os
import sys
from json import dumps
from urllib.error import URLError

import click

from requests import Session

from . import cli
from .storage import cache
from .environment import SS_GRAPHQL

requests = Session()


def graphql(query, **variables):
    try:
        res = requests.post(
            SS_GRAPHQL,
            data=dumps({'query': query, 'variables': variables}),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {cli.get_access_token()}',
            },
            timeout=10,
        )
    except KeyboardInterrupt:  # OK - user cancelled.
        click.echo('\nCancelled')
        sys.exit(1)
    except (URLError, ConnectionError, requests.exceptions.ConnectionError):
        click.echo(
            click.style(f'\nFailed to connect to {SS_GRAPHQL}', fg='red'),
            err=True,
        )
        sys.exit(1)

    data = res.json()
    if 'errors' in data:
        click.echo()
        for error in data['errors']:
            click.echo(
                click.style('Error: ', fg='red') + error['message'], err=True
            )
        sys.exit(1)
    return data


class Config:
    @staticmethod
    def get(app: str):
        res = graphql(
            """
            query($app: UUID!){
              allReleases(condition: {appUuid: $app},
                          first: 1, orderBy: ID_DESC){
                nodes{
                  config
                }
              }
            }
            """,
            app=Apps.get_uuid_from_hostname(app),
        )
        try:
            return res['data']['allReleases']['nodes'][0]['config'] or {}
        except:
            return {}

    @staticmethod
    def set(config: {}, app: str, message: str) -> dict:
        return Releases.create(
            config, None, app, message or 'Update environment'
        )


class Releases:
    @staticmethod
    def list(app: str, limit: int):
        res = graphql(
            """
            query($app: UUID!){
              allReleases(condition: {appUuid: $app},
                        first: 30, orderBy: ID_DESC){
                nodes{
                  id
                  message
                  timestamp
                  state
                }
              }
            }
            """,
            app=Apps.get_uuid_from_hostname(app),
        )
        try:
            return res['data']['allReleases']['nodes']
        except:
            return []

    @staticmethod
    def rollback(version: str, app: str):
        app_uuid = Apps.get_uuid_from_hostname(app)
        res = graphql(
            """
            query($app: UUID!, $version: Int!){
              releaseByAppUuidAndId( appUuid: $app, id: $version){
                config
                payload
              }
            }
            """,
            app=app_uuid,
            version=version,
        )
        release = res['data']['releaseByAppUuidAndId']

        return Releases.create(
            release['config'] or {},
            release['payload'],
            app,
            f'Rollback to v{version}',
        )

    @staticmethod
    def get(app: str):
        res = graphql(
            """
            query($app: UUID!){
              allReleases(condition: {appUuid: $app},
                          first: 1, orderBy: ID_DESC){
                nodes{
                  id
                  state
                }
              }
            }
            """,
            app=Apps.get_uuid_from_hostname(app),
        )
        try:
            return res['data']['allReleases']['nodes']
        except:
            return []

    @staticmethod
    def create(config: {}, payload: {}, app: str, message: str) -> dict:
        res = graphql(
            """
            mutation ($data: CreateReleaseInput!){
              createRelease(input: $data) {
                release { id }
              }
            }
            """,
            data={
                'release': {
                    'appUuid': Apps.get_uuid_from_hostname(app),
                    'message': message or 'Deploy app',
                    'config': config,
                    'payload': payload,
                }
            },
        )

        release_ = res['data']['createRelease']['release']

        changes = 'Code'
        if payload is None:
            changes = 'Config'

        cli.track(
            'App Release Created',
            {'Version': release_['id'], 'App name': app, 'Changes': changes},
        )

        return release_


class Apps:
    _hostname_to_uuid = {}

    @staticmethod
    def get_uuid_from_hostname(app: str) -> str:
        """
        This method also caches all queries made, but only during the current
        CLI session.
        """
        cache_key = f'app-{app}'
        the_uuid = None

        if cache_key in cache:
            the_uuid = cache.fetch(cache_key)

        if not the_uuid:
            the_uuid = Apps._hostname_to_uuid.get(app)

        # Cache the app's UUID.
        if cache_key not in cache:
            cache.store(cache_key, the_uuid)

        res = graphql(
            """
            query($app: Hostname!){
              app: appDnsByHostname(hostname: $app){
                appUuid
              }
            }
            """,
            app=app,
        )
        if res['data']['app'] is None:
            click.echo()
            click.echo(
                click.style(
                    f'The app "{app}" doesn\'t seem to exist.\n'
                    f'Are you sure you have access to it?',
                    fg='red',
                ),
                err=True,
            )
            sys.exit(1)

        app_uuid = res['data']['app']['appUuid']
        Apps._hostname_to_uuid[app] = app_uuid

        return app_uuid

    @staticmethod
    def maintenance(app: str, maintenance: bool):
        if maintenance is None:
            res = graphql(
                """
                query($app: UUID!){
                  app: appByUuid(uuid: $app){
                    maintenance
                  }
                }
                """,
                app=Apps.get_uuid_from_hostname(app),
            )
            return res['data']['app']['maintenance']
        else:
            graphql(
                """
                mutation ($data: UpdateAppByUuidInput!){
                  updateAppByUuid(input: $data){
                    app{
                      uuid
                    }
                  }
                }
                """,
                data={
                    'uuid': Apps.get_uuid_from_hostname(app),
                    'appPatch': {'maintenance': maintenance},
                },
            )

    @staticmethod
    def list() -> list:
        res = graphql(
            """
            query{
              allApps(condition: {deleted: false}, orderBy: NAME_ASC){
                nodes{
                  name
                  timestamp
                  maintenance
                }
              }
            }
            """
        )
        return res['data']['allApps']['nodes']

    @staticmethod
    def create(name: str, team: str) -> dict:
        res = graphql(
            """
            mutation ($data: CreateAppInput!){
              createApp(input: $data) {
                app{
                  name
                }
              }
            }
            """,
            data={'app': {'ownerUuid': cli.get_user_id(), 'name': name}},
        )
        return res['data']['createApp']['app']

    @staticmethod
    def destroy(app: str):
        graphql(
            """
            mutation ($data: UpdateAppByUuidInput!){
              updateAppByUuid(input: $data){
                app{
                  uuid
                }
              }
            }
            """,
            data={
                'uuid': Apps.get_uuid_from_hostname(app),
                'appPatch': {'deleted': True},
            },
        )
