from __future__ import print_function

from itertools import chain, groupby
import json
import os
import sys
import tarfile
import tempfile

import docker.utils

def build_docker_image(docker_client, **kwargs):
    build_output = docker_client.build(
        decode=True,
        **kwargs
    )

    build_output_lines = []
    for line in build_output:
        if 'stream' in line:
            sys.stdout.write(line['stream'])
            build_output_lines.append(line['stream'])
        elif 'error' in line:
            sys.stdout.write(line['error'])
            build_output_lines.append(line['error'])

    if 'Successfully built' in build_output_lines[-1] or 'Successfully built' in build_output_lines[-2]:
        return
    else:
        raise RuntimeError("Error building image")

def create_build_context_archive(path, dockerfile=None, include=None):
    """
    Create a Docker build context tar-archive.

    Source: https://github.com/docker/docker-py/blob/master/docker/utils/build.py#L8
    """
    dockerignore = os.path.join(path, '.dockerignore')
    exclude = None
    if os.path.exists(dockerignore):
        with open(dockerignore, 'r') as f:
            exclude = list(filter(bool, f.read().splitlines()))
    context = create_tar(
        path, exclude=exclude, include=include, dockerfile=dockerfile, gzip=False
    )

    return context

def create_tar(path, exclude=None, include=None, dockerfile=None, fileobj=None, gzip=False):
    """
    Create a tar archive for Docker

    Source: https://github.com/docker/docker-py/blob/master/docker/utils/build.py#L8
    """

    root = os.path.abspath(path)
    exclude = exclude or []

    if dockerfile is None:
        dockerfile = 'Dockerfile'

    files = set(docker.utils.exclude_paths(root, exclude, dockerfile=dockerfile))
    if include:
        files = files - set(docker.utils.exclude_paths(
            root, include + [dockerfile], dockerfile='dummy-path-lcas08h028hknj'))

    return create_archive(
        files=sorted(files),
        root=root, fileobj=fileobj, gzip=gzip
    )

def create_archive(root, files=None, fileobj=None, gzip=False):
    """
    Create archive.

    Source: https://github.com/docker/docker-py/blob/master/docker/utils/utils.py#L93
    """
    if not fileobj:
        fileobj = tempfile.NamedTemporaryFile()
    t = tarfile.open(mode='w:gz' if gzip else 'w', fileobj=fileobj)
    if files is None:
        files = docker.utils.build_file_list(root)
    for path in files:
        i = t.gettarinfo(os.path.join(root, path), arcname=path)

        # Normalize file metadata to get deterministic builds
        i.mtime = 1483228800.0 # 2017-01-01
        i.mode = 493 # 0o755
        i.uid = 1000
        i.gid = 1000
        i.uname = 'foo'
        i.gname = 'bar'
        i.pax_headers = {}

        if i is None:
            # This happens when we encounter a socket file. We can safely
            # ignore it and proceed.
            continue

        if docker.constants.IS_WINDOWS_PLATFORM:
            # Windows doesn't keep track of the execute bit, so we make files
            # and directories executable by default.
            i.mode = i.mode & 0o755 | 0o111

        try:
            # We open the file object in binary mode for Windows support.
            with open(os.path.join(root, path), 'rb') as f:
                t.addfile(i, f)
        except IOError:
            # When we encounter a directory the file object is set to None.
            t.addfile(i, None)
    t.close()
    fileobj.seek(0)
    return fileobj

def push_docker_image(docker_client, **kwargs):
    push_output = docker_client.push(
        stream=True,
        decode=True,
        **kwargs
    )

    push_output_items = []
    for item in push_output:
        if 'progress' not in item:
            print(item)
            push_output_items.append(item)

    if 'aux' in push_output_items[-1]:
        return
    else:
        raise RuntimeError("Error building image")
        