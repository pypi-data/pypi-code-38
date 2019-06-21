import requests
from syncloudlib.integration.ssh import run_scp, run_ssh
from syncloudlib.integration.installer import wait_for_platform_web, wait_for_installer


class Device:

    def __init__(self, main_domain, device_host, domain, device_user, device_password, redirect_user, redirect_password, ssh_env_vars):
        self.main_domain = main_domain
        self.device_host = device_host
        self.domain = domain
        self.device_user = device_user
        self.device_password = device_password
        self.redirect_user = redirect_user
        self.redirect_password = redirect_password
        self.ssh_env_vars = ssh_env_vars
        self.ssh_password = 'syncloud'
        self.session = None

    def activate(self):
        wait_for_platform_web(self.device_host)
        response = requests.post('http://{0}:81/rest/activate'.format(self.device_host),
                                 data={'main_domain': self.main_domain,
                                       'redirect_email': self.redirect_user,
                                       'redirect_password': self.redirect_password,
                                       'user_domain': self.domain,
                                       'device_username': self.device_user,
                                       'device_password': self.device_password})
        if response.status_code == 200:
            self.activated()
        
        self.login()
        return response

    def activated(self):
        self.ssh_password = self.device_password

    def login(self, retries=5):
    
        retry = 0
        while True:
            try:
                session = requests.session()
                session.post('https://{0}/rest/login'.format(self.device_host), verify=False, data={'name': self.device_user, 'password': self.device_password})
                response = session.get('https://{0}/rest/user'.format(self.device_host), verify=False, allow_redirects=False)
                if response.status_code == 200:
                    self.session = session
                    return session
            except Exception, e:
                retry += 1
                if retry > retries:
                    raise e
                print(e.message)
                print('retry {0} of {1}'.format(retry, retries))
   
    def app_remove(self, app):
        response = self.session.get('https://{0}/rest/remove?app_id={1}'.format(self.device_host, app), allow_redirects=False, verify=False)
        wait_for_installer(self.session, self.device_host)
        return response

    def run_ssh(self, cmd, retries=0, throw=True, env_vars=''):
        ssh_env_vars = self.ssh_env_vars + ' ' + env_vars
        return run_ssh(self.device_host, cmd, password=self.ssh_password, env_vars=ssh_env_vars, retries=retries, throw=throw)
    
    def scp_from_device(self, dir_from, dir_to, throw=False):
        return run_scp('root@{0}:{1} {2}'.format(self.device_host, dir_from, dir_to), password=self.ssh_password, throw=throw)

    def scp_to_device(self, dir_from, dir_to, throw=False):
        return run_scp('{0} root@{1}:{2}'.format(dir_from, self.device_host, dir_to), password=self.ssh_password, throw=throw)

    def http_get(self, url):
        return self.session.get('https://{0}{1}'.format(self.device_host, url), allow_redirects=False, verify=False)
