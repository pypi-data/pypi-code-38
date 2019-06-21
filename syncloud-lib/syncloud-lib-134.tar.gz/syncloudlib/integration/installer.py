import time
from syncloudlib.integration.ssh import run_scp, run_ssh
from subprocess import check_output
from os.path import split
import json
import os

SNAP = 'snap'
SNAP_INSTALL = '{0} install --devmode'.format(SNAP)


def get_data_dir(app):
    return '/var/snap/{0}/common'.format(app)


def get_app_dir(app):
    return '/snap/{0}/current'.format(app)


def get_service_prefix():
    return 'snap.'


def get_ssh_env_vars(app):
    return 'SNAP={0} SNAP_COMMON={1}'.format(get_app_dir(app), get_data_dir(app))


def local_install(host, password, app_archive_path):
    run_ssh(host, 'ls -la /', password=password)
    _, app_archive = split(app_archive_path)
    run_scp('{0} root@{1}:/'.format(app_archive_path, host), password=password, retries=3)
    run_ssh(host, 'ls -la /{0}'.format(app_archive), password=password)
    run_ssh(host, '{0} /{1}'.format(SNAP_INSTALL, app_archive), password=password)


def local_remove(host, password, app):
    run_ssh(host, '{0} remove {1}'.format(SNAP, app), password=password)


def wait_for_platform_web(host):
    print(check_output('while ! nc -w 1 -z {0} 81; do sleep 1; done'.format(host), shell=True))
    print(check_output('while ! nc -w 1 -z {0} 80; do sleep 1; done'.format(host), shell=True))


def wait_for_installer(web_session, host, attempts=200, throw_on_error=False):
    is_running = True
    attempt = 0
    while is_running and attempt < attempts:
        try:
            response = web_session.get('https://{0}/rest/settings/sam_status'.format(host), verify=False)
            if response.status_code == 200:
                status = json.loads(response.text)
                is_running = status['is_running']
            else:
                if throw_on_error:
                    raise Exception("error http status code: {0}".format(response.status_code))
        except Exception, e:
            print(e.message)
            if throw_on_error:
                raise e
            
        print("attempt: {0}/{1}".format(attempt, attempts))
        attempt += 1
        time.sleep(10)
    
    if is_running:
        raise Exception("time out waiting for thr installer")


def wait_for_rest(web_session, host, url, code, attempts=10):
    def pred(resp):
        return resp.status_code == code

    wait_for_response(web_session, host, url, pred, attempts)


def wait_for_file(file, attempts=10):
    attempt=0
    attempt_limit=attempts
    while attempt < attempt_limit:
        if os.path.isfile(file):
            return
        time.sleep(10)
        attempt = attempt + 1


def wait_for_response(web_session, host, url, resp_predicate, attempts=10):
    
    attempt=0
    attempt_limit=attempts
    response = None
    while attempt < attempt_limit:
        try:
            response = web_session.get('https://{0}{1}'.format(host, url), verify=False)
            print('code: {0}'.format(response.status_code))
            if resp_predicate(response):
                return
        except Exception, e:
            print(e.message)
        time.sleep(10)
        attempt = attempt + 1
    if response and response.text:
        print(response.text)
    raise Exception('exhausted')
