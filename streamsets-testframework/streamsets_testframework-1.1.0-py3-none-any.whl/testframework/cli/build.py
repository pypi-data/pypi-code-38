# Copyright 2017 StreamSets Inc.

import argparse
import collections
import io
import json
import logging
import os
import re
import subprocess
import sys
import textwrap
from itertools import chain
from pathlib import Path

import boto3
import javaproperties
from botocore.handlers import disable_signing

from streamsets.testframework import constants, logger as streamsets_logger

DEFAULT_S3_BUCKET = 'nightly.streamsets.com'
DEFAULT_BUILD = 'latest'
DEFAULT_BUILD_PREFIX = 'datacollector'
DEFAULT_BUILD_SUFFIX = 'tarball'
DEFAULT_ENTERPRISE_STAGE_LIBS_MANIFEST_FILENAME = 'repository.manifest.json'
DEFAULT_ENTERPRISE_STAGE_LIBS_BUILD_SUFFIX = 'tarball/enterprise'
DEFAULT_ENVIRONMENT_LIBRARIES_DOCKER_REPO = 'streamsets/environment-libs'
DEFAULT_ENVIRONMENT_LIBRARIES_ROOT_DIRECTORY_PATH = Path('/root/testframework/streamsets/testframework/libraries/'
                                                         'environment')
DEFAULT_EXTRA_LIBRARIES_DOCKER_REPO = 'streamsets/sdc-extra-libs'
DEFAULT_EXTRA_LIBRARIES_ROOT_DIRECTORY_PATH = Path('/root/testframework/streamsets/testframework/libraries/extra')
DEFAULT_DOCKER_REPO = 'streamsets/datacollector-libs'
DEFAULT_LEGACY_BUILD_SUFFIX = 'legacy'
DEFAULT_SDC_DOCKER_REPO_URL = 'https://github.com/streamsets/datacollector-docker.git'
DEFAULT_STAGE_LIB_MANIFEST_FILENAME = 'stage-lib-manifest.properties'
DEFAULT_STAGE_LIBRARIES_DIRECTORY_PATH = Path('/root/testframework/streamsets/testframework/libraries/stage')
DEFAULT_BUILD_ARGS = []

# Minimum SDC versions to enforce for stages.
SDC_MIN_VERSION = {'streamsets-datacollector-pmml-lib': '3.5.0'}

logger = logging.getLogger('streamsets.testframework.cli.build')


# Useful to get newlines in the print help
class ArgumentHybridFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


class DockerImage:
    def __init__(self, name, tags, dockerfile_path, build_args):
        self.name = name
        self.tags = tags
        self.dockerfile_path = dockerfile_path
        self.build_args = build_args


