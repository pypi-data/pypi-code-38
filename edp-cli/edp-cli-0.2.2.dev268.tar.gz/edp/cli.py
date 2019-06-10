import click
import os
import glob
import re
import csv
import types
import sys
import datetime
import json
from girder_client import GirderClient
from edp.composite import _ingest_runs, _ingest_samples, _ingest_run_data
import importlib
from edp.deploy import deploy
import pytz
from pathlib import Path
from itertools import chain
import asyncio

from . import composite


class GC(GirderClient):

    def __init__(self, api_url=None, api_key=None):

        def _progress_bar(*args, **kwargs):
            bar = click.progressbar(*args, **kwargs)
            bar.bar_template = "[%(bar)s]  %(info)s  %(label)s"
            bar.show_percent = True
            bar.show_pos = True

            def formatSize(length):
                if length == 0:
                    return '%.2f' % length
                unit = ''
                # See https://en.wikipedia.org/wiki/Binary_prefix
                units = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
                while True:
                    if length <= 1024 or len(units) == 0:
                        break
                    unit = units.pop(0)
                    length /= 1024.
                return '%.2f%s' % (length, unit)

            def formatPos(_self):
                pos = formatSize(_self.pos)
                if _self.length_known:
                    pos += '/%s' % formatSize(_self.length)
                return pos

            bar.format_pos = types.MethodType(formatPos, bar)
            return bar

        _progress_bar.reportProgress = sys.stdout.isatty()

        super(GC, self).__init__(
            apiUrl=api_url, progressReporterCls=_progress_bar)

        self.authenticate(apiKey=api_key)

@click.group()
def cli():
    pass

def _generate_schedule_file_map(schedule_dir):
    schedule_map = {}
    for f in chain(glob.glob('%s/**/*.SDU' % schedule_dir), glob.glob('%s/**/*.sdu' % schedule_dir)):
        schedule_map[Path(f).name.lower()] = f

    return schedule_map

def _ingest_batch(gc, data_folder, project, cycle, dir, schedule_dir, public,
                  summary_func, timezone):
    timezone = pytz.timezone(timezone)

    # Loady summary function
    if summary_func is not None:
        try:
            module_name, func_name = summary_func.rsplit('.',1)
            module = importlib.import_module(module_name)
            summary_func = getattr(module, func_name)
        except:
            click.echo(click.style('Unable to load summary function: %s' % summary_func, fg='yellow'))
            raise

    batch_name = os.path.basename(dir)

    # See if we have a MatLab struct
    struct_file = glob.glob('%s/*.mat' % dir)
    if struct_file:
        click.echo(click.style('Uploading MatLab struct file', fg='red'))
        struct_file = gc.uploadFileToFolder(data_folder['_id'], struct_file[0])

    # Create the batch
    batch = {
        'startDate': '',
        'title': batch_name,
        'motivation': '',
        'experimentalDesign': '',
        'experimentalNotes': '',
        'dataNotes': '',
        'public': public
    }

    if struct_file:
        batch['structFileId'] = struct_file['_id']

    # Determine the batches url, depending on whether we have been given a cycle
    batches_url = 'edp/projects/%s' % project
    if cycle is not None:
        batches_url = '%s/cycles/%s/batches' % (batches_url, cycle)
    else:
        batches_url = '%s/batches' % batches_url

    batch = gc.post(batches_url, json=batch)

    click.echo(click.style('Batch created: %s' % batch['_id'], fg='red'))

    schedule_file_map = _generate_schedule_file_map(schedule_dir)
    metafile_regex =  re.compile(r'^(\d{4}-\d{2}-\d{2}_.*_CH(\d+))_Metadata.csv$')
    for meta_file in glob.glob('%s/*Metadata.csv' % dir):
        name = os.path.basename(meta_file)
        match = metafile_regex.match(name)
        if match is None:
            click.echo(click.style('%s does not have expected filename format, skipping.' % meta_file, fg='yellow'))
            continue

        test_name = match.group(1)
        channel = match.group(2)
        data_file_path = meta_file.replace('_Metadata.csv', '.csv')

        with open(meta_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            start_date = row['first_start_datetime']
            start_date = datetime.datetime.fromtimestamp(
                int(start_date), tz=timezone).strftime('%Y-%m-%d')
            cell_id = row['item_id']
            schedule_file = row['schedule_file_name']

        # Find the schedule file, there seems to be a mix of case!
        schedule_file = schedule_file.split('\\')[1]
        if schedule_file.lower() not in  schedule_file_map:
            click.echo(click.style('Unable to file schedule file: %s.' % schedule_file, fg='yellow'))
            schedule_file = None
        else:
            click.echo(click.style('Uploading schedule file', fg='blue'))
            schedule_file = gc.uploadFileToFolder(data_folder['_id'], schedule_file_map[schedule_file.lower()])

        click.echo(click.style('Uploading meta data file', fg='blue'))
        meta_file = gc.uploadFileToFolder(data_folder['_id'], meta_file)
        click.echo(click.style('Uploading data file', fg='blue'))
        data_file = gc.uploadFileToFolder(data_folder['_id'], data_file_path)

        if summary_func is not None:
            summary = summary_func(data_file_path)

        test = {
            'name': test_name,
            'startDate': start_date,
            'cellId': cell_id,
            'batteryType': '',
            'channel': channel,
            'metaDataFileId': meta_file['_id'],
            'dataFileId': data_file['_id'],
            'public': 'public',
            'summary': summary
        }

        if schedule_file is not None:
            test['scheduleFileId'] = schedule_file['_id']

        test = gc.post('%s/%s/tests' % (batches_url, batch['_id']), json=test)

        click.echo(click.style('Test created: %s' % test['_id'], fg='blue'))

@cli.command('ingest', help='Ingest data')
@click.option('-p', '--project', default=None, help='the project id', required=True)
@click.option('-c', '--cycle', default=None, help='the cycle id')
@click.option('-d', '--dir', help='path to batch(es) to ingest',
              type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True), default='.')
