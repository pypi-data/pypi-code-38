#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import os
from csv import DictReader
from reader import UserDictReader
from lib import Client

def validate_secret(ctx, param, value):
    if not value:
        raise click.BadParameter('The parameter API secret is not defined')
    return str(value)

def validate_source(ctx, param, value):
    if not value:
        raise click.BadParameter('The parameter source is not defined')
    return value

def validate_destination(ctx, param, value):
    if not value:
        raise click.BadParameter('The parameter source is not defined')
    return value

@click.command()
@click.option('--api-secret', help='The profile sync API secret. [envvar=API_SECRET]', envvar='API_SECRET', callback=validate_secret)
@click.option('--source', help='The source file (formatted as CSV).', type=click.STRING, callback=validate_source)
@click.option('--destination', help='The Pleio subsite providing the profile sync.', callback=validate_destination)
@click.option('--ban', help='Ban users on the site who are not listed in the CSV file. [default=False]', type=click.BOOL, default=False)
@click.option('--dry-run', help='Perform a dry run. [default=False]', type=click.BOOL, default=False)
@click.option('--verbose', help='Show verbose output [default=False]', type=click.BOOL, default=False)
def main(api_secret, source, destination, ban, dry_run, verbose):
    with open(source) as file_source:
        csv_source = UserDictReader(file_source)
        rest_destination = Client(base_url=destination, api_secret=api_secret, read_only=dry_run, verbose=verbose)

        on_source = { 'email': set() }
        on_destination = { 'email': set() }

        print('Retrieving list of source users')
        for user in csv_source:
            on_source['email'].add(user['email'])

        print('Retrieving list of destination users')
        for user in rest_destination.get_users():
            if not user['is_banned']:
                on_destination['email'].add(user['email'])

        to_add = on_source['email'].difference(on_destination['email'])
        to_update = on_source['email'].intersection(on_destination['email'])
        to_ban = on_destination['email'].difference(on_source['email'])

    with open(source) as file_source:
        csv_source = UserDictReader(file_source)

        for user in csv_source:
            if user['email'] in to_add:
                print('Adding {}'.format(user['email']))
            if user['email'] in to_update:
                print('Updating {}'.format(user['email']))

            result = rest_destination.post_user(user)

            if user['avatar']:
                with open(os.path.join(os.path.dirname(source), user['avatar']), 'rb') as avatar:
                    rest_destination.post_avatar(result['user']['guid'], avatar)

        if ban:
            for user in rest_destination.get_users():
                if user['email'] in to_ban:
                    print('Banning {}'.format(user['email']))
                    result = rest_destination.ban_user(user['guid'])

if __name__ == '__main__':
    main()