def main():
    """Main function invoked from command line."""
    parser = argparse.ArgumentParser(
        prog='stf build',
        description='Build the Docker images used by the StreamSets Test Framework',
        formatter_class=ArgumentHybridFormatter
    )

    parser.add_argument('-v', '--verbose', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--s3-bucket',
                        help='S3 bucket to get tarballs from',
                        default=DEFAULT_S3_BUCKET)
    parser.add_argument('--build',
                        help='The build to use from S3 (e.g. of the form "2038," "2.4," "latest")',
                        default=DEFAULT_BUILD)
    parser.add_argument('--use-aws-credentials',
                        help='If set, use local AWS credentials when communicating with Amazon S3',
                        action='store_true')
    parser.add_argument('--dry-run',
                        help="Don't actually do the `docker build`",
                        action='store_true')
    parser.add_argument('--version-tag',
                        help='A tag to use for images instead of the version gleamed from '
                             'stage-lib-manifest.properties',
                        metavar='tag')
    parser.add_argument('--stage-library',
                        help='Stage library to build; can be invoked multiple times to specify several, '
                             'but will default to selecting all available stage libraries if omitted',
                        action='append')
    parser.add_argument('--push',
                        help='Push Docker images after building',
                        action='store_true')
    parser.add_argument('--build-arg',
                        help='Build argument to pass to docker build command',
                        action='append',
                        default=DEFAULT_BUILD_ARGS)
    parser.add_argument('--build-prefix',
                        help='Key prefix to use',
                        default=DEFAULT_BUILD_PREFIX)
    parser.add_argument('--build-suffix',
                        help='Key suffix to use',
                        default=DEFAULT_BUILD_SUFFIX)
    parser.add_argument('--docker-repo',
                        help='Docker repo to use',
                        default=DEFAULT_DOCKER_REPO)

    subparsers = parser.add_subparsers(help='Build targets', dest='target')

    sdc_subparser = subparsers.add_parser('sdc', help='Build SDC image', formatter_class=ArgumentHybridFormatter)
    stage_subparser = subparsers.add_parser('stage-libraries', help='Build SDC stage libraries',
                                            formatter_class=ArgumentHybridFormatter)
    additional_stage_subparser = subparsers.add_parser('additional-stage-libraries',
                                                       help='Build SDC additional stage libraries',
                                                       formatter_class=ArgumentHybridFormatter)

    extras_subparser = subparsers.add_parser('extras', help='Build extra libraries', add_help=False,
                                             formatter_class=ArgumentHybridFormatter)
    extras_subparser.add_argument('--extra-library',
                                  help='Extra library to build; can be invoked multiple times to specify several, '
                                       'but will default to selecting all available extra libraries if omitted',
                                  action='append')
    extras_subparser.add_argument('--extra-library-docker-repo',
                                  help='Docker repo to use for extra libraries',
                                  default=DEFAULT_EXTRA_LIBRARIES_DOCKER_REPO)

    enterprise_stage_subparser = subparsers.add_parser('enterprise-stage-libraries',
                                                       help='Build SDC enterprise libraries',
                                                       formatter_class=ArgumentHybridFormatter)

    environments_subparser = subparsers.add_parser('environments', help='Build environment libraries',
                                                   add_help=False, formatter_class=ArgumentHybridFormatter)
    environments_subparser.add_argument('--environment-library',
                                        help='Environment library to build; can be invoked multiple times to specify '
                                             'several, but will default to selecting all available environment '
                                             'libraries if omitted',
                                        action='append')
    environments_subparser.add_argument('--environment-library-docker-repo',
                                        help='Docker repo to use for environment libraries',
                                        default=DEFAULT_ENVIRONMENT_LIBRARIES_DOCKER_REPO)

    # all args assumed to be set before this. Doing to get any help to be added for subcommands later.
    args, unknown_args = parser.parse_known_args()
    streamsets_logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    bucket = _get_s3_bucket(args)
    images = []

    if args.target in ['stage-libraries', 'additional-stage-libraries']:
        _add_stage_libs_images(args, bucket, images)
    elif args.target == 'enterprise-stage-libraries':
        _add_enterprise_stage_libs_images(args, bucket, images)
    elif args.target == 'extras':
        _handle_extra_libs(args, images, extras_subparser)
    elif args.target == 'environments':
        _handle_environment_libs(args, images, environments_subparser)
    elif args.target == 'sdc':
        _add_sdc_image(args, bucket, images)

    parser.parse_args()

    if args.dry_run:
        logger.info('Doing dry-run of tool ...')


    images_with_build_errors = build_images(images=images,
                                            dry_run=args.dry_run)

    images_with_tag_errors = tag_images(set(images)
                                        - images_with_build_errors,
                                        dry_run=args.dry_run)

    images_with_push_errors = (push_images(set(images)
                                           - images_with_build_errors
                                           - images_with_tag_errors,
                                           dry_run=args.dry_run)
                               if args.push
                               else set())

    images_without_errors = (set(images)
                             - images_with_build_errors
                             - images_with_tag_errors
                             - images_with_push_errors)

    if images_without_errors:
        logger.info('%s images were successfully created:\n%s',
                    len(images_without_errors),
                    '\n'.join('* {0}'.format(image.name) for image in sorted(images_without_errors,
                                                                             key=lambda image: image.name)))

    if images_with_build_errors:
        logger.error('%s images had build errors:\n%s',
                     len(images_with_build_errors),
                     '\n'.join('* {0}'.format(image.name) for image in sorted(images_with_build_errors,
                                                                              key=lambda image: image.name)))

    if images_with_push_errors:
        logger.error('%s images had push errors:\n%s',
                     len(images_with_push_errors),
                     '\n'.join('* {0}'.format(image.name) for image in sorted(images_with_push_errors,
                                                                              key=lambda image: image.name)))

    if images_with_build_errors or images_with_push_errors:
        sys.exit(1)


def _add_sdc_image(args, bucket, images):
    key_prefix = '/'.join((args.build_prefix, args.build, args.build_suffix))

    manifest_version = _get_stage_lib_version(bucket=bucket, key_prefix=key_prefix)
    tag_version = args.version_tag or manifest_version
    logger.info('This will build image for version %s ...', manifest_version)

    build_args = dict(
        SDC_URL=_get_s3_object_url(bucket, f'{key_prefix}/streamsets-datacollector-core-{manifest_version}.tgz'),
        SDC_VERSION=manifest_version,
        **{build_arg.split('=')[0]: build_arg.split('=')[1]
           for build_arg in args.build_arg}
    )
    images.append(DockerImage(
        name=f'streamsets/datacollector:{tag_version}',
        tags=[f"streamsets/datacollector:{tag_version.split('-')[0]}-latest"],
        dockerfile_path=DEFAULT_SDC_DOCKER_REPO_URL,
        build_args=build_args
    ))


