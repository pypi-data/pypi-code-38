"""fast_package_file
https://github.com/Kataiser/fast-package-file
https://fast-package-file.readthedocs.io/en/latest/
"""

__author__ = "Kataiser (https://github.com/Kataiser)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2019 Kataiser (https://github.com/Kataiser)"
__license__ = "MIT"

import gzip
import json
import os
import sys
import time
import zlib

try:
    import tqdm  # a neat progress bar
except ImportError:
    tqdm = None


class PackagedDataFile:
    def __init__(self, data_file_path: str):
        # load and parse file locations (indices?) header in init in order to not do so each time a file is loaded
        self.__data_file_path_ = data_file_path

        if not os.path.exists(self.__data_file_path_):  # check if file exists
            raise PackageDataError("{} doesn't seem to exist".format(self.__data_file_path_))

        if not os.access(self.__data_file_path_, os.R_OK):  # check file permissions
            raise PackageDataError("Don't have read permissions for {}".format(self.__data_file_path_))

        with open(self.__data_file_path_, 'rb') as data_file_init:
            self.__loc_data_length = int.from_bytes(data_file_init.read(8), byteorder='little')  # read header length
            if self.__loc_data_length < 0 or self.__loc_data_length > 1000000000000:  # 1 TB seems to be a reasonable limit
                raise PackageDataError("{} is corrupted or malformed (header length is {})".format(self.__data_file_path_, self.__loc_data_length))

            loc_data_gz = data_file_init.read(self.__loc_data_length)  # read the compressed header

            try:
                loc_data_raw = gzip.decompress(loc_data_gz)  # decompress
                self.__loc_data = json.loads(loc_data_raw)  # and parse
            except (zlib.error, json.decoder.JSONDecodeError) as e:
                raise PackageDataError("{} is corrupted or malformed ({} {})".format(self.__data_file_path_, type(e), e))

    # load an individual file from the build
    def load(self, file: str) -> bytes:
        try:
            file_loc_data = self.__loc_data[file]  # get the file's stats: (offset, length, compressed (1 or 0), first byte, last byte)
        except KeyError:
            raise PackageDataError("{} is corrupted or malformed (file {} doesn't exist in location header)".format(self.__data_file_path_, file))

        with open(self.__data_file_path_, 'rb') as data_file:
            data_file.seek(file_loc_data[0] + self.__loc_data_length + 8)  # account for header and the length data
            data_file_raw = data_file.read(file_loc_data[1])

            # hashing is slow, so...
            if data_file_raw[0] != file_loc_data[3]:  # check if first byte matches
                raise PackageDataError("{} is corrupted or malformed (file {}'s first byte should be {}, but was loaded as {})".format(
                                       self.__data_file_path_, file, data_file_raw[0], file_loc_data[3]))
            elif data_file_raw[-1] != file_loc_data[4]:  # check if last byte matches
                raise PackageDataError("{} is corrupted or malformed (file {}'s last byte should be {}, but was loaded as {})".format(
                                       self.__data_file_path_, file, data_file_raw[-1], file_loc_data[4]))

            if file_loc_data[2] == 1:
                return gzip.decompress(data_file_raw)
            elif file_loc_data[2] == 0:
                return data_file_raw
            else:
                raise PackageDataError("{} is corrupted or malformed (file compressed state isn't 1 or 0)".format(self.__data_file_path_))


# only used when reading packages
class PackageDataError(Exception):
    pass


