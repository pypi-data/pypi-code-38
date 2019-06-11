import argparse
import logging
import os
import subprocess
import sys

import docker
from streamsets.sdk.config import USER_CONFIG_PATH
from streamsets.sdk.exceptions import ActivationError
from streamsets.sdk.sdc_api import ACTIVATION_FILE_NAME

from .. import logger as streamsets_logger
from ..__version__ import __version__

DOCKER_IMAGE_3_X = 'streamsets/testframework:3.x'
DOCKER_IMAGE_4_X = 'streamsets/testframework-4.x:latest'
DEFAULT_DOCKER_IMAGE = DOCKER_IMAGE_3_X
DEFAULT_DOCKER_NETWORK = 'cluster'

DEFAULT_TESTFRAMEWORK_CONFIG_DIRECTORY = os.path.expanduser('~/.streamsets/testframework')

DEFAULT_BUILD_NAME = 'latest'
DEFAULT_BUILD_S3_BUCKET = 'nightly.streamsets.com'
DEFAULT_BUILD_DOCKER_REPO = 'streamsets/datacollector-libs'

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="Run 'stf <command> -h' for more information on a specific subcommand.")
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('-v', '--verbose', action='store_true', help='Be noisier')
    parser.add_argument('--docker-image',
                        metavar='image',
                        help='Docker image to use for the STF container')
    parser.add_argument('--release',
                        help='Release version to use the appropriate STF image',
                        choices=['3.x', '4.x'])
    parser.add_argument('--docker-image-dont-pull',
                        action='store_true',
                        help="Don't pull STF Docker image")
    parser.add_argument('--docker-network',
                        metavar='network',
                        help='Docker network to which to attach the STF container',
                        default=DEFAULT_DOCKER_NETWORK)
    parser.add_argument('--sdc-resources-directory',
                        metavar='dir',
                        help=('A directory containing resources to mount into the SDC container'))
    parser.add_argument('--testframework-config-directory',
                        metavar='dir',
                        help=("A directory containing STF configuration files to mount into the "
                              "STF container"),
                        default=DEFAULT_TESTFRAMEWORK_CONFIG_DIRECTORY)
    advanced_group = parser.add_argument_group('advanced arguments', 'Stuff for StreamSets devs, mostly')
    advanced_group.add_argument('--streamsets-sdk-directory',
                                metavar='dir',
                                help=("Path to the an `sdk` folder containing source code of the "
                                      "StreamSets SDK for Python"))
    advanced_group.add_argument('--testframework-directory',
                                metavar='dir',
                                help=("A testframework directory to mount into the STF container (for use "
                                      "when making STF changes that don't require a rebuild of the image)"))
    subparsers = parser.add_subparsers(help='Test Framework subcommands', dest='subcommand')

    test_subparser = subparsers.add_parser('test', help='Run STF tests', add_help=False)
    test_subparser.add_argument('test_command', metavar='<test command>',
                                help='Arguments to pass to our test execution framework',
                                nargs=argparse.REMAINDER)
    benchmark_subparser = subparsers.add_parser('benchmark', help = 'Run performance metrics', add_help=False)
    benchmark_subparser.add_argument('benchmark_command', metavar='<test command>',
                                help='Arguments to pass to benchmark framework',
                                nargs=argparse.REMAINDER)

    shell_subparser = subparsers.add_parser('shell', help='Open a shell within the STF container')
    shell_subparser.add_argument('shell_command', metavar='<shell command>',
                                 help='Shell command to execute',
                                 nargs=argparse.REMAINDER)

    build_subparser = subparsers.add_parser('build',
                                            help='Build STF Docker images',
                                            add_help=False)
    build_subparser.add_argument('build_command', metavar='<build command>',
                                 help='Arguments to pass to the image build script',
                                 nargs=argparse.REMAINDER)

    start_parser = subparsers.add_parser('start', help='Start a sub-system')
    start_subparser = start_parser.add_subparsers(help='sub-system to start', dest='sub_system')
    start_subparser.required = True
    start_sdc_subparser = start_subparser.add_parser('sdc', help='Start SDC', add_help=False)

    # Handle the case of `stf` being run without any arguments.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args, unknown = parser.parse_known_args()
    streamsets_logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    client = docker.from_env()

    docker_image = _pick_docker_image(args.docker_image, args.release) or DEFAULT_DOCKER_IMAGE

    if not args.docker_image_dont_pull:
        logger.info('Pulling Docker image %s ...', docker_image)
        client.images.pull(docker_image)

    _create_docker_network(client, args.docker_network)

    container_hostname = _get_stf_container_hostname(client)

    environment = {
        'TZ': os.readlink('/etc/localtime').split('zoneinfo/')[1], # sync host time zone to docker container
        'TESTFRAMEWORK_CONFIG_DIRECTORY': args.testframework_config_directory,
    }
    # TODO: Move the AWS and Azure environment variables into
    #       an ini file.
    for variable in ('AWS_ACCESS_KEY_ID',
                     'AWS_SECRET_ACCESS_KEY',
                     'azure_tenant_id',
                     'azure_client_id',
                     'azure_client_secret',
                     'azure_storage_account_key',
                     'azure_storage_account_name',
                     'azure_eh_sas_connection_primary',
                     'azure_iot_sas_connection_primary',
                     'azure_sb_sas_connection_primary'):
        environment[variable] = os.getenv(variable)

    user_activation_file_path = os.path.join(USER_CONFIG_PATH, 'activation', ACTIVATION_FILE_NAME)
    if not os.path.isfile(user_activation_file_path):
        raise ActivationError('Could not find activation file at {}'.format(user_activation_file_path))
    stf_container_activation_file_path = os.path.join('/root/.streamsets/activation', ACTIVATION_FILE_NAME)

    container_configs = {
        'auto_remove': False,
        'detach': True,
        'environment': environment,
        'hostname': container_hostname,
        'network': args.docker_network,
        'volumes': {args.testframework_config_directory: dict(bind='/etc/testframework', mode='rw'),
                    os.getcwd(): dict(bind='/root/tests', mode='rw'),
                    user_activation_file_path: dict(bind=stf_container_activation_file_path, mode='ro'),
                    '/var/run/docker.sock': dict(bind='/var/run/docker.sock', mode='rw'),
                    os.path.expanduser('~/.docker'): dict(bind='/root/.docker', mode='rw')},
        'tty': True if sys.stdout.isatty() else False,
        'working_dir': '/root/tests',
    }

    if args.sdc_resources_directory:
        environment['SDC_RESOURCES_DIRECTORY'] = os.path.realpath(os.path.expanduser(args.sdc_resources_directory))

    if args.testframework_directory:
        container_configs['volumes'][args.testframework_directory] = dict(bind='/root/testframework', mode='rw')

    if args.streamsets_sdk_directory:
        container_configs['volumes'][args.streamsets_sdk_directory] = dict(bind='/usr/local/lib/python3.6/site-packages/streamsets/sdk', mode='rw')
        environment['STREAMSETS_SDK_DIRECTORY'] = True

    if args.subcommand == 'shell':
        shell_command = 'bash' if not args.shell_command else ' '.join('"{}"'.format(arg) for arg in args.shell_command)
        volumes = ' '.join('-v "{}:{}"'.format(k, v['bind']) for k, v in container_configs['volumes'].items())
        environments = ' '.join('-e {}="{}"'.format(k, (v or '')) for k, v in container_configs['environment'].items())
        interactive = '-i' if sys.stdout.isatty() else ''
        command = 'docker run {} -t --rm -w {} --net {} -h {} {} {} {} {}'.format(interactive,
                                                                                  container_configs['working_dir'],
                                                                                  container_configs['network'],
                                                                                  container_configs['hostname'],
                                                                                  volumes,
                                                                                  environments,
                                                                                  docker_image,
                                                                                  shell_command)
        child = subprocess.Popen(command, shell=True)
        child.communicate()
        sys.exit(child.returncode)
    elif args.subcommand == 'test':
        test_index = sys.argv.index('test')
        command = 'pytest {}'.format(' '.join('"{}"'.format(arg) for arg in sys.argv[test_index+1:]))
        container = client.containers.run(docker_image, command, **container_configs)
        logger.debug('Running command (%s) in STF container (%s) ...', command, container.id)
        for line in container.attach(stream=True):
            sys.stdout.write(line.decode())
    elif args.subcommand == 'benchmark':
        benchmark_index = sys.argv.index('benchmark')
        command = 'pytest {}'.format(' '.join('"{}"'.format(arg) for arg in sys.argv[benchmark_index+1:]))
        container = client.containers.run(args.docker_image, command, **container_configs)
        logger.debug('Running command (%s) in STF container (%s) ...', command, container.id)
        for line in container.attach(stream=True):
            sys.stdout.write(line.decode())
    elif args.subcommand == 'build':
        build_index = sys.argv.index('build')
        build_commands = (['-v'] if args.verbose else []) + sys.argv[build_index+1:]
        command = ('python3 /root/testframework/streamsets/testframework/cli/build.py {}'.format(
            ' '.join('"{}"'.format(arg) for arg in build_commands))
        )
        container = client.containers.run(docker_image, command, **container_configs)
        logger.debug('Running command (%s) in STF container (%s) ...', command, container.id)
        for line in container.attach(stream=True):
            sys.stdout.write(line.decode())
    elif args.subcommand == 'start':
        start_commands = sys.argv[sys.argv.index('start')+1:]
        if args.sub_system == 'sdc':
            sub_system_command = 'python3 /root/testframework/streamsets/testframework/cli/start_sdc.py'
            sub_system_args = ((['-v'] if args.verbose else []) + ['--docker-network', args.docker_network] +
                               start_commands[1:])
            command = ('{} {}'.format(sub_system_command, ' '.join('"{}"'.format(arg) for arg in sub_system_args)))
            container = client.containers.run(docker_image, command, **container_configs)
            logger.debug('Running command (%s) in STF container (%s) ...', command, container.id)
            for line in container.attach(stream=True):
                sys.stdout.write(line.decode())
    # If a container instance was created, we return its status code.
    if 'container' in locals():
        sys.exit(container.wait()['StatusCode'])