def _add_stage_libs_images(args, bucket, images):
    # Stage libs can be current or legacy. To handle the latter case, we compose both possibilities,
    # looking for tarballs at the former location first.
    key_prefix = '/'.join((args.build_prefix, args.build, args.build_suffix))
    legacy_key_prefix = '/'.join((args.build_prefix, args.build, DEFAULT_LEGACY_BUILD_SUFFIX))

    manifest_version = _get_stage_lib_version(bucket=bucket, key_prefix=key_prefix)
    tag_version = args.version_tag or manifest_version
    logger.info('This will build images for version %s ...', manifest_version)

    is_additional_stage_lib = (args.target == 'additional-stage-libraries')
    for object_ in chain(bucket.objects.filter(Prefix=key_prefix),
                         bucket.objects.filter(Prefix=legacy_key_prefix)):
        if object_.key.endswith(f'-lib-{manifest_version}.tgz'):
            key_match = re.search(f'{key_prefix}/(.*)-{manifest_version}.tgz', object_.key)
            legacy_key_match = re.search(f'{legacy_key_prefix}/(.*)-{manifest_version}.tgz', object_.key)
            is_legacy_stage_lib = bool(legacy_key_match)
            stage_lib_name = (key_match or legacy_key_match).group(1)

            name = f'{args.docker_repo}:{stage_lib_name}-{tag_version}'
            tags = [f"{args.docker_repo}:{stage_lib_name}-{tag_version.split('-')[0]}-latest"]
            tarball_url = _get_s3_object_url(bucket, object_.key)

            build_args = dict(
                SDC_MIN_VERSION=SDC_MIN_VERSION.get(stage_lib_name, '1.0.0'),
                STAGE_LIB_ROOT=('/opt/streamsets-datacollector-user-libs'
                                if is_legacy_stage_lib or is_additional_stage_lib
                                else '/opt'),
                STAGE_LIB_DIRECTORY=(f'/opt/streamsets-datacollector-user-libs/{stage_lib_name}'
                                     if is_legacy_stage_lib or is_additional_stage_lib
                                     else (f'/opt/streamsets-datacollector-{manifest_version}/'
                                           f'streamsets-libs/{stage_lib_name}')),
                STAGE_LIB_S3_BUCKET=args.s3_bucket,
                STAGE_LIB_S3_OBJECT_KEY=object_.key,
                **{build_arg.split('=')[0]: build_arg.split('=')[1]
                   for build_arg in args.build_arg}
            )

            if not args.stage_library or stage_lib_name in args.stage_library:
                images.append(DockerImage(name=name,
                                          tags=tags,
                                          dockerfile_path=DEFAULT_STAGE_LIBRARIES_DIRECTORY_PATH,
                                          build_args=build_args))


# TODO: STF-685. stf build: Add help to print applicable libs
def _add_enterprise_stage_libs_images(args, bucket, images):
    key_prefix = '/'.join((args.build_prefix, args.build, DEFAULT_ENTERPRISE_STAGE_LIBS_BUILD_SUFFIX))
    # Parse the manifest file to get versions of all enterprise stage libs.
    enterprise_stage_libs_versions = _get_enterprise_stage_libs_versions(bucket=bucket, key_prefix=key_prefix)
    for object_ in bucket.objects.filter(Prefix=key_prefix):
        if object_.key.endswith('.tgz'):
            logger.info('object_.key = %s', object_.key)
            stage_lib_name_match = re.search(f'{key_prefix}/(.*)lib', object_.key)
            # Get manifest_versions for this stage lib.
            manifest_versions = enterprise_stage_libs_versions.get(f'{stage_lib_name_match.group(1)}lib', None)
            object_key_lib_version = object_.key.split('lib-')[1].strip('.tgz')
            if object_key_lib_version in manifest_versions:
                tag_version = args.version_tag or object_key_lib_version

                key_match = re.search(f'{key_prefix}/(.*)-{object_key_lib_version}.tgz', object_.key)
                stage_lib_name = (key_match).group(1)

                name = f'{args.docker_repo}:{stage_lib_name}-{tag_version}'
                tags = [f"{args.docker_repo}:{stage_lib_name}-{tag_version.split('-')[0]}-latest"]

                stage_lib_directory = f'{constants.DATACOLLECTOR_ENTERPRISE_LIBS_MOUNT_POINT}/{stage_lib_name}'
                stage_lib_root = '/opt/streamsets-datacollector-enterprise-libs'

                build_args = dict(
                    SDC_MIN_VERSION=SDC_MIN_VERSION.get(stage_lib_name, '1.0.0'),
                    STAGE_LIB_ROOT=stage_lib_root,
                    STAGE_LIB_DIRECTORY=stage_lib_directory,
                    STAGE_LIB_S3_BUCKET=args.s3_bucket,
                    STAGE_LIB_S3_OBJECT_KEY=object_.key,
                    **{build_arg.split('=')[0]: build_arg.split('=')[1]
                       for build_arg in args.build_arg}
                )

                if not args.stage_library or stage_lib_name in args.stage_library:
                    images.append(DockerImage(name=name,
                                              tags=tags,
                                              dockerfile_path=DEFAULT_STAGE_LIBRARIES_DIRECTORY_PATH,
                                              build_args=build_args))


