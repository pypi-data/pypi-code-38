#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Imports
import json
import argparse
from os import path, environ, makedirs, walk, remove, rmdir, listdir
from shutil import copy, copytree, rmtree
import contextlib
import socket
from git import Repo
from git.exc import GitCommandError

#  Constants
REPO_DIR = environ['HOME'] + '/.local_configurations'
repo = Repo(REPO_DIR)


class Environment:
    def __init__(self, repo_dir, **kwargs):
        self.full_file_path = path.abspath(kwargs['filename'])
        self.filename = path.basename(self.full_file_path)
        self.user = environ.get('USER')
        self.host = socket.gethostname()
        self.repo_dir = repo_dir
        self.index_path = path.join(self.repo_dir, 'index.json')
        self.hostname_dir = path.join(self.repo_dir, self.host)

    @property
    def destination_path(self):
        return path.join(self.repo_dir, self.user + '@' + self.host, self.filename)

    @property
    def destination_dir(self):
        return path.join(self.repo_dir, self.user + '@' + self.host)


def copy_dir(source_dir, dest_dir):
    dir_name = path.basename(source_dir)
    copytree(source_dir, path.join(dest_dir, dir_name))


def silent_remove_dir(dir_path):
    with contextlib.suppress(FileNotFoundError):
        rmtree(dir_path)


def silent_create(directory):
    with contextlib.suppress(FileExistsError):
        makedirs(directory)
    return directory


def silent_remove(filename):
    with contextlib.suppress(FileNotFoundError):
        remove(filename)


def path_to_object(file_path):
    return path.basename(file_path), file_path


def insert_path_into_path_json(user, host, file_path, path_json):
    file_name, file_path = path_to_object(file_path)
    key = user + '@' + host
    path_json = path_json.setdefault(key, {})
    path_json[file_name] = file_path


def retrieve_or_create_index_file(index_path):
    #  file at index_path and format correct
    if path.isfile(index_path):
        with open(index_path, 'r') as handle:
            index = json.load(handle)

    #  no file found
    else:
        index = {}
        index_path = path.join(index_path, 'index.json')
        with open(index_path, 'w') as handle:
            json.dump(index, handle)

    return index


if __name__ == '__main__':

    #  Arguments
    parser = argparse.ArgumentParser(description='Backup local system files with ease.')
    parser.add_argument('filename',
                        metavar='FILENAME',
                        type=str,
                        help='Filename of config file.')

    parser.add_argument('-d', '--delete',
                        action='store_true',
                        help='Delete a file and remove its reference.')

    args = vars(parser.parse_args())

    env = Environment(REPO_DIR, **args)
    index_file = retrieve_or_create_index_file(env.index_path)

    if args['delete']:
        #  TODO; delete file
        pass
    else:
        silent_create(env.destination_dir)
        if path.isfile(env.full_file_path):
            silent_remove(env.destination_path)
            copy(env.full_file_path, env.destination_dir)
        else:
            dest_path = path.join(env.destination_dir, env.filename)
            silent_remove_dir(dest_path)
            copy_dir(env.full_file_path, env.destination_dir)

        insert_path_into_path_json(env.user, env.host, env.full_file_path, index_file)

    with open(env.index_path, 'w') as handle:
        json.dump(index_file, handle)

    repo.git.add('--all')

    try:
        repo.git.commit('-am', args['filename'])
        origin = repo.remote(name='origin')
        #  with repo.git.custom_environment(
        #          GIT_SSH_COMMAND='ssh -v -i ~/.ssh/id_rsa'):
        #      origin.push()
        origin.push()
    except GitCommandError as e:
        print(str(e))
