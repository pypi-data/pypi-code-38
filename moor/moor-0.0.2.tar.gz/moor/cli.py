import argparse
import json
import re
import subprocess
import sys
import traceback

import moor
from moor.config import BuildContext

DOCKER_PS_REGEX = re.compile(r'^([a-f0-9]{12})\s+(.*?)\s+.*$')
DOCKER_IMAGES_REGEX = re.compile(r'^(.*?)\s+(.*?)\s+.*$')


def _split_container_image(image_name):
    tag_parts = image_name.split(':')
    assert len(tag_parts) in (1, 2)

    label = None
    if len(tag_parts) == 2:
        label = tag_parts[1]

    parts = tag_parts[0].split('/')
    base_image = parts[-1]
    registry = '/'.join(parts[:-1])

    if len(registry) == 0:
        registry = None

    return registry, base_image, label


def _docker_images():
    cmd = ['docker', 'images', '--format', '{{ json . }}']
    output = subprocess.check_output(cmd).decode().splitlines()

    result = []
    for line in output:
        result.append(json.loads(line))

    return result


def _docker_ps():
    cmd = ['docker', 'ps', '-a', '--format', '{{ json . }}']
    output = subprocess.check_output(cmd).decode().splitlines()

    result = []
    for line in output:
        result.append(json.loads(line))

    return result


def _find_old_containers(ctx: BuildContext):
    old_containers = set()
    for container in _docker_ps():
        registry, base_image, _ = _split_container_image(container['Image'])

        # determine if the image should be removed
        remove = False
        if base_image == ctx.name:
            if registry is None:
                remove = True
            else:
                remove = registry == ctx.registry

        # add the container id if needed
        if remove:
            old_containers.add(container['ID'])
    return old_containers


def _find_old_images(ctx: BuildContext):
    old_images = set()
    for image in _docker_images():
        if image['Tag'] == '<none>':
            continue

        registry, base_image, _ = _split_container_image(image['Repository'])

        remove = False
        if base_image == ctx.name:
            if registry is None:
                remove = True
            else:
                remove = registry == ctx.registry

        if remove:
            old_images.add(f"{image['Repository']}:{image['Tag']}")

    return old_images


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable extra debugging')
    parser.add_argument('-v', '--version', action='store_true', help='Print the version and exit')
    subparsers = parser.add_subparsers()

    parser_build = subparsers.add_parser('build', help='Builds a docker image')
    parser_build.add_argument('-n', '--dry-run', action='store_true')
    parser_build.add_argument('-l', '--local', action='store_true', help='Build a local version of the image only')
    parser_build.add_argument('path', default='.', nargs='?', help='The path to build context')
    parser_build.set_defaults(handler=run_build)

    parser_info = subparsers.add_parser('info', help='Prints useful information about a build')
    parser_info.add_argument('path', default='.', nargs='?', help='The path to build context')
    parser_info.set_defaults(handler=run_info)

    parser_publish = subparsers.add_parser('publish', help='Builds and pushes the image to the remove repository')
    parser_publish.add_argument('path', default='.', nargs='?', help='The path to build context')
    parser_publish.set_defaults(handler=run_publish)

    parser_remove_old = subparsers.add_parser('remove-old', help='Removes old containers and images for the context')
    parser_remove_old.add_argument('path', default='.', nargs='?', help='The path to build context')
    parser_remove_old.set_defaults(handler=run_remove_old)

    return parser, parser.parse_args()


def run_build(args):
    ctx = BuildContext(args.path)
    ctx.build_image(args.local)


def run_info(args):
    ctx = BuildContext(args.path)

    print('      Name:', ctx.name)
    print('Latest Tag:', ctx.latest_tag)
    print(' Local Tag:', ctx.local_tag)
    print('Remove Tag:', ctx.remote_tag)


def run_publish(args):
    ctx = BuildContext(args.path)
    ctx.build_image()
    ctx.push_image()


def run_remove_old(args):
    ctx = BuildContext(args.path)

    for container_id in _find_old_containers(ctx):
        cmd = ['docker', 'rm', container_id]
        subprocess.check_call(cmd)

    # remove all of the old images at once
    old_images = _find_old_images(ctx)
    if len(old_images):
        cmd = ['docker', 'rmi'] + list(old_images)
        subprocess.check_call(cmd)


def main():
    exit_code = 1

    parser, args = parse_commandline()

    # quick exit for just the version
    if args.version:
        print('v' + moor.__version__)
        return

    try:
        if hasattr(args, 'handler'):
            ret = args.handler(args)
            if ret is None:
                exit_code = None
            elif isinstance(ret, int):
                exit_code = ret
        else:
            parser.print_usage()

    except Exception as ex:
        if args.debug:
            traceback.print_exc()
        print('Error:', ex)

    sys.exit(exit_code)