def _handle_extra_libs(args, images, extras_subparser):
    build_args = {build_arg.split('=')[0]: build_arg.split('=')[1] for build_arg in args.build_arg}
    extra_lib_names = [name for name in os.listdir(DEFAULT_EXTRA_LIBRARIES_ROOT_DIRECTORY_PATH)
                       if os.path.isdir(DEFAULT_EXTRA_LIBRARIES_ROOT_DIRECTORY_PATH.joinpath(name))]
    for extra_lib_name in extra_lib_names:
        if not args.extra_library or extra_lib_name in args.extra_library:
            name = f'{args.extra_library_docker_repo}:{extra_lib_name}'
            images.append(
                DockerImage(name=name,
                            tags=[],
                            dockerfile_path=DEFAULT_EXTRA_LIBRARIES_ROOT_DIRECTORY_PATH.joinpath(extra_lib_name),
                            build_args=build_args))
    print_extra_libs = ('''
            Applicable extra libraries
            --------------------------
            {}
            ''').format('\n        '.join(sorted(extra_lib_names)))
    extras_subparser.description = textwrap.dedent(print_extra_libs)
    _add_help(extras_subparser)


def _handle_environment_libs(args, images, environments_subparser):
    build_args = {build_arg.split('=')[0]: build_arg.split('=')[1] for build_arg in args.build_arg}
    env_lib_names = [name for name in os.listdir(DEFAULT_ENVIRONMENT_LIBRARIES_ROOT_DIRECTORY_PATH)
                     if os.path.isdir(DEFAULT_ENVIRONMENT_LIBRARIES_ROOT_DIRECTORY_PATH.joinpath(name))]
    for env_lib_name in env_lib_names:
        if not args.environment_library or env_lib_name in args.environment_library:
            name = f'{args.environment_library_docker_repo}:{env_lib_name}'
            images.append(DockerImage(name=name, tags=[],
                                      dockerfile_path=
                                      DEFAULT_ENVIRONMENT_LIBRARIES_ROOT_DIRECTORY_PATH.joinpath(env_lib_name),
                                      build_args=build_args))
    print_env_libs = ('''
            Applicable environment libraries
            --------------------------------
            {}
            ''').format('\n        '.join(sorted(env_lib_names)))
    environments_subparser.description = textwrap.dedent(print_env_libs)
    _add_help(environments_subparser)


def build_images(images, dry_run):
    """Do the actual building of Docker images.

    Args:
        images (:obj:`list`): List of :py:class:`streamsets.testframework.cli.build.DockerImage` instances.
        dry_run (:obj:`bool`): If ``True``, don't actually execute Docker commands (but display what they are).

    Returns:
        (:obj:`set`): A set of images with build errors.
    """
    # To handle any errors during the `docker build`, keep a set. This will also be used to exclude
    # images from being pushed if this script is run with --push.
    images_with_build_errors = set()

    for image in sorted(images, key=lambda image: image.name):
        try:
            cmd = (f'docker build --no-cache -t {image.name} '
                   + ' '.join(f'--build-arg {key}={value}' for key, value in image.build_args.items())
                   + f' {image.dockerfile_path}')
            logger.debug('Running Docker build command (%s) ...', cmd)
            if not dry_run:
                subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            logger.error('Non-zero exit code seen while building %s ...',
                         image.name)
            images_with_build_errors.add(image)
    return images_with_build_errors


