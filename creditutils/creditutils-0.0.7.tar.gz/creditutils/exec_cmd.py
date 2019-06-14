# -*- coding:UTF-8 -*-

import os
import subprocess
import re
import chardet.universaldetector as detector_
import creditutils.system_util as system_util


def run_cmd_with_cmd_str_and_decode_gracefully(cmd_str, print_flag=False, capture_stdout=True):
    if capture_stdout:
        p = subprocess.Popen(cmd_str, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    else:
        p = subprocess.Popen(cmd_str, shell=True, stderr=subprocess.STDOUT)

    if capture_stdout:
        encoding = None
        detector = detector_.UniversalDetector()

        result = bytearray()
        for line in p.stdout.readlines():
            result.extend(line)

            if not encoding:
                detector.feed(line)
                if detector.done:
                    encoding = detector.result['encoding']

        rtn_val = p.wait()
        detector.close()

        # print(detector.result)

        if not encoding:
            encoding = detector.result['encoding']
            if not encoding:
                encoding = system_util.get_system_encoding()
                # print('encoding: ' + encoding)

        rtn_str = ''
        if result:
            rtn_str = result.decode(encoding)

        if print_flag:
            print(rtn_str)
    else:
        rtn_val = p.wait()
        rtn_str = None

    return rtn_val, rtn_str


def run_cmd_for_stdout_ignores_exit_code(cmd_str, print_flag=False):
    return run_cmd_with_cmd_str_and_decode_gracefully(cmd_str, print_flag)[1]


def run_cmd_with_system_in_specified_dir(dst_dir, cmd_str, print_flag=False):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(dst_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)
        if print_flag:
            print(cmd_str)

        os.system(cmd_str)
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


def run_cmd_for_code_in_specified_dir(dst_dir, cmd_str, print_flag=False):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(dst_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)
        if print_flag:
            print(cmd_str)

        cp = subprocess.run(cmd_str, check=True, shell=True)
        return cp.returncode
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


def run_cmd_for_output_in_specified_dir(dst_dir, cmd_str, print_flag=False):
    try:
        curr_dir = os.getcwd()
        dst_dir = os.path.abspath(dst_dir)
        if curr_dir != dst_dir:
            os.chdir(dst_dir)
        if print_flag:
            print(cmd_str)

        cp = subprocess.run(cmd_str, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        return cp.stdout
    finally:
        if curr_dir != dst_dir:
            os.chdir(curr_dir)


def run_cmd_and_check_output_in_specified_dir(dst_dir, cmd_str, result_re, print_flag=False):
    result = run_cmd_for_output_in_specified_dir(dst_dir, cmd_str, print_flag)
    match = re.search(result_re, result, flags=re.IGNORECASE)
    if not match:
        raise Exception('run cmd failed!')
    return True
