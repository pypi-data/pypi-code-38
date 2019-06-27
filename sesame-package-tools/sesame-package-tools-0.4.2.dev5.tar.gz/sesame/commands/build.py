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

import sesame

from colorama import Fore, Back, Style

def build_cmd(args):
    """Build a recipe"""
    parser = argparse.ArgumentParser(description=build_cmd.__doc__, prog='sesame build')
    parser.add_argument('--upload', action='store_true', default=False)
    parser.add_argument("--user", '-u', help="Conan user that the package will be created under.", default='sesame')
    parser.add_argument("--channel", '-c', help="Conan channel that the package will be created under.", default='testing')

    parser.add_argument("--default-profile", help="Uses sesame-default.profile instead of i.e. sesame-base-windows.profile", default=False, action="store_true")
    parser.add_argument("--build-missing", help="Build missing deps", default=False, action="store_true")

    parser.add_argument("--android", help="builds for android", default=False, action="store_true")
    parser.add_argument("--emscripten", help="builds for emscripten", default=False, action="store_true")
    parser.add_argument("--linux", help="builds for linux", default=False, action="store_true")
    parser.add_argument("--macos", help="builds for macOS", default=False, action="store_true")
    parser.add_argument("--uwp", help="builds for UWP", default=False, action="store_true")
    parser.add_argument("--windows", help="builds for windows", default=False, action="store_true")

    args = parser.parse_args(*args)
    _build(args)

def _build(args):
    target_path = os.path.expanduser('~/.conan/settings.yml')
    if os.path.exists(target_path):
        os.remove(target_path)
    shutil.copy(sesame.get_conan_settings_yml_path(), target_path)

    common_conan_env = {
        'CONAN_USERNAME': f'{args.user}',
        'CONAN_CHANNEL': f'{args.channel}',

        'CONAN_PIP_PACKAGE': 'False',
        'CONAN_BUILD_TYPES': 'Debug,RelWithDebInfo',
        'CONAN_STABLE_BRANCH_PATTERN': ' '
    }

    upload_conan_env = {}
    if args.upload:
        upload_conan_env = {
            'CONAN_LOGIN_USERNAME': 'orhun',
            'CONAN_UPLOAD': 'https://api.bintray.com/conan/orhun/sesame',
            'CONAN_UPLOAD_ONLY_WHEN_STABLE': '0',
        }

    build_conan_env = {}
    if args.build_missing:
        build_conan_env = {
            'CONAN_BUILD_POLICY': 'missing'
        }

    platform_activity_map = {
        'android': args.android,
        'emscripten': args.emscripten,
        'linux': args.linux,
        'macos': args.macos,
        'uwp': args.uwp,
        'windows': args.windows
    }

    if not any(platform_activity_map.values()):
        build = {
            'Windows': 'windows',
            'Darwin': 'macos',
            'Linux': 'linux'
        }.get(platform.system())
        platform_activity_map[build] = True

    for build in platform_activity_map.items():
        name = build[0]
        active = build[1]
        if active:
            platform_conan_envs = _prepare_conan_env(args, prep_for=name)

            for platform_conan_env in platform_conan_envs:
                conan_env = {**common_conan_env, **upload_conan_env, **build_conan_env, **platform_conan_env}

                build_script = 'build.py'
                if os.path.isfile('build-sesame.py'):
                    build_script = 'build-sesame.py'
                python = {
                    'Windows': 'python',
                    'Darwin': 'python3',
                    'Linux': 'python3'
                }.get(platform.system())
                subprocess.run([python, build_script], check=True, cwd='.', env={**os.environ.copy(), **conan_env})

def _prepare_conan_env(args, prep_for):
    envs = [{}]

    if prep_for == 'android':
        host = {
            'Windows': 'windows',
            'Darwin': 'macos',
            'Linux': 'linux'
        }.get(platform.system())

        # get current clang version
        clang = f'{os.environ["ANDROID_NDK_HOME"]}/toolchains/llvm/prebuilt/{host}-x86_64/bin/clang'
        output = subprocess.check_output([clang, '--version']).decode()
        p = re.compile(r'clang version (\d).(\d).(\d)')
        m = p.search(output)

        envs[0]['SESAME_BUILD_FOR'] = prep_for
        envs[0]['CONAN_CLANG_VERSIONS'] = '8.0'
        envs[0]['CONAN_ARCHS'] = 'armv8,x86'
        envs[0]['CONAN_BASE_PROFILE'] = sesame.get_conan_profiles_path('sesame-base-android-25.profile')

        envs.append({})
        envs[1]['SESAME_BUILD_FOR'] = prep_for
        envs[1]['CONAN_CLANG_VERSIONS'] = '8.0'
        envs[1]['CONAN_ARCHS'] = 'armv8,x86'
        envs[1]['CONAN_BASE_PROFILE'] = sesame.get_conan_profiles_path('sesame-base-android-26.profile')

        envs.append({})
        envs[2]['SESAME_BUILD_FOR'] = prep_for
        envs[2]['CONAN_CLANG_VERSIONS'] = '8.0'
        envs[2]['CONAN_ARCHS'] = 'armv8,x86'
        envs[2]['CONAN_BASE_PROFILE'] = sesame.get_conan_profiles_path('sesame-base-android-28.profile')
    elif prep_for == 'emscripten':
        envs[0]['CONAN_CLANG_VERSIONS'] = '7.0'
        envs[0]['CONAN_ARCHS'] = 'llvmbc'
    elif prep_for == 'linux':
        envs[0]['CONAN_CLANG_VERSIONS'] = '8.0'
        envs[0]['CONAN_ARCHS'] = 'x86_64'
        envs[0]['CONAN_BASE_PROFILE'] = sesame.get_conan_profiles_path('sesame-base-linux.profile')
    elif prep_for == 'macos':
        envs[0]['CONAN_APPLE_CLANG_VERSIONS'] = '10.0'
        envs[0]['CONAN_ARCHS'] = 'x86_64'
        envs[0]['CONAN_BASE_PROFILE'] = sesame.get_conan_profiles_path('sesame-base-macos.profile')
    elif prep_for == 'uwp':
        envs[0]['CONAN_VISUAL_VERSIONS'] = '16'
        envs[0]['CONAN_VISUAL_RUNTIMES'] = 'MD, MDd'
        envs[0]['CONAN_ARCHS'] = 'x86_64'
        envs[0]['CONAN_BASE_PROFILE'] = sesame.get_conan_profiles_path('sesame-base-uwp.profile')
    elif prep_for == 'windows':
        envs[0]['CONAN_VISUAL_VERSIONS'] = '16'
        envs[0]['CONAN_VISUAL_RUNTIMES'] = 'MD, MDd'
        envs[0]['CONAN_ARCHS'] = 'x86_64'
        envs[0]['CONAN_BASE_PROFILE'] = sesame.get_conan_profiles_path('sesame-base-windows.profile')

    return envs
