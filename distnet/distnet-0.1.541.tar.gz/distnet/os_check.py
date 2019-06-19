"""
    Utilities for OS level filesystem checks.
"""
import re
import sys
import subprocess

import os.path as osp

# TODO: refactor
# idea 1: into check_path and check_files
# idea 2:
def os_filesystem_check(directory, files_list, filetype_pattern):
    """
        Checks if file types match pattern.
        Input:
            directory = str : path to directory, eg. "/proc/net"
            files_list = list : list of str, eg. "["f1", "f2"]"
            filetype_pattern = str: eg. " empty$"
    """
    passed = True

    # TODO: import struct?
    class CHECK_RESULTS:
        """
            ANSI escape sequences for colored output.
        """
        OK = '\033[92m OK \033[0m'
        FAIL = '\033[91m FAIL \033[0m'


    cdirpath = directory.rstrip('/') + '/'

    flist_format = []
    for file_name in files_list:
        flist_format.append(cdirpath + file_name.strip('/'))

    # directory check, don't check files if this fails
    sys.stdout.write('Checking path: ' + cdirpath.ljust(24) + ' ... ')
    if not osp.exists(cdirpath.rstrip('/')):
        # unlike isdir(), exists() fails with trailing '/'
        sys.stdout.write(CHECK_RESULTS.FAIL + '\n')
        sys.stderr.write('Path ' + cdirpath + ' does not exist or not accessible. Check OS.\n')
        return not passed
    elif not osp.isdir(cdirpath):
        sys.stdout.write(CHECK_RESULTS.FAIL + '\n')
        sys.stderr.write('Path ' + cdirpath + ' is not a directory. \n')
        return not passed
    else:
        sys.stdout.write(CHECK_RESULTS.OK + '\n')

    # iterate files_list, continue on verification fail with continue kw
    # files_list will all be checked under cdirpath
    for file_n in flist_format:
        cfile_path = file_n
        r_status = CHECK_RESULTS.OK

        # file in question
        sys.stdout.write('Checking file: ' + cfile_path.ljust(24) + ' ... ')

        # file type matches pattern, see Documentation/Popen/file.c
        p_proc = subprocess.Popen(['file', '-E', cfile_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subp_out, subp_err = p_proc.communicate()

        subp_out = subp_out.decode('utf-8')
        subp_err = subp_err.decode('utf-8')

        if p_proc.returncode != 0:
            passed = False
            r_status = CHECK_RESULTS.FAIL
            sys.stdout.write(r_status + '\n')
            sys.stderr.write('There were errors verifying type of ' + cfile_path + ' ... \n' + subp_err + '\n')
            continue

        pattern_filetype = re.compile(r'' + str(filetype_pattern))

        #DEBUG
        # print(subp_out)
        # print(type(subp_out))
        #/dEBUG


        regex_result = pattern_filetype.search(str(subp_out))
        if not regex_result:
            passed = False
            r_status = CHECK_RESULTS.FAIL
            sys.stdout.write(r_status + '\n')
            sys.stderr.write('File type of ' + cfile_path + ' does not correspond. \n')
            continue

        # depth level 0, no if statement passed
        sys.stdout.write(r_status + '\n')

    return passed
