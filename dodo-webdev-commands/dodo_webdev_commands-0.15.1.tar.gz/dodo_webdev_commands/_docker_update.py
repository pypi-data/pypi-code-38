from plumbum.cmd import docker
from dodo_commands.framework import Dodo


def _docker_image(name):
    return Dodo.get_config('DOCKER/images/%s/image' % name, name)


def add_name_argument(parser, choices=None):
    parser.add_argument(
        'name',
        help='Identifies docker image in /DOCKER/images',
        choices=choices or Dodo.get_config('/DOCKER/images', {}).keys())


def commit_container(docker_image):
    container_id = docker("ps", "-l", "-q")[:-1]
    docker("commit", container_id, _docker_image(docker_image))
    docker("rm", container_id)


def patch_docker_options(docker_image):
    docker_options = Dodo.get_config('/DOCKER') \
        .setdefault('options', {}) \
        .setdefault(Dodo.command_name, {})

    docker_options.setdefault('image', _docker_image(docker_image))
    docker_options.setdefault('rm', False)
