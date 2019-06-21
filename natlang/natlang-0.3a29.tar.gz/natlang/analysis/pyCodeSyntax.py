from __future__ import absolute_import
from subprocess import Popen, PIPE
import argparse


def check_file_py2(fpath, checker_path='syntax_checker', python_path='python2'):
    process = Popen([python_path, checker_path, fpath], stdout=PIPE)
    output, err = process.communicate()
    exit_code = process.wait()
    if exit_code == 0:
        return eval(output)
    else:
        raise RuntimeError(err)


def check_file_py3(fpath, checker_path='syntax_checker', python_path='python3'):
    process = Popen([python_path, checker_path, fpath], stdout=PIPE)
    output, err = process.communicate()
    exit_code = process.wait()
    if exit_code == 0:
        return eval(output)
    else:
        raise RuntimeError(err)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='check syntax of python code')
    parser.add_argument('code_file')
    args = parser.parse_args()

    py2_results = check_file_py2(args.code_file)
    py3_results = check_file_py3(args.code_file)