# build a directory and all subdirectories into a single file (this part isn't fast tbh)
def build(directory: str, target: str, compress: bool = True, keep_gzip_threshold: float = 0.98, progress_bar: bool = True):
    print(directory)

    start_time = time.perf_counter()
    loc_data_save = {}
    files_to_add = []
    current_loc = 0
    total_data_in = 0
    files_in = []
    gztemps_deleted = 0
    compressed_formats = ('dl_', '.gif', '.jpg', '.jpeg', '.bmp', '.png', '.wmf', '.mkv', '.mp4', '.wmv', '.avi', '.bik', '.flv', '.ogg', '.mpg', '.m2v', '.m4v', '.vob', '.mp3', '.aac',
                          '.wma', '.flac', '.zip', '.xap', '.rar', '.7z', '.cab', '.lzx', '.docx', '.xlsx', '.pptx', '.vssx', '.vstx', '.onepkg')  # list from CompactGUI

    for root, dirs, files in os.walk(directory):
        for filename_in in files:
            filename_in_joined = os.path.join(root, filename_in)  # prepare file list in order to have a progress bar

            if filename_in_joined.endswith('.gztemp'):  # in case packaging was cancelled
                os.remove(filename_in_joined)
                gztemps_deleted += 1
            else:
                files_in.append(filename_in_joined)

    if gztemps_deleted != 0:
        print("    Deleted {} .gztemp files".format(gztemps_deleted))

    if tqdm:
        input_iterable = tqdm.tqdm(files_in, file=sys.stdout, ncols=40, unit=' files', bar_format='    {l_bar}{bar}|', disable=not progress_bar)
    else:
        input_iterable = files_in

    for file_path in input_iterable:
        with open(file_path, 'rb') as input_file:
            input_file_data_raw = input_file.read()
            total_data_in += len(input_file_data_raw)
            is_compressed = [c_format for c_format in compressed_formats if file_path.endswith(c_format)]  # check file extension

            if compress and not is_compressed:
                input_file_data_gzip = gzip.compress(input_file_data_raw)

                if len(input_file_data_gzip) < len(input_file_data_raw) * keep_gzip_threshold:  # if compression improves file size
                    input_file_data = input_file_data_gzip
                    compressed = True
                    gz_path = '{}.gztemp'.format(file_path)  # because storing every file's data takes too much memory
                    files_to_add.append(gz_path)

                    with open(gz_path, 'wb') as temp_gz:
                        temp_gz.write(input_file_data)
                else:
                    # if compression doesn't improve file size (much)
                    input_file_data = input_file_data_raw
                    compressed = False
                    files_to_add.append(file_path)
            else:
                # skipping gzip testing because file is likely already compressed based on extension
                input_file_data = input_file_data_raw
                compressed = False
                files_to_add.append(file_path)

            file_path_short = file_path[len(directory) + len(os.sep):]  # removes some redundancy
            loc_data_save[file_path_short] = (current_loc, len(input_file_data), 1 if compressed else 0, input_file_data[0], input_file_data[-1])  # add file to header dictionary
            current_loc += len(input_file_data)  # keep track of offset

    loc_data_save_json = json.dumps(loc_data_save, separators=(',', ':')).encode('utf-8')  # convert header to binary
    loc_data_save_gz = gzip.compress(loc_data_save_json)  # and compress it
    loc_data_save_length = (len(loc_data_save_gz)).to_bytes(8, byteorder='little')  # get its length as an 8 bit binary

    with open(target, 'wb') as out_file:
        out_file.write(loc_data_save_length)  # add the header's length
        out_file.write(loc_data_save_gz)  # add the header

        for file_to_add_path in files_to_add:
            with open(file_to_add_path, 'rb') as file_to_add:  # add the files from either the original data or its .gztemp
                out_file.write(file_to_add.read())

            if file_to_add_path.endswith('.gztemp'):  # and then delete the .gztemp
                os.remove(file_to_add_path)

    # monitoring output
    duration = format(time.perf_counter() - start_time, '.2f')
    input_size = format(total_data_in / 1048576, '.2f')
    target_size = format(os.stat(target).st_size / 1048576, '.2f')
    print("    {} ({} MB, {} files) -> {} ({} MB) took {} seconds".format(directory, input_size, len(files_in), target, target_size, duration))


if __name__ == '__main__':
    pass
