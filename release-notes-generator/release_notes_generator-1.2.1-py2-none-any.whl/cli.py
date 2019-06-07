#!/usr/bin/env python

import os
import click

from release_notes_generator.release_note_generator import ReleaseNoteGenerator
from release_notes_generator import services


@click.group()
def release_notes():
    pass


@release_notes.command()
@click.option(
    '--source',
    type=click.File('r'),
    help='A file that contains a pull request number per line.'
)
@click.argument(
    'project',
    default='wet_arms',
    required=False,
)
def getfor(source, project):
    ''' This fetches the latest release for the given project, parses out an
    expected list of PR numbers, then fetches and parses each of their PR
    descriptions.

    It takes those descriptions and does some minor formatting before
    concatenating them together.

    <project> can be one of:\n\n\twet_arms\n\n\tauto_pipeline\n\n\twetlab-ops'''

    token = os.getenv('GITHUB_API_TOKEN')

    if not token:
        print('ERROR: GITHUB_API_TOKEN must be set in the environment.')
    else:
        if source:
            print('Fetching notes from sourcefile pull requests.')
            pr_nums = source.read().splitlines()
        else:
            pr_nums = services.ReleasePRNumbersFetcher(
                token,
                repository_name=project).pull_request_numbers()

        notes = ReleaseNoteGenerator(
            token,
            pr_nums,
            repository_name=project).release_notes()

        services.ReleaseNotesFormatter.output(notes)
