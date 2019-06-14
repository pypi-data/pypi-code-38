#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import subprocess
import platform
from random import randint

import fileutils
from project import Project
from management import Slack


message_with_insufficient_test_quota = '''
Упс. Превышена квота на количество тестовых запусков в Firebase TestLab.
Придется проверять запуск apk вручную.
Проект: *{project_name}*
'''


def get_app_info(app_gradle_path):
    # data = open(app_gradle_path).read()
    # min_sdk_version = re.findall(r'minSdkVersion (\d+)', data)[0]
    # print('  - Min SDK Version: ', min_sdk_version)
    # return min_sdk_version

    # TODO
    return 26


def get_devices_list(app_info):
    arguments = [
        'gcloud',
        'firebase',
        'test',
        'android',
        'models',
        'list',
    ]
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=(platform.system() == "Windows"))
    out, err = process.communicate()
    print(out)
    # matches = re.findall(r'(\w+).+ \d+ x \d+.+\s([\d,]+)', out)
    matches = re.findall(r'(\w+).+PHYSICAL.+ \d+ x \d+.+\s([\d,]+)', out)
    devices = []
    for match in matches:
        device_id = match[0]
        try:
            sdks = [int(x) for x in match[1].split(',')]
            sdks = list(filter(lambda x: x >= app_info, sdks))
        except ValueError:
            continue
        if sdks:
            devices.append((device_id, sdks))
    return devices


def run_robo_tests(devices, path_to_apk):
    arguments = [
        'gcloud',
        'firebase',
        'test',
        'android',
        'run',
        '--type',
        'robo',
        '--app',
        path_to_apk,
    ]

    device_id = 'Any'
    os_sdk_id = 'Any'
    os_sdk_id

    if devices is not None:
        device = devices[randint(0, len(devices) - 1)]
        device_id = device[0]
        os_sdk_id = device[1][randint(0, len(device[1]) - 1)]
        os_sdk_id = str(os_sdk_id)

        arguments.extend([
            '--device-ids',
            device_id,
            '--os-version-ids',
            os_sdk_id,
        ])
    print('Run robo-test on device: %s OS Version: %s' % (device_id, os_sdk_id))

    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=(platform.system() == "Windows"))
    out, err = process.communicate()
    print 'Return Code:', process.returncode
    print 'Out:\n', out
    print 'Err:\n', err

    if process.returncode == 1 and devices is not None:
        return run_robo_tests(None, path_to_apk)

    return process.returncode


def main(apk_path):
    app_gradle_path = '{}/proj.android/app/build.gradle'.format(fileutils.root_dir)

    app_info = get_app_info(app_gradle_path)
    devices = get_devices_list(app_info)
    result = run_robo_tests(devices, apk_path)
    if result == 1:
        message = message_with_insufficient_test_quota.format(project_name=Project.instance.app_bundle_name)
        Slack().send_message('#stores', message, 'Сборщик и тестировщик Android билдов')
        exit(0)
    exit(result)


if __name__ == '__main__':
    fileutils.root_dir = '/work/td_core/projects/syndicate-4'
    apk = '/users/stereo7/Downloads/syndicate4-release.apk'
    main(apk)
