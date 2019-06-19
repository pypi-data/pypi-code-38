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
"""Module providing functions for creating unique filenames."""
import os


def digits_required(length):
    """
    Returns the number of digits that would be needed to represent 'length'
    number of elements.
    """
    digits = 0
    while 10 ** digits <= length:
        digits += 1
    return digits


def order_filenames(filepath_list):
    """
    Prefixes the filenames with a numeric identifier followed by _.
    The order in the returned output list matches its alphabetic ordering.
    The length of the returned list matches the length of the input list.

    >>> order_filenames([])
    []

    >>> order_filenames(['/path/file'])
    ['/path/0_file']

    >>> order_filenames(['file'] * 3)
    ['0_file', '1_file', '2_file']

    >>> ordered_list = order_filenames(['file'] * 10)

    >>> ordered_list[:5]
    ['00_file', '01_file', '02_file', '03_file', '04_file']

    >>> ordered_list[5:]
    ['05_file', '06_file', '07_file', '08_file', '09_file']

    >>> len(set(order_filenames(['file'] * 1000)))
    1000
    """
    digits = digits_required(len(filepath_list))
    split_list = [os.path.split(filepath) for filepath in filepath_list]

    return [os.path.join(dirpath, "{0:0{1}d}_{2}".format(i, digits, filename))
            for i, (dirpath, filename) in enumerate(split_list)]


def unique_filenames(filepath_list):
    """
    Returns a list of unique filenames.
    Here unique means that the filepath is unique in the list.
    The filenames are obtained by adding a numeric suffix to the filepaths.
    Suffixes are only added when there are conflicting names.

    >>> unique_filenames([])
    []

    >>> unique_filenames(['/path/first.txt', '/path/second.txt'])
    ['/path/first.txt', '/path/second.txt']

    >>> unique_filenames(['/path/first.txt', '/path/first.txt'])
    ['/path/first_0.txt', '/path/first_1.txt']

    >>> unique_list = unique_filenames(['file'] * 10)

    >>> unique_list[:5]
    ['file_00', 'file_01', 'file_02', 'file_03', 'file_04']

    >>> unique_list[5:]
    ['file_05', 'file_06', 'file_07', 'file_08', 'file_09']

    >>> len(set(unique_filenames(['file'] * 1000)))
    1000
    """
    filepath_set = set(filepath_list)
    if len(filepath_list) == len(filepath_set):
        # The filepaths in the filepath_list are already unique.
        return filepath_list
    else:
        # The filepaths in the filepath_list are not unique.
        filepath_dict = {}
        digits = digits_required(len(filepath_list))
        split_list = [os.path.splitext(filepath) for filepath in filepath_list]
        unique_list = []

        for filepath, (base, ext) in zip(filepath_list, split_list):
            index = 0
            try:
                index = filepath_dict[filepath]
                filepath_dict[filepath] += 1
            except KeyError:
                filepath_dict[filepath] = 1

            unique_list.append(
                "{0}_{1:0{2}d}{3}".format(base, index, digits, ext))

        return unique_list


def unused_filenames(filepath_list):
    """
    Returns a list of what is hoped to be unused filenames.
    The files will be created on disk to prevent race conditions.
    There is no guarantee that the files will be not be overwritten.

    >>> import os
    >>> import tempfile
    >>> import shutil

    >>> tempdir = tempfile.mkdtemp(prefix='filenames_')
    >>> filename_list = ['file.txt'] * 4
    >>> filename_list
    ['file.txt', 'file.txt', 'file.txt', 'file.txt']
    >>> filepath_list = [os.path.join(tempdir, name) for name in filename_list]
    >>> unused_list = unused_filenames(filepath_list)
    >>> [os.path.split(filepath)[1] for filepath in unused_list]
    ['file.txt', 'file_0.txt', 'file_00.txt', 'file_000.txt']
    >>> for filepath in unused_list:
    ...     with open(filepath, 'w'):
    ...         pass
    >>>
    >>> shutil.rmtree(tempdir)
    >>>
    """
    unused_list = []
    file_list = []

    for filepath in filepath_list:
        base, ext = os.path.splitext(filepath)
        count = 0
        testpath = filepath

        try:
            fsock = os.open(testpath, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        except OSError:
            fsock = None

        while not fsock:
            testpath = "{0}_{1:0{2}d}{3}".format(base, 0, count, ext)
            count += 1
            try:
                fsock = os.open(testpath, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            except OSError:
                fsock = None

        file_list.append(fsock)
        unused_list.append(testpath)

    for fsock in file_list:
        os.close(fsock)

    return unused_list


def build_export_filenames(outdir, filename_list, order, overwrite):
    """
    Returns a list of filepaths that can be used to write to disk.

    Assuming that the filepaths in filepath_list.
    filename_list is typically built with build_filename_identifier and
    build_filename_postfix functions.

    When 'order' is True the filenames will be prefixed by a numeric
    combination to preserve the order of the filename_list.

    When 'overwrite' is False, '0' will be appended to the filename to avoid
    name clashes with the files existing on disk.
    The files will also be created so that simultanious calls will not
    overwrite each other's files.
    """
    if order:
        filename_list = order_filenames(filename_list)
    else:
        filename_list = unique_filenames(filename_list)

    filepath_list = [os.path.join(outdir, filename)
                     for filename in filename_list]
    if not overwrite:
        export_list = unused_filenames(filepath_list)
    else:
        export_list = filepath_list

    return export_list
