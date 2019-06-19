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
import json
import glob
import fnmatch


class FilenameSerializer(object):
    def __init__(self):
        pass

    def serialize_filenames(self, fq_outfilename, fq_filenames):
        with open(fq_outfilename, 'w') as f:
            f.write(json.dumps(fq_filenames))

    def deserialize_filenames(self, fq_infilename):
        filenames = None
        with open(fq_infilename, 'r') as f:
            filenames = json.loads(f.read())

        return filenames


class FilenameRetriever(object):
    def __init__(self, directory, ext):
        self._directory = directory
        self._ext = ext

    def filenames(self, fully_qualified=True, recursive=False,
                  max_length=None, max_length_msg=''):
        if not recursive:
            return self._nonrecursive_fq_filenames(fully_qualified)
        else:
            return self._recursive_fq_filenames(
                fully_qualified, max_length, max_length_msg)

    def _nonrecursive_fq_filenames(self, fully_qualified=True):
        if not self._ext:
            return []
        not_fq_filenames = glob.glob1(self._directory, self._ext)
        filenames = not_fq_filenames
        if fully_qualified:
            fq_filenames = [os.path.join(self._directory, filename)
                            for filename in not_fq_filenames]
            filenames = fq_filenames
        return filenames

    def _recursive_fq_filenames(
            self, fully_qualified=True, max_length=None, max_length_msg=''):
        matches = []
        for i, (root, dirnames, filenames) in enumerate(
                os.walk(self._directory)):
            if max_length:
                if len(matches) >= max_length:
                    return matches[:max_length]
                elif i > max_length:
                    return matches + [max_length_msg]

            for filename in fnmatch.filter(filenames, self._ext):
                if fully_qualified:
                    matches.append(os.path.normpath(
                        os.path.join(root, filename)))
                else:
                    matches.append(os.path.normpath(filename))
        return matches
