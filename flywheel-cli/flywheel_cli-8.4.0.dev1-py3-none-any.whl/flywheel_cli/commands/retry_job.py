import flywheel
import logging
import os
import pytz
import re
import subprocess
import sys
import tempfile

from ..sdk_impl import create_flywheel_client
from .. import util

ACTION_RE = re.compile(r'^(ignore|retry|r|i)\s+[-:0-9\s]+\s+([a-f0-9]{24})')
COL_FORMAT = '{:<8}  {:<19}  {:<24}  {:<24}  {:<24}  {}'
HEADER_FORMAT = '# {:<6}  {:<19}  {:<24}  {:<24}  {:<24}  {}'

log = logging.getLogger(__name__)

def add_command(subparsers, parents):
    parser = subparsers.add_parser('retry', parents=parents, help='Retry one or more jobs matching the given IDs or filters')
    parser.add_argument('--file', help='A file containing ids of jobs to retry, one per line')

    parser.add_argument('job_id', nargs='?', action='append', help='One or more job id to reschedule')

    parser.add_argument('--ignore-state', action='store_true', help='Ignore state (allow restart of any job that is failed, canceled or complete)')

    parser.add_argument('--since', type=util.parse_datetime_argument, help='Filter jobs created after the given date / time')
    parser.add_argument('--gear-name', help='Filter jobs based on gear name (not label)')
    parser.add_argument('--gear-version', help='Filter jobs on gear version')
    parser.add_argument('--origin', help='Filter jobs based on who scheduled them (by user email or self for your own jobs)')
    parser.add_argument('--filter', help='Add additional arbitrary filters (comma separated)')
    parser.add_argument('--limit', default='1000', help='Limit the number of returned jobs')

    parser.set_defaults(func=retry_jobs)
    parser.set_defaults(parser=parser)

    return parser

def retry_jobs(args):
    fw = create_flywheel_client()

    # Combine job ids from args and file
    job_ids = util.args_to_list(args.job_id)
    if args.file:
        with open(args.file, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    job_ids.append(line)

    job_ids = set(job_ids)
    if job_ids:
        # Prompt if more than 1 job is selected
        msg = 'Do you really want to restart {} jobs?'.format(len(job_ids))
        if len(job_ids) == 1 or (args.config.assume_yes or util.confirmation_prompt(msg)):
            retry_job_ids(fw, job_ids, args)
    else:
        find_and_retry_jobs(fw, args)

def find_and_retry_jobs(fw, args):
    """Find and retry jobs based on command line arguments"""
    # Create filter query parameter
    job_filter = []
    if args.since:
        since = args.since.astimezone(pytz.UTC).strftime('%Y-%m-%dT%H:%M:%S')
        job_filter.append('created>={}'.format(since))
    if args.gear_name:
        job_filter.append('gear_info.name="{}"'.format(args.gear_name))
    if args.gear_version:
        job_filter.append('gear_info.version="{}"'.format(args.gear_version))
    if args.origin:
        if args.origin == 'self':
            self = fw.get_current_user()
            origin = self.id
            log.debug('origin (self) is: %s', origin)
        else:
            origin = args.origin
        job_filter.append('origin.id="{}"'.format(origin))

    if args.filter:
        job_filter.append(args.filter)

    if not job_filter:
        args.parser.error('Please specify job id(s) or a filter!')

    # Built-in filters
    if args.ignore_state:
        job_filter.append('state=~(failed|cancelled|complete)')
    else:
        job_filter.append('state=failed')

    job_filter.append('retried=null')

    job_filter = ','.join(job_filter)
    log.debug('Finding jobs to retry with filter: %s', job_filter)

    print('Querying jobs...')
    try:
        all_jobs = fw.get_all_jobs(filter=job_filter, sort='created:desc', limit=args.limit)
    except flywheel.ApiException as e:
        log.exception('Error retrieving list of jobs')
        sys.exit(1)

    log.debug('Found %d matching jobs', len(all_jobs))

    if not all_jobs:
        log.error('No jobs found matching that criteria!')
        sys.exit(0)

    # Get a list of valid ids
    valid_ids = { job.id for job in all_jobs }

    fd, path = tempfile.mkstemp('job-actions')
    with os.fdopen(fd, 'w') as f:
        print('# Determine action to take for failed jobs. Either retry or ignore.', file=f)
        print(HEADER_FORMAT.format('action', 'created', 'job id', 'gear name', 'gear version', 'state'), file=f)
        print('', file=f)

        for job in all_jobs:
            if job.gear_info:
                gear_name = job.gear_info.name
                gear_version = job.gear_info.version
            else:
                gear_name = 'UNKNOWN'
                gear_version = 'UNKNOWN'

            timestamp = str(job.created)[:19]
            print(COL_FORMAT.format('ignore', timestamp, job.id, gear_name, gear_version, job.state), file=f)

    # Allow user to edit actions
    util.edit_file(path)

    retry_ids = []
    with open(path, 'r') as f:
        for line in f.readlines():
            m = ACTION_RE.search(line)
            if m is not None:
                action = m.group(1)
                job_id = m.group(2)
                if action == 'retry' or action == 'r':
                    if job_id in valid_ids:
                        retry_ids.append(job_id)
                    else:
                        log.error('Invalid job id: %s', job_id)

    log.debug('%d jobs selected to retry', len(retry_ids))
    if retry_ids:
        retry_job_ids(fw, retry_ids, args)

def retry_job_ids(fw, ids, args):
    """Retry jobs in id list"""
    query_params = {}
    if args.ignore_state:
        query_params['ignore_state'] = True

    for job_id in ids:
        try:
            new_job_id = fw.retry_job(job_id, **query_params)['_id']
            log.info('Restarted job %s as %s', job_id, new_job_id)
        except flywheel.ApiException as e:
            log.exception('Unable to restart job %s', job_id)