@click.option('-e', '--schedule_dir', help='path to the directory containing the schedule  to ingest',
              type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True), default='.')
@click.option('-u', '--api-url', default='http://localhost:8080/api/v1', help='RESTful API URL '
                   '(e.g https://girder.example.com/api/v1)')
@click.option('-k', '--api-key', envvar='GIRDER_API_KEY', default=None,
              help='[default: GIRDER_API_KEY env. variable]', required=True)
@click.option('-b', '--public', is_flag=True,
              help='Marked the data as public')
@click.option('-s', '--summary-func', default=None, help='Fully qualified name of function to summarize test data.')
@click.option('-z', '--timezone', default='UTC', help='The timezone (pyz format) for any timestamp conversion.')
def _ingest(project, cycle, api_url, api_key, dir, schedule_dir, public, summary_func, timezone):
    gc = GC(api_url=api_url, api_key=api_key)

    # Try to get edp data folder
    data_folder = gc.resourceLookup('/collection/edp/data', test=True)

    # Create a private folder
    if data_folder is None:

        me = gc.get('/user/me')
        user_folder = 'Public' if public else 'Private'
        try:
            user_folder = next(gc.listFolder(me['_id'], 'user', user_folder))
        except StopIteration:
            raise Exception('Unable to find user folder: %s' % user_folder)

        data_folder = gc.listFolder(user_folder['_id'], 'folder', name='edp')
        try:
            data_folder = next(data_folder)
        except StopIteration:
            data_folder = gc.createFolder(user_folder['_id'], 'edp', parentType='folder',
                                          public=public)

    dir  = os.path.abspath(dir)

    # See if the input directory contains directories then assume each of them is
    # a batch to ingest.
    batch_dirs = list(filter(os.path.isdir, [os.path.join(dir, d) for d in os.listdir(dir)]))
    if len(batch_dirs) == 0:
        batch_dirs = [dir]

    for batch_dir in batch_dirs:
        _ingest_batch(gc, data_folder, project, cycle, batch_dir, schedule_dir, public, summary_func, timezone)

@cli.command('ingest_composite', help='Ingest composite data')
@click.option('-p', '--project', default=None, help='the project id', required=True)
@click.option('-d', '--dir', help='base path to data to ingest',
              type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True), default='.')
@click.option('-u', '--api-url', default='http://localhost:8080/api/v1', help='RESTful API URL '
                   '(e.g https://girder.example.com/api/v1)')
@click.option('-k', '--api-key', envvar='GIRDER_API_KEY', default=None,
              help='[default: GIRDER_API_KEY env. variable]', required=True)
def _ingest_composite(project, dir, api_url, api_key):
    if dir[-1] != '/':
        dir += '/'

    asyncio.run(composite.ingest(project, dir, api_url, api_key))

@cli.command('deploy_static', help='Extract data from Girder and deploy static files to S3')
@click.option('-b', '--bucket', default=None, help='the S3 bucket to deploy to', required=True)
@click.option('-p', '--prefix', default='', help='the bucket prefix')
@click.option('-u', '--api-url', default='http://localhost:8080/api/v1',
              help='RESTful API URL for the instance we extracting from '
                   '(e.g https://girder.example.com/api/v1)')
def _deploy_static(bucket, prefix, api_url):
    deploy(api_url, 'edp/projects', ('batches', 'tests'), bucket, prefix)
