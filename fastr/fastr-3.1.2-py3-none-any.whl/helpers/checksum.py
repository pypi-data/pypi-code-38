# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains a number of functions for checksumming files and objects
"""
import hashlib
import _hashlib
import io
import os
import pickle
from fastr import exceptions


def checksum(filepath, algorithm='md5', hasher=None, chunksize=32768):
    """
    Generate the checksum of a file

    :param filepath: path of the file(s) to checksum
    :type filepath: str, list
    :param str algorithm: the algorithm to use
    :param _hashlib.HASH hasher: a hasher to continue updating (rather then creating a new one)
    :return: the checksum
    :rtype: str
    """
    if isinstance(filepath, str):
        filepath = [filepath]

    if hasher is None:
        hasher = hashlib.new(algorithm)

    for path in filepath:
        if os.path.isdir(path):
            checksum_directory(path, hasher=hasher)
        else:
            _checksum_file(path, hasher=hasher, chunksize=chunksize)
    return hasher.hexdigest()


def _checksum_file(path: str, hasher: _hashlib.HASH, chunksize: int=32768):
    """
    Hash a file to a hasher

    :param path:
    :param hasher:
    """
    with open(path, 'rb') as file_handle:
        data = file_handle.read(chunksize)
        while data:
            hasher.update(data)
            data = file_handle.read(chunksize)


def checksum_directory(directory, algorithm='md5', hasher=None):
    """
    Generate the checksum of an entire directory

    :param str directory: path of the file(s) to checksum
    :param str algorithm: the algorithm to use
    :param _hashlib.HASH hasher: a hasher to continue updating (rather then creating a new one)
    :return: the checksum
    :rtype: str
    """
    if not os.path.isdir(directory):
        raise exceptions.FastrValueError('{} does not point to a valid directory!'.format(directory))

    if hasher is None:
        hasher = hashlib.new(algorithm)

    for root, dirs, files in os.walk(directory):
        relroot = os.path.relpath(root, directory)
        for d in dirs:
            hasher.update(os.path.join(relroot, d).encode())

        for filename in files:
            hasher.update(os.path.join(relroot, filename).encode())

            _checksum_file(os.path.join(root, filename), hasher)

    return hasher.hexdigest()


def hashsum(objects, hasher=None):
    """
    Generate the md5 checksum of (a) python object(s)

    :param objects: the objects to hash
    :param hasher: the hasher to use as a base
    :return: the hash generated
    :rtype: str
    """
    if hasher is None:
        hasher = hashlib.new('md5')

    if not isinstance(objects, list):
        objects = [objects]

    for obj in objects:
        if isinstance(obj, str):
            hasher.update(obj.encode())
        elif isinstance(obj, (bool, int, float)):
            hasher.update(str(obj).encode())
        elif isinstance(obj, io.TextIOBase):
            # Make sure to hash entire file
            obj.seek(0)
            while True:
                data = obj.read(32768)
                if not data:
                    break
                hasher.update(data.encode())
        elif isinstance(obj, io.IOBase):
            # Make sure to hash entire file
            obj.seek(0)
            while True:
                data = obj.read(32768)
                if not data:
                    break
                hasher.update(data)
        elif isinstance(obj, list):
            hasher.update(b'_||LIST||_')
            for element in obj:
                hashsum(element, hasher=hasher)
                hasher.update(b'_|ENDELEM|_')
            hasher.update(b'_||ENDLIST||_')
        elif isinstance(obj, tuple):
            hasher.update(b'_||TUPLE||_')
            for element in obj:
                hashsum(element, hasher=hasher)
                hasher.update(b'_|ENDELEM|_')
            hasher.update(b'_||ENDTUPLE||_')
        elif isinstance(obj, dict):
            hasher.update(b'_||DICT||_')
            for key in sorted(obj.keys()):
                hashsum(key, hasher=hasher)
                hasher.update(b'_|ENDKEY|_')
                hashsum(obj[key], hasher=hasher)
                hasher.update(b'_|ENDVALUE|_')
            hasher.update(b'_||ENDDICT||_')
        elif isinstance(obj, set):
            hasher.update(b'_||SET||_')
            for element in sorted(obj):
                hashsum(element, hasher=hasher)
                hasher.update(b'_|ENDELEM|_')
            hasher.update(b'_||ENDSET||_')
        else:
            hasher.update(pickle.dumps(obj))

    return hasher.hexdigest()


def md5_checksum(filepath):
    """
    Generate the md5 checksum of a file

    :param filepath: path of the file(s) to checksum
    :type filepath: str, list
    :return: the checksum
    :rtype: str
    """
    return checksum(filepath)


def sha1_checksum(filepath):
    """
    Generate the sha1 checksum of a file

    :param filepath: path of the file(s) to checksum
    :type filepath: str, list
    :return: the checksum
    :rtype: str
    """
    return checksum(filepath, 'sha1')
