#!/usr/bin/env python3

#  Imports
import sys
from os import path, environ, makedirs, walk, remove, rmdir, listdir
from shutil import copy
import socket
print(sys.path)
from git import Repo
from git.exc import GitCommandError

#  Constants
BASE_DIR = environ['HOME'] + '/.local_configurations'
repo = Repo(BASE_DIR)


class Environment:
    def __init__(self, args, base_dir):
        self.fullpath = path.abspath(args.filename)
        self.filename = self.fullpath.split('/')[-1]
        self.hostname = socket.gethostname()
        self.base_dir = base_dir
        self.hostname_dir = path.join(self.base_dir, self.hostname)
        self.directory = args.dir + '/' if args.dir else ''
        print("Self directory: ", self.directory)

    @property
    def save_name(self):
        return self.fullpath.replace('/', '++')

    @property
    def destination_path(self):
        return path.join(self.hostname_dir, self.directory)


def delete_if_file_exists(file, hostname_dir):
    """Check if file exists somewhere inside the repo."""
    print("file: ", file)
    print("hostname_dir: ", hostname_dir)
    for root, dirs, files in walk(hostname_dir):
        for name in files:
            print(name)
            if name == file:
                remove(path.join(root, file))

def remove_empty_dirs(hostname_dir):
    """Walk repo and delete any empty folders."""
    for root, dirs, files in walk(hostname_dir):
        for dir in dirs:
            if len(listdir(path.join(root, dir))) == 0:
                print("Will remove empty directory:")
                print(path.join(root, dir))
                rmdir(path.join(root, dir))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Backup local system files with ease.')
    parser.add_argument('filename',
                        metavar='FILENAME',
                        type=str,
                        help='Filename of config file.')
    parser.add_argument('--dir',
                        metavar='DIRECTORY',
                        type=str,
                        help='Specify directory under which file is to be saved.')

    args = parser.parse_args()
    print(args)

    if path.exists(args.filename):
        env = Environment(args, BASE_DIR)
        env.hostname = socket.gethostname()
        # check if there is already a dir for this machine
        if not path.exists(env.destination_path):
            makedirs(env.destination_path)

        # check if file exists somewhere in the repo already
        delete_if_file_exists(env.save_name, env.hostname_dir)

        copy(env.fullpath, env.destination_path + env.save_name)
        if path.isfile(env.destination_path + env.save_name):
            print('File successfully copied')

        # clean up empty dirs
        remove_empty_dirs(env.hostname_dir)

        repo.git.add('--all')
        try:
            repo.git.commit('-am', args.filename)
            origin = repo.remote(name='origin')
            #  with repo.git.custom_environment(
            #          GIT_SSH_COMMAND='ssh -v -i ~/.ssh/id_rsa'):
            #      origin.push()
            origin.push()
        except GitCommandError as e:
            print(str(e))

    else:
        #  raise argparse.ArgumentError(
        #      'Please provide exactly one argument for the file name')
        print("Please provide exactly one argument for the file name (must exist)")
        sys.exit()
