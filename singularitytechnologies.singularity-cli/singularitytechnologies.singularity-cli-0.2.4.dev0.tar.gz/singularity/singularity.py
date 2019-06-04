"""
singularity-cli
Usage:
  singularity-cli ping [--api-url=<api_url>]
  singularity-cli batch create --from-file=<from_file> --cpus=<cpus> --mode=<mode> [--api-key=<api_key> --secret=<secret> --gpus=<gpus> --api-url=<api_url>]
  singularity-cli (job|batch) status <uuid> [--api-key=<api_key> --secret=<secret> --api-url=<api_url>]
  singularity-cli (job|batch) cancel <uuid> [--api-key=<api_key> --secret=<secret> --api-url=<api_url>]
  singularity-cli batch summary [--api-key=<api_key> --secret=<secret> --api-url=<api_url> --since=<since>]
  singularity-cli dataset add <name> <location> --pilot-count=<pilot_count> [--api-key=<api_key> --secret=<secret> --api-url=<api_url>]
  singularity-cli dataset summary <name> [--api-key=<api_key> --secret=<secret> --api-url=<api_url>]
  singularity-cli model download <batch_uuid> <job_uuid> --download-path=<download_path> [--api-key=<api_key> --secret=<secret> --api-url=<api_url>]
  singularity-cli -h | --help
  singularity-cli --version

Options:
  --cpus=<cpus>                    Number of CPUs required for each job (can be fractional)
  --gpus=<gpus>                    Number of GPUs required for each job
  --from-file=<from_file>    Path to a json file listing ML experiments you wish to run
  --mode=<mode>                    Mode of operation (pilot|production)
  --api-url=<api_url>              URL to send requests to [default: https://api.singularity-technologies.io]

  -h --help                        Show this screen.
  --version                        Show version.
"""

import json
import os
import sys
import traceback

from docopt import docopt

from . import __version__ as VERSION

from singularitytechnologiesapi import BatchCreate
from singularitytechnologiesapi import BatchStatus
from singularitytechnologiesapi import BatchSummary
from singularitytechnologiesapi import Cancel
from singularitytechnologiesapi import JobStatus
from singularitytechnologiesapi import DataSetAdd
from singularitytechnologiesapi import DataSetSummary
from singularitytechnologiesapi import ModelDownload
from singularitytechnologiesapi import Ping
from singularitytechnologiesapi import ShardAdd

from singularity.data import Sharder


def __load_config():
    home = os.environ.get('HOME')
    default_path = os.path.join(home, '.singularity')

    # Attempt to get path override
    config_path = os.environ.get('SINGULARITY_CONFIG_PATH', default_path)
    config_file = os.path.join(config_path, 'config.json')

    if not os.path.exists(config_file):
        print('No config file detected at: "%s"' % config_file)
        return {}

    config = {}
    with open(config_file, 'r') as f:
        try:
            config = json.load(f)

        except ValueError as e:
            raise SystemExit(
                'Config file "%s" is not valid json: %s' % (config_file, e)
            )

    return config


def __run_cmd(cmd):
    try:
        payload, _ = cmd.run()
    except Exception as e:
        print(traceback.format_exc())
        raise SystemExit('\nCommand error, please report bug: %s\n' % e)

    cmd.summary()

    # TODO(Sam): Add Status code checks
    return payload


def __data_set_add(options):
    payload = __run_cmd(DataSetAdd(options))
    data_set_uuid = payload.get('data_set_uuid')
    if not data_set_uuid:
        raise SystemExit('data_set_uuid not found in response')

    location = options.get('location')
    sharder = Sharder(location)
    for shard_id, shard in sharder.get_new_shards():
        shard_options = {
            'shard': shard,
            'shard_id': shard_id,
            'data_set_uuid': data_set_uuid
        }

        shard_options.update(options)

        __run_cmd(ShardAdd(shard_options))


def __model_download(options):
        model = __run_cmd(ModelDownload(options))
        if model:
            download_path = options.get('download_path')
            with open(download_path, 'wb') as f:
                f.write(model)


def main():
    config = __load_config()
    options = docopt(__doc__, version=VERSION)

    options['--api-key'] = options['--api-key'] or config.pop('api_key', '')
    options['--secret'] = options['--secret'] or config.pop('secret', '')

    if not options.get('--api-key'):
        raise SystemExit('API Key not set in either arguents or config file')

    if not options.get('--secret'):
        raise SystemExit('Secret not set in either arguents or config file')

    new_options = {}
    for key, value in options.items():
        key = key.replace('--', '')
        key = key.replace('-', '_')
        key = key.replace('<', '')
        key = key.replace('>', '')

        new_options[key] = value

    options = new_options

    if options.get('ping'):
        __run_cmd(Ping(options))

    elif options.get('batch') and options.get('create'):
        with open(options.get('from_file', 'r')) as f:
            options['payload'] = json.load(f)

        __run_cmd(BatchCreate(options))

    elif options.get('batch') and options.get('status'):
        __run_cmd(BatchStatus(options))

    elif options.get('batch') and options.get('summary'):
        __run_cmd(BatchSummary(options))

    elif options.get('job') and options.get('status'):
        __run_cmd(JobStatus(options))

    elif options.get('job') and options.get('cancel'):
        __run_cmd(Cancel(options, 'job'))

    elif options.get('batch') and options.get('cancel'):
        __run_cmd(Cancel(options, 'batch'))

    elif options.get('dataset') and options.get('add'):
        __data_set_add(options)

    elif options.get('dataset') and options.get('summary'):
        __run_cmd(DataSetSummary(options))

    elif options.get('model') and options.get('download'):
        __model_download(options)

    else:
        print('Unknown option')
        sys.exit(1)