def tag_images(images, dry_run):
    """Tag successfully built images.

    Args:
        images (:obj:`list`): List of :py:class:`streamsets.testframework.cli.build.DockerImage` instances.
        dry_run (:obj:`bool`): If ``True``, don't actually execute Docker commands (but display what they are).

    Returns:
        (:obj:`set`): A set of images with tag errors.
    """
    images_with_tag_errors = set()

    for image in sorted(images, key=lambda image: image.name):
        for tag in image.tags:
            try:
                cmd = f'docker tag {image.name} {tag}'
                logger.debug('Running Docker tag command (%s) ...', cmd)
                if not dry_run:
                    subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                logger.error('Non-zero exit code seen while tagging %s ...',
                             tag)
                images_with_tag_errors.add(image)
    return images_with_tag_errors


def push_images(images, dry_run):
    """Push Docker images
    Args:
        images (:obj:`set`): Docker images to push.
        dry_run (:obj:`bool`): If ``True``, don't actually execute Docker commands (but display what they are).
    Returns:
        (:obj:`set`): A set of images with push errors.
    """
    images_with_push_errors = set()
    # Iterate over every successfully-built image (i.e. all images except those that show up in
    # the build errors list).
    logger.info('Beginning `docker push` of successfully-built images ...')
    for image in sorted(images, key=lambda image: image.name):
        for image_name in [image.name] + image.tags:
            try:
                cmd = f'docker push {image_name}'
                logger.debug('Running Docker push command (%s) ...', cmd)
                if not dry_run:
                    subprocess.run(cmd,
                                   shell=True,
                                   check=True)
            except subprocess.CalledProcessError:
                logger.error('Non-zero exit code seen while pushing %s ...', image_name)
                images_with_push_errors.add(image)

    return images_with_push_errors


def _get_s3_bucket(args):
    """Return an S3.Bucket instance."""
    s3_resource = boto3.resource('s3')
    # In general, the S3 buckets hosting our public-facing artifacts can be accessed in anonymous mode, so
    # disable signing for our S3 client unless otherwise specified.
    if not args.use_aws_credentials:
        s3_resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
    return s3_resource.Bucket(args.s3_bucket)


def _get_s3_object_url(bucket, key):
    """Return a string of the public URL of an S3 object."""
    # Following AWS's conventions for accessing virtual-hosted-style URLs (see
    # http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html#access-bucket-intro).
    return 'http://{bucket}.s3.amazonaws.com/{key}'.format(bucket=bucket.name,
                                                           key=key) if _s3_key_exists(bucket, key) else None


def _get_stage_lib_version(bucket, key_prefix):
    """Parse the stage lib manifest properties file to determine the version corresponding to
    this build.
    """
    # Instead of dealing with temporary files, just use Bucket.download_fileobj to copy the contents
    # of the manifest file to a BytesIO instance, which we need to read and decode before parsing.
    fileobj = io.BytesIO()
    manifest_key = '/'.join((key_prefix, DEFAULT_STAGE_LIB_MANIFEST_FILENAME))
    logger.debug('Getting stage-lib-manifest.properties file (%s) ...', manifest_key)
    bucket.download_fileobj(manifest_key, fileobj)
    fileobj.seek(0)

    # Each manifest has a 'version=...' line, which is all we care to parse out.
    return javaproperties.load(fileobj)['version']


def _get_enterprise_stage_libs_versions(bucket, key_prefix):
    # Instead of dealing with temporary files, just use Bucket.download_fileobj to copy the contents
    # of the manifest file to a BytesIO instance, which we need to read and decode before parsing.
    fileobj = io.BytesIO()
    manifest_key = '/'.join((key_prefix, DEFAULT_ENTERPRISE_STAGE_LIBS_MANIFEST_FILENAME))
    logger.debug('Getting manifest file (%s) ...', manifest_key)
    bucket.download_fileobj(manifest_key, fileobj)
    fileobj.seek(0)

    data = json.load(fileobj)

    # Create a dictionary with entries of the form key='stage lib name' and value='a set of versions'.
    # e.g. {'streamsets-datacollector-teradata-lib': {'1.1.0-SNAPSHOT', '1.0.0-SNAPSHOT'},
    #      'streamsets-datacollector-snowflake-lib': {'1.0.0-SNAPSHOT', '1.1.0-SNAPSHOT'}}
    stage_libs_versions = collections.defaultdict(set)
    for item in data['stage-libraries']:
        stage_libs_versions[f"{item['stagelib.manifest'].split('lib')[0]}lib"].add(item['stagelib.version'])

    return stage_libs_versions


def _s3_key_exists(bucket, key):
    """Return whether the given key exists in the bucket."""
    try:
        return next(iter(bucket.objects.filter(Prefix=key))).key == key
    except StopIteration:
        return False


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


if __name__ == '__main__':
    main()
