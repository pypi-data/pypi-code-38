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
import os
import sys
import hashlib
import fnmatch


CHUNK_SIZE = 512


def hashfile(filename, hash_function):
    with open(filename, 'rb') as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0, os.SEEK_SET)
        while f.tell() < size:
            hash_function.update(f.read(CHUNK_SIZE))


def hashfiles(filename, hash_algo=hashlib.md5, pattern='*.py'):
    """
    hashfiles returns the hex digest of all files contained in the directory -
    specified by 'filename' including its subdirectories, links excluded.
    [hash_algo] is an hash algorithm from hashlib e.g. hashlib.md5.
    """
    assert(os.path.exists(filename))
    hash_function = hash_algo()

    if os.path.isdir(filename):
        for root, dirs, files in os.walk(filename):
            for name in fnmatch.filter(files, pattern):
                try:
                    hashfile(os.path.join(root, name), hash_function)
                except (IOError, OSError):
                    pass
    elif os.path.isfile(filename):
        hashfile(filename, hash)
    else:
        assert(False)
    return hash.hexdigest()


def main():
    """
    Main function.
    Requires 1 command line arguments.
        filename path

    Produces hexadecimal hash string of python files under SY_PYTHON_SUPPORT.
    """
    sys.stdout.write(hashfiles(sys.argv[1]))


if __name__ == '__main__':
    main()
