"""
This will check validity of compressed files.
Currently it only works for bz.
"""
import os
import pandas as pd
import sys
import progressbar


def get_dir_file_list(data_dir):
    # data_dir = '../raw data'
    dir_list = os.listdir(data_dir)
    return dir_list, data_dir


def try_to_read_files(f_list, files_location):
    for file_name in progressbar.progressbar(f_list):
            try:
                pd.read_csv(os.path.join(files_location, file_name), compression='gzip')
            except Exception as e:
                print(f'\nError in {file_name}: {e}')


if __name__ == '__main__':
    cmd_args = sys.argv
    if len(sys.argv) != 2:
        print('Usage: python archive_validity_checker.py path_to_files')
        sys.exit()
    files_loc = cmd_args[1]
    # list files
    file_list, dir_location = get_dir_file_list(files_loc)

    # try to read files in order to check validity
    try_to_read_files(file_list, dir_location)