def _create_docker_network(client, name):
    try:
        client.networks.create(name=name, check_duplicate=True)
        logger.debug('Successfully created network (%s).', name)
    except docker.errors.APIError as api_error:
        if api_error.explanation == 'network with name {} already exists'.format(name):
            logger.debug('Network (%s) already exists. Continuing without creating ...', name)
        else:
            raise


def _get_stf_container_hostname(client):
    # We set the STF container's hostname to match the host's to make the experience of running
    # tests as seamless as if they were being run from the host itself.

    # We need special logic to check whether Docker for Mac is being used and then handling
    # how it exposes ports to 'localhost'.
    docker_hostname = client.info()['Name']
    logger.debug('Docker detected hostname: %s', docker_hostname)

    hostname = subprocess.check_output('hostname', shell=True, universal_newlines=True).strip()
    logger.debug('Shell detected hostname: %s', hostname)

    if docker_hostname == hostname:
        return subprocess.check_output('hostname -f', shell=True, universal_newlines=True).strip()
    elif docker_hostname.startswith('linuxkit') or docker_hostname == 'moby':
        return 'localhost'


def _add_help(parser):
    """Utility method that adds a help argument to whichever parser is passed to it. This is
    needed to correctly handle display of help messages through the various parsers we create
    dynamically at runtime.

    Args:
        parser (:py:obj:`argparse.ArgumentParser`): Parser instance.
    """
    parser.add_argument('-h', '--help',
                        action='help',
                        default=argparse.SUPPRESS,
                        help='show this help message and exit')


def _pick_docker_image(docker_image, release):
    """Utility method to pick docker image.

    Args:
        docker_image (:obj:`str`): Docker image name with tag from args.
        release (obj:`str`): Release option in {'3.x', '4.x'} from args.

    Returns:
        Docker image as an instance of obj:`str`.
    """
    if docker_image and release:
        raise Exception('Both --docker-image and --release cannot be specified at the same time.')

    if release == '4.x':
        return DOCKER_IMAGE_4_X

    return docker_image
