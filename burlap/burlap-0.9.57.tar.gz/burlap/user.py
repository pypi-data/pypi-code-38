from __future__ import print_function

import os
from pipes import quote
import random
import string

from fabric.api import hide

import six

from burlap.constants import *
from burlap import Satchel
from burlap.decorators import task


_SALT_CHARS = string.ascii_letters + string.digits + './'

CAT_KEY = 'cat-key'
UPLOAD_KEY = 'upload-key'

def _crypt_password(password):
    from crypt import crypt
    random.seed()
    salt = ''
    for _ in range(2):
        salt += random.choice(_SALT_CHARS)
    crypted_password = crypt(password, salt)
    return crypted_password


class UserSatchel(Satchel):

    name = 'user'

    def set_defaults(self):

        self.env.tmp_sudoers_fn = '/tmp/sudoers'

        self.env.key_type = 'rsa' # e.g. rsa|dsa
        self.env.key_bits = 2048 # e.g. 1024, 2048, or 4096
        self.env.key_filename_template = 'roles/{ROLE}/{host}-{username}.pem'
        self.env.key_perms = '600'

        self.env.home_template = '/home/{username}'
        #self.env.passwordless = True
        self.env.groups = {} # {username:[groups]}
        self.env.passwordless = {} # {username:True/False}
        self.env.passwords = {} # {username: password}
        self.env.reset_passwords_on_first_login = {} # {username: true/false}

        self.env.default_passwords = {} # {username:password}

        self.env.passwordless_method = CAT_KEY

    @task
    def enter_password_change(self, username=None, old_password=None):
        """
        Responds to a forced password change via `passwd` prompts due to password expiration.
        """
        from fabric.state import connections
        from fabric.network import disconnect_all
        r = self.local_renderer
#         print('self.genv.user:', self.genv.user)
#         print('self.env.passwords:', self.env.passwords)
        r.genv.user = r.genv.user or username
        r.pc('Changing password for user {user} via interactive prompts.')
        r.env.old_password = r.env.default_passwords[self.genv.user]
#         print('self.genv.user:', self.genv.user)
#         print('self.env.passwords:', self.env.passwords)
        r.env.new_password = self.env.passwords[self.genv.user]
        if old_password:
            r.env.old_password = old_password
        prompts = {
            '(current) UNIX password: ': r.env.old_password,
            'Enter new UNIX password: ': r.env.new_password,
            'Retype new UNIX password: ': r.env.new_password,
            #"Login password for '%s': " % r.genv.user: r.env.new_password,
#             "Login password for '%s': " % r.genv.user: r.env.old_password,
        }
        print('prompts:', prompts)

        r.env.password = r.env.old_password
        with self.settings(warn_only=True):
            ret = r._local("sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {user}@{host_string} echo hello", capture=True)
            #code 1 = good password, but prompts needed
            #code 5 = bad password
            #code 6 = good password, but host public key is unknown
        if ret.return_code in (1, 6) or 'hello' in ret:
            # Login succeeded, so we haven't yet changed the password, so use the default password.
            self.genv.password = r.env.old_password
        elif self.genv.user in self.genv.user_passwords:
            # Otherwise, use the password or key set in the config.
            self.genv.password = r.env.new_password
        else:
            # Default password fails and there's no current password, so clear.
            self.genv.password = None
        print('using password:', self.genv.password)

        # Note, the correct current password should be set in host.initrole(), not here.
        #r.genv.password = r.env.new_password
        #r.genv.password = r.env.new_password
        with self.settings(prompts=prompts):
            ret = r._run('echo checking for expired password')
            print('ret:[%s]' % ret)
            do_disconnect = 'passwd: password updated successfully' in ret
            print('do_disconnect:', do_disconnect)
            if do_disconnect:
                # We need to disconnect to reset the session or else Linux will again prompt
                # us to change our password.
                disconnect_all()

                # Further logins should require the new password.
                self.genv.password = r.env.new_password

    @task
    def configure_keyless(self):
        self.generate_keys()
        self.passwordless()

    @task
    def togroups(self, user, groups):
        """
        Adds the user to the given list of groups.
        """

        r = self.local_renderer

        if isinstance(groups, six.string_types):
            groups = [_.strip() for _ in groups.split(',') if _.strip()]
        for group in groups:
            r.env.username = user
            r.env.group = group
            r.sudo('groupadd --force {group}')
            r.sudo('adduser {username} {group}')

    @task
    def passwordless(self, username, pubkey):
        """
        Configures the user to use an SSL key without a password.
        Assumes you've run generate_keys() first.
        """

        r = self.local_renderer

        r.env.username = username
        r.env.pubkey = pubkey
        if not self.dryrun:
            assert os.path.isfile(r.env.pubkey), \
                'Public key file "%s" does not exist.' % (str(r.env.pubkey),)

        first = os.path.splitext(r.env.pubkey)[0]
        r.env.pubkey = first+'.pub'
        r.env.pemkey = first+'.pem'
        r.env.home = r.env.home_template.format(username=username)

        # Upload the SSH key.
        r.sudo('mkdir -p {home}/.ssh')
        r.sudo('chown -R {user}:{user} {home}/.ssh')

        if r.env.passwordless_method == UPLOAD_KEY:
            put_remote_paths = self.put(local_path=r.env.pubkey)
            r.env.put_remote_path = put_remote_paths[0]
            r.sudo('cat {put_remote_path} >> {home}/.ssh/authorized_keys')
            r.sudo('rm -f {put_remote_path}')
        elif r.env.passwordless_method == CAT_KEY:
            r.env.password = r.env.default_passwords.get(r.env.username, r.genv.password)
            if r.env.password:
                r.local("cat {pubkey} | sshpass -p '{password}' ssh {user}@{host_string} 'cat >> {home}/.ssh/authorized_keys'")
            else:
                r.local("cat {pubkey} | ssh {user}@{host_string} 'cat >> {home}/.ssh/authorized_keys'")
        else:
            raise NotImplementedError

        # Disable password.
        r.sudo('cp /etc/sudoers {tmp_sudoers_fn}')
        r.sudo('echo "{username} ALL=(ALL) NOPASSWD: ALL" >> {tmp_sudoers_fn}')
        r.sudo('sudo EDITOR="cp {tmp_sudoers_fn}" visudo')

        r.sudo('service ssh reload')

        print('You should now be able to login with:')
        r.env.host_string = self.genv.host_string or (self.genv.hosts and self.genv.hosts[0])#self.genv.hostname_hostname
        r.comment('\tssh -i {pemkey} {username}@{host_string}')

    @task
    def generate_keys(self, username, hostname):
        """
        Generates *.pem and *.pub key files suitable for setting up passwordless SSH.
        """

        r = self.local_renderer

        #r.env.key_filename = r.env.key_filename or env.key_filename
        #assert r.env.key_filename, 'r.env.key_filename or env.key_filename must be set. e.g. roles/role/app_name-role.pem'
        r.env.key_filename = self.env.key_filename_template.format(
            ROLE=self.genv.ROLE,
            host=hostname,
            username=username,
        )
        if os.path.isfile(r.env.key_filename):
            r.pc('Key file {key_filename} already exists. Skipping generation.'.format(**r.env))
        else:
            r.local("ssh-keygen -t {key_type} -b {key_bits} -f {key_filename} -N ''")
            r.local('chmod {key_perms} {key_filename}')
            if r.env.key_filename.endswith('.pem'):
                src = r.env.key_filename+'.pub'
                dst = (r.env.key_filename+'.pub').replace('.pem', '')
