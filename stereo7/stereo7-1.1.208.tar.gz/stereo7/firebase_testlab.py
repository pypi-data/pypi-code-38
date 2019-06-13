import re
import subprocess
from random import randint

import fileutils
from project import Project


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
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
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

    device = devices[randint(0, len(devices) - 1)]
    device_id = device[0]
    os_sdk_id = device[1][randint(0, len(device[1]) - 1)]
    os_sdk_id = str(os_sdk_id)
    print('Run robo-test:')
    # print('Run robo-test on device: %s OS Version: %s (supported OS\'s %s)' % (device_id, os_sdk_id, device[1]))

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
        # '--device-ids',
        # device_id,
        # '--os-version-ids',
        # os_sdk_id,
    ]
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    print 'Return Code:', process.returncode
    print 'Out:\n', out
    print 'Err:\n', err

    return process.returncode == 0


def main(apk_path):
    app_gradle_path = '{}/proj.android/app/build.gradle'.format(fileutils.root_dir)

    app_info = get_app_info(app_gradle_path)
    devices = get_devices_list(app_info)
    result = run_robo_tests(devices, apk_path)
    exit(0 if result else 1)


if __name__ == '__main__':
    fileutils.root_dir = '/work/td_core/projects/syndicate-4'
    apk = '/users/stereo7/Downloads/syndicate4-release.apk'
    main(apk)
