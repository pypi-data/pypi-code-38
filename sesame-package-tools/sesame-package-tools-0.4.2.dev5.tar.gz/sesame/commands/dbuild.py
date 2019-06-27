# -*- coding: utf-8 -*-

import argparse
import configparser
import os
import shutil
import subprocess
import platform
import re

import docker
import vswhere
import psutil

import sesame

from colorama import Fore, Back, Style

def dbuild_cmd(args):
    """Build a recipe in docker"""
    parser = argparse.ArgumentParser(description=dbuild_cmd.__doc__, prog='sesame build')
    parser.add_argument("--user", '-u', help="Conan user that the package will be created under.", default='sesame')
    parser.add_argument("--channel", '-c', help="Conan channel that the package will be created under.", default='testing')

    parser.add_argument("--android", help="builds for android", default=False, action="store_true")
    parser.add_argument("--emscripten", help="builds for emscripten", default=False, action="store_true")
    parser.add_argument("--windows", help="builds for windows", default=False, action="store_true")
    parser.add_argument("--uwp", help="builds for windows", default=False, action="store_true")

    args = parser.parse_args(*args)
    _build(args)

def _is_docker_running():
    return True
    service = None
    try:
        service = psutil.win_service_get('docker')
        service = service.as_dict()
    except Exception:
        pass

    return service is not None

def _build(args):
    if args.android:
        docker_image = 'sesameorhun/android-devel'
        sesame_mount = '/tmp/sesame'
        recipe_mount = '/tmp/recipe'
        result_mount = '/tmp/result'
        conan_user_home = '~/'
        command = f'/bin/bash -c "cd {recipe_mount} && sesame build --android --user {args.user} --channel {args.channel} && conan remove */*@* --builds --src --force && cp -r ~/.conan {result_mount}"'
    elif args.emscripten:
        docker_image = 'sesameorhun/emscripten-devel'
        sesame_mount = '/tmp/sesame'
        recipe_mount = '/tmp/recipe'
        result_mount = '/tmp/result'
        conan_user_home = '~/'
        command = f'/bin/bash -c "cd {recipe_mount} && sesame build --emscripten --user {args.user} --channel {args.channel} && conan remove */* --builds --src --force && cp -r ~/.conan {result_mount}"'
    elif args.windows:
        docker_image = 'sesameorhun/windows-devel'
        sesame_mount = 'C:\\sesame'
        recipe_mount = 'C:\\recipe'
        result_mount = 'C:\\result'
        conan_user_home = 'C:\\conan'
        command = f'powershell -command cd sesame ; pip install . ; cd ..\\\\recipe ; sesame build --windows --user {args.user} --channel {args.channel} ; conan remove --builds --src --force * ; robocopy "$env:USERPROFILE\\.conan" "c:\\result" /MIR /J /MOVE'
    elif args.uwp:
        docker_image = 'sesameorhun/windows-devel'
        sesame_mount = 'C:\\sesame'
        recipe_mount = 'C:\\recipe'
        result_mount = 'C:\\result'
        conan_user_home = 'C:\\conan'
        command = f'powershell -command cd sesame ; pip install . ; cd ..\\\\recipe ; sesame build --uwp --user {args.user} --channel {args.channel} ; conan remove --builds --src --force * ; robocopy "$env:USERPROFILE\\.conan" "c:\\result" /MIR /J /MOVE'

    is_docker_running = _is_docker_running()

    if is_docker_running:
        try:
            print(Style.BRIGHT + Fore.LIGHTWHITE_EX + 'Starting docker...')

            docker_client = docker.from_env(version='auto')
            container = docker_client.containers.run(
                image=docker_image,
                command=command,
                volumes={
                    # sesame.get_setup_path(): {
                    #     'bind': sesame_mount,
                    #     'mode': 'rw'
                    # },
                    os.getcwd(): {
                        'bind': recipe_mount,
                        'mode': 'rw'
                    },
                    'G:\\Devel\\projects\\sesame2\\.build': {
                        'bind': result_mount,
                        'mode': 'rw'
                    }
                },
                environment={
                    'CONAN_USER_HOME_SHORT': 'None',
                    'CONAN_TEMP_TEST_FOLDER': 'False'
                },
                detach=True,
                auto_remove=True,
                stdout=True,
                stderr=True)

            for log in container.logs(stream=True):
                print(log.decode().rstrip('\r\n'))
        except Exception as e:
            print(Style.BRIGHT + Fore.LIGHTRED_EX + str(e))
    else:
        print(Style.BRIGHT + Fore.LIGHTRED_EX + "Docker is not running.")