#                 print('generate_keys:', src, dst)
                r.env.src = src
                r.env.dst = dst
                r.local('mv {src} {dst}')
        return r.env.key_filename

    @task
    def exists(self, name):
        """
        Check if a user exists.
        """
        with self.settings(hide('running', 'stdout', 'warnings'), warn_only=True):
            return self.run('getent passwd %s' % name).succeeded

    @task
    def create(self, username, groups=None, uid=None, create_home=None, system=False, password=None, home_dir=None):
        """
        Creates a user with the given username.
        """
        r = self.local_renderer
        r.env.username = username

        args = []

        if uid:
            args.append('-u %s' % uid)

        if create_home is None:
            create_home = not system

        if create_home is True:
            if home_dir:
                args.append('--home %s' % home_dir)
        elif create_home is False:
            args.append('--no-create-home')

        if password is None:
            pass
        elif password:
            crypted_password = _crypt_password(password)
            args.append('-p %s' % quote(crypted_password))
        else:
            args.append('--disabled-password')

        args.append('--gecos ""')

        if system:
            args.append('--system')

        r.env.args = ' '.join(args)
        r.env.groups = (groups or '').strip()
        r.sudo('adduser {args} {username} || true')
        if groups:
            for group in groups.split(' '):
                group = group.strip()
                if not group:
                    continue
                r.sudo('adduser %s %s || true' % (username, group))

    @task
    def expire_password(self, username):
        """
        Forces the user to change their password the next time they login.
        """
        r = self.local_renderer
        r.env.username = username
        r.sudo('chage -d 0 {username}')

    @task
    def configure(self):
        r = self.local_renderer

        lm = self.last_manifest
        lm_reset_passwords_on_first_login = lm.reset_passwords_on_first_login or {}
        lm_passwordless = lm.passwordless or {}
        lm_passwords = lm.passwords or {}
        lm_groups = lm.groups or {}

        # Make one-time password changes.
        just_changed = set()
        for username, ret in r.env.reset_passwords_on_first_login.items():
            if ret and not lm_reset_passwords_on_first_login.get(username):
                self.enter_password_change(username)
                just_changed.add(username)

        # Make passwordless logins.
        for username, is_passwordless in r.env.passwordless.items():
            if is_passwordless:
                if not lm_passwordless.get(username):
                    # If this user is passwordless, and we've not already created a passwordless
                    # login for them, then create one.
                    pubkey = self.generate_keys(username=username, host=self.genv.hostname_hostname)
                    self.passwordless(username=username, pubkey=pubkey)
            else:
                #TODO:expire old SSH key?
                pass

        # Update passwords.
        for username, password in r.env.passwords.items():
            if username in just_changed:
                continue
            if lm_passwords.get(username) != password:
                r.env.username = username
                r.env.password = password
                r.sudo('echo "{username}:{password}"|chpasswd')

        # Create new users.
        r = self.new_local_renderer
        new_users = set(r.env.groups).difference(lm_groups)
        for username in new_users:
            password = r.env.passwords.get(username, '')
            self.create(username=username, password=password)

        # Set groups.
        r = self.new_local_renderer
        for username, groups in r.env.groups.items():
            self.togroups(username, groups)

user = UserSatchel()
