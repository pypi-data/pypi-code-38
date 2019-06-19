# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from collections import OrderedDict
import argparse
import fnmatch
import hashlib
import io
import itertools
import json
import os
import sys


CHUNK_SIZE = 4096
INFO_DIRECTORY = '.package-info'


def hash_file(filename, hash_function=hashlib.md5, chunk_size=CHUNK_SIZE):
    """
    Compute the hash of file using provided hash algorithm.
    Returns hexadecimal string corresponding to the hash of file.
    """
    hasher = hash_function()
    with io.open(filename, 'rb') as file_object:
        data = file_object.read(chunk_size)
        while data:
            hasher.update(data)
            data = file_object.read(chunk_size)
        return hasher.hexdigest()


def find(root):
    """
    Find all files rooted above the root directory.
    Returns a generator of these files.
    """
    return (os.path.join(dirpath, filename)
            for dirpath, dirnames, filenames in os.walk(root)
            for filename in filenames)


def find_info():
    """
    Find INFO_DIRECTORY if it is located in the file tree above, or in,
    the current working directory.

    Returns the path to the INFO_DIRECTORY if it is found and None if it cannot
    be found.
    """
    for dirpath, dirnames, filenames in os.walk(os.getcwd(), False):
        dirname = os.path.join(dirpath, INFO_DIRECTORY)
        if os.path.isdir(dirname):
            return dirname


def hash_files(root):
    """
    Computes the file hash of all files rooted above the root directory.
    Returns a generator of pairs of filename and corresponding file hash.
    """
    return ((filename, hash_file(filename))
            for filename in find(root))


def added_keys(original, current):
    """
    Given two ordered dictionaries compute the keys present in the
    second dictionary which are not present in the first.

    Returns a generator of such keys preserving the order in which they occur.
    """
    original_set = set(original)
    current_set = set(current)
    added = current_set - original_set
    return (key for key in current if key in added)


def removed_keys(original, current):
    """
    Given two ordered dictionaries compute the keys present in the
    first dictionary which are not present in the second.

    Returns a generator of such keys preserving the order in which they occur.
    """
    return added_keys(current, original)


def modified_values(original, current):
    """
    Given two ordered dictionaries compute the keys common to both dictionaries
    whose corresponding values differ.

    Returns a generator of such keys preserving the order in which they occur.
    """
    original_set = set(original)
    current_set = set(current)
    common = original_set.intersection(current_set)
    return (key for key in original
            if key in common and original[key] != current[key])


def status_mode(args):
    """
    Status mode is the mode used when the command is run with the 'status'
    argument.

    In this case, status changes can be printed.
    As default, all status changes are printed.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--added', '-a', action='store_true')
    parser.add_argument('--modified', '-m', action='store_true')
    parser.add_argument('--removed', '-r', action='store_true')
    parsed = parser.parse_args(args)

    info = find_info()
    try:
        with io.open(os.path.join(info, 'checksums'), 'rb') as f:
            original = json.load(f, object_hook=OrderedDict)
            current = OrderedDict(
                ((key, value) for key, value in hash_files('.')
                 if not fnmatch.fnmatch(key,
                                        os.path.join(
                                            '.', INFO_DIRECTORY, '*'))))
            added = parsed.added
            modified = parsed.modified
            removed = parsed.removed
            if not any([added, modified, removed]):
                added, modified, removed = (True, True, True)
            if added:
                for key in added_keys(original, current):
                    print('A {}'.format(key))
            if modified:
                for key in modified_values(original, current):
                    print('M {}'.format(key))
            if removed:
                for key in removed_keys(original, current):
                    print('R {}'.format(key))
    except:
        if info is None:
            print('Cannot find {}'.format(INFO_DIRECTORY))
        else:
            print('Cannot open checksums.')


def with_resource(resources, function):
    """Yield entered contexts from processing resources in order."""
    for resource in resources:
        with function(resource) as entered:
            yield entered


def init_mode(args):
    """
    Init mode is the mode used when the command is run with the 'init'
    argument.

    In this case, INFO_DIRECTORY is created, containing checksums.
    Unless INFO_DIRECTORY already exists, that is.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--extra-checksum-files', '-f', nargs='*', default=[],
        action='store')
    parser.add_argument(
        '--folders-to-copy', '-c', nargs='*', default=[],
        action='store')
    parser.add_argument(
        '--filter-include', '-i', default='*',  action='store')
    parsed = parser.parse_args(args)

    try:
        os.mkdir(INFO_DIRECTORY)
        with io.open(os.path.join(INFO_DIRECTORY, 'checksums'), 'wb') as f:
            files = ((key, value) for key, value in hash_files('.')
                     if fnmatch.fnmatch(key, parsed.filter_include))

            extra_files = itertools.chain(*(
                json.load(f, object_hook=OrderedDict).iteritems()
                for f in with_resource(parsed.extra_checksum_files,
                                       lambda x: io.open(x, 'rb'))))

            extra_directory_files = (
                (key.replace(d, '.'), value) for d in parsed.folders_to_copy
                for key, value in hash_files(d)
                if fnmatch.fnmatch(key, parsed.filter_include))

            json.dump(
                OrderedDict(
                    (key, value)
                    for key, value in itertools.chain(files,
                                                      extra_files,
                                                      extra_directory_files)
                    if not fnmatch.fnmatch(
                        key,
                        os.path.join('.', INFO_DIRECTORY, '*'))),
                f,
                indent=4)
    except OSError:
        print('Already initialized.')


def main():
    """
    Main package entry point.

    Package is an utility helpful for keeping track of and verifying package
    integrity.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['status', 'init'])
    parsed = parser.parse_args(sys.argv[1:2])
    modes = {'init': init_mode,
             'status': status_mode}

    modes[parsed.mode](sys.argv[2:])


if __name__ == '__main__':
    main()
