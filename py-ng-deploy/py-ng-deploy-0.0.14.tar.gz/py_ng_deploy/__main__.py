import os
import sys
import json
import shutil

from colorama import Fore, Style
from pathlib import Path
from py_ng_deploy import __version__
from py_ng_deploy import py_ng_build
from py_ng_deploy import py_ng_upload

RCFILE = '.pyngdeployrc'


def main():
    if len(sys.argv) == 1:
        print(f'{Fore.BLUE}                         _____             _')
        print(f'{Fore.BLUE}                        |  __ \\           | |')
        print(f'{Fore.BLUE} _ __  _   _ _ __   __ _| |  | | ___ _ __ | | ___  '
              f'_   _')
        print(
            f'{Fore.BLUE}| \'_ \\| | | | \'_ \\ / _` | |  | |/ _ \\ \'_ \\| |/'
            f' _ \\| | | |')
        print(f'{Fore.BLUE}| |_) | |_| | | | | (_| | |__| |  __/ |_) | | (_) |'
              f' |_| |')
        print(f'{Fore.BLUE}| .__/ \\__, |_| |_|\\__, |_____/ \\___| .__/|_|\\_'
              f'__/ \\__, |')
        print(f'{Fore.BLUE}| |     __/ |       __/ |           | |            '
              f' __/ |')
        print(f'{Fore.BLUE}|_|    |___/       |___/            |_|            '
              f'|___/')
        print(f'{Fore.BLUE}Version: {__version__}\n')
        print(f'{Fore.BLUE}Usage:')
        print(f'{Fore.BLUE}  pyngDeploy (init | prod | dev) [--hash | '
              f'--restore]', Style.RESET_ALL)
        if not Path('.pyngdeployrc').is_file():
            print(f'\n{Fore.RED}[!] The actual folder seems not to be an '
                  f'angular project or uninitialized pyngDeploy project, '
                  f'check before try to upload/restore', Style.RESET_ALL)
        sys.exit()
    elif len(sys.argv) > 1:
        if not initialize(sys.argv[1], len(sys.argv)):
            if len(sys.argv) == 2 or (
                    len(sys.argv) > 2 and
                    not restoring(sys.argv[1], sys.argv[2], True)
                    ):
                result = py_ng_build.build(sys.argv[1])
                if result.returncode == 0 and len(sys.argv) > 2:
                    py_ng_build.gen_hash(sys.argv[2], json_find())
                py_ng_upload.upload(sys.argv[1], json_find(), False,
                                    os.name == 'posix')
            else:
                if restoring(sys.argv[1], sys.argv[2], False):
                    return
                else:
                    print(f'{Fore.CYAN}[pyngDeploy]:: Nothing to do',
                          Style.RESET_ALL)
                    sys.exit()
                    # spCallParams = []
                    # if os.name == 'nt':
                    #     spCallParams.append('bash.exe')
                    #     spCallParams.append('-c')
                    # spCallParams.append('python')
                    # spCallParams.append('upload.py')

                    # result = sp.call(spCallParams, stderr=sp.DEVNULL)
                    # if result == 0:
                    #     print('Process complete :D')
                    # else:
                    #     print('Something fails :O')


def initialize(init_keyword, argv_length):
    if argv_length > 2:
        print(f'{Fore.YELLOW}[pyngDeploy]:: [!] Invalid arguments',
              Style.RESET_ALL)
    elif init_keyword == 'init':
        rc_file = Path(RCFILE)
        src_rcfile = f'{os.path.dirname(os.path.abspath(__file__))}/{RCFILE}'
        if not rc_file.is_file():
            shutil.copy2(src_rcfile, RCFILE)
            print(f'{Fore.CYAN}[pyngDeploy]:: Configuration file created')
            print(f'{Fore.CYAN}[pyngDeploy]:: Please edit the file {RCFILE} '
                  f'with the given keys', Style.RESET_ALL)
        else:
            print(f'{Fore.YELLOW}[pyngDeploy]:: {RCFILE} file already exists')
            print(f'{Fore.YELLOW}[pyngDeploy]:: Verify it and their config '
                  f'keys', Style.RESET_ALL)
        return True
    else:
        return check_rcfile()


def check_rcfile():
    if Path(RCFILE).is_file():
        return False
    else:
        sys.exit(f'{Fore.RED}[pyngDeploy]:: [!] {RCFILE} not found, please '
                 f'init project {Style.RESET_ALL}')


def json_find():
    json_file = {}
    try:
        with open('angular.json') as json_config:
            json_file = json.load(json_config)
    except FileNotFoundError:
        sys.exit(f'{Fore.RED}[pyngDeploy]:: [!] angular.json file not found,'
                 f'{Fore.RED} verify that you are in an angular project folder'
                 f' {Style.RESET_ALL}')
    return iter_finder(json_file, 'outputPath')


def iter_finder(input_dict, key):
    if key in input_dict:
        return input_dict[key]
    for value in input_dict.values():
        if isinstance(value, dict):
            res = iter_finder(value, key)
            if res is not None:
                return res
    return None


def restoring(environment, restore_flag, validation):
    if environment != 'init' and restore_flag == '--restore':
        if not validation:
            print(f'{Fore.YELLOW}[pyngDeploy]:: [!] Restoring Last Backup!',
                  Style.RESET_ALL)
            py_ng_upload.upload(environment, json_find(), True,
                                os.name == 'posix')
        return True
    else:
        return False


if __name__ == '__main__':
    main()
