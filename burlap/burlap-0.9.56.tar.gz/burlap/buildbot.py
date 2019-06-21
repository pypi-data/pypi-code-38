import os

from fabric.api import settings

from burlap.constants import *
from burlap import ServiceSatchel
from burlap.decorators import task
from burlap.trackers import FilesystemTracker, SettingsTracker, ORTracker

class BuildBotSatchel(ServiceSatchel):
    """
    Configures a Buildbot master and worker on the first host,
    with a worker on every additional host.
    """

    name = 'buildbot'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['git'],
        }

    def set_defaults(self):

        self.env.project_dir = '/usr/local/myproject'
        self.env.virtualenv_dir = '/usr/local/myproject/.env'
        self.env.home_dir = '/var/lib/{bb_user}'
        self.env.src_dir = 'src/buildbot'

        self.env.ssh_bin = '{home_dir}/bin'
        self.env.ssh_dir = '{home_dir}/.ssh'
        self.env.ssh_private_key = None # should be a *.pem file
        self.env.ssh_public_key = None # should be a *.pub file

        # Must match the main user, or otherwise we get rsync errors.
        self.env.user = 'ubuntu'
        self.env.group = 'ubuntu'

        self.env.bb_user = 'buildbot'
        self.env.bb_group = 'buildbot'

        self.env.manhole_user = 'admin'
        self.env.manhole_port = 1234

        self.env.perms = '777'

        #DEPRECATED
        # self.env.cron_path = '/etc/cron.d/buildbot_boot'
        # self.env.cron_user = 'root'
        # self.env.cron_group = 'root'
        # self.env.cron_perms = '600'

        self.env.extra_deploy_paths = ['buildbot/worker/info/', 'buildbot/worker/buildbot.tac']

        self.env.delete_deploy_paths = []

        self.env.check_ok = True
        self.env.check_ok_paths = {} # {branch: (url, text)}

        self.env.rsync_paths = [] # [[from_path, to_path, user, group]]

        self.env.enable_apache_site = True

        self.env.requirements = 'pip-requirements.txt'

        self.env.use_ssh_key = False

        self.env.pid_path = 'buildbot/{type}/twistd.pid'

        self.env.worker_names = ['worker']

        #DEPRECATED
        self.env.cron_check_enabled = False
        self.env.cron_check_schedule = '0,30 * * * *'
        self.env.cron_check_user = 'root'
        self.env.cron_cron_check_worker_pid_path = None
        self.env.cron_check_command_template = 'buildbot/check_buildbot.sh.template'
        self.env.cron_check_command_path = '/usr/local/bin/check_buildbot.sh'
        self.env.cron_check_crontab_template = 'buildbot/etc_crond_buildbot.template'
        self.env.cron_check_crontab_path = '/etc/cron.d/buildbot'

        self.env.supervisor_enabled = False

        self.env.service_commands = {
#             START:{
#                 UBUNTU: 'service apache2 start',
#             },
#             STOP:{
#                 UBUNTU: 'service apache2 stop',
#             },
#             DISABLE:{
#                 (UBUNTU, '14.04'): 'update-rc.d -f apache2 remove',
#             },
#             ENABLE:{
#                 (UBUNTU, '14.04'): 'update-rc.d apache2 defaults',
#             },
#             RELOAD:{
#                 UBUNTU: 'service apache2 reload',
#             },
#             RESTART:{
#                 # Note, the sleep 5 is necessary because the stop/start appears to
#                 # happen in the background but gets aborted if Fabric exits before
#                 # it completes.
#                 UBUNTU: 'service apache2 restart; sleep 3',
#             },
        }

    @property
    def is_first_host(self):
        return self.genv.hosts[0] == self.genv.host_string

    @task
    def restart(self):
        r = self.local_renderer
        self.set_permissions()
        if r.env.supervisor_enabled:
            r.sudo('supervisorctl restart all')
        else:
            self.restart_master(ignore_errors=True)
            self.restart_worker(ignore_errors=True)

    @property
    def restart_master_command(self):
        r = self.local_renderer
        r.env.restart_master_command = r.format(
            'sudo -u {bb_user} bash -c "cd {project_dir}/src/buildbot; '
            '{virtualenv_dir}/bin/buildbot restart master"')
        return r.env.restart_master_command

    @task
    def restart_master(self, ignore_errors=None):
        if not self.is_first_host:
            return
        ignore_errors = self.ignore_errors if ignore_errors is None else ignore_errors
        r = self.local_renderer
        s = {'warn_only':True} if ignore_errors else {}
        with settings(**s):
            r.run(self.restart_master_command)

    @task
    def upgrade_master(self):
        r = self.local_renderer
        r.run('sudo -u {bb_user} bash -c "cd {project_dir}/src/buildbot; {virtualenv_dir}/bin/buildbot upgrade-master {project_dir}/src/buildbot/master"')

    def get_restart_worker_command(self, name=None):
        r = self.local_renderer
        parts = []
        for worker_name in self.get_worker_names_for_current_host():
            if name and worker_name != name:
                continue
            r.env.worker_name = worker_name
            parts.append('cd {project_dir}/src/buildbot; {virtualenv_dir}/bin/buildbot-worker restart %s;' % worker_name)
        if not parts:
            return
        parts = ' '.join(parts)
        r.env.restart_worker_command = r.format('sudo -u {bb_user} bash -c "%s"' % parts)
        return r.env.restart_worker_command

    @task
    def restart_worker(self, ignore_errors=None, name=None):
        ignore_errors = self.ignore_errors if ignore_errors is None else ignore_errors
        r = self.local_renderer
        s = {'warn_only':True} if ignore_errors else {}
        with settings(**s):
            cmd = self.get_restart_worker_command(name=name)
            if cmd:
                print('cmd:', cmd)
                r.run(cmd)

    @task
    def start(self):
        r = self.local_renderer
        s = {'warn_only':True} if self.ignore_errors else {}
        with settings(**s):
            if r.env.supervisor_enabled:
                r.sudo('supervisorctl start all')
            else:
                r.run(
                    'sudo -u {bb_user} bash -c "cd {project_dir}/src/buildbot; '
                    '{virtualenv_dir}/bin/buildbot start master"')
                for worker_name in self.get_worker_names_for_current_host():
                    r.env.worker_name = worker_name
                    r.run(
                        'sudo -u {bb_user} bash -c "cd {project_dir}/src/buildbot; '
                        '{virtualenv_dir}/bin/buildbot-worker start {worker_name}"')

    @property
    def host_index(self):
        return self.genv.hosts.index(self.genv.host_string)

    def get_worker_names_for_current_host(self):
        r = self.local_renderer
        names = []
        host_index = self.host_index
        for i, worker_name in enumerate(r.env.worker_names):
            if i == host_index:
                names.append(worker_name)
        return names

    @task
    def stop(self):
        r = self.local_renderer
        s = {'warn_only': True}
        with settings(**s):
            if r.env.supervisor_enabled:
                r.sudo('supervisorctl stop all')
            else:
                if self.is_first_host:
                    r.run(
                        'sudo -u {bb_user} bash -c "cd {project_dir}/src/buildbot; '
                        '{virtualenv_dir}/bin/buildbot stop master"')
                for worker_name in self.get_worker_names_for_current_host():
                    r.env.worker_name = worker_name
                    with settings(warn_only=True):
                        r.run(
                            'sudo -u {bb_user} bash -c "cd {project_dir}/src/buildbot; '
                            '{virtualenv_dir}/bin/buildbot-worker stop {worker_name}"')

    @task
    def reload(self):
        r = self.local_renderer
        s = {'warn_only':True} if self.ignore_errors else {}
        with settings(**s):
            r.run(
                'sudo -u {bb_user} bash -c "'
                'cd {project_dir}/src/buildbot; '
                '{virtualenv_dir}/bin/buildbot reconfig master"')

    @task
    def set_permissions(self):
        r = self.local_renderer
        r.sudo('chown -R {bb_user}:{bb_group} {home_dir}')
        r.sudo('chown -R {bb_user}:{bb_group} {project_dir}')
        #r.sudo('chown -R {bb_user}:{bb_group} {project_dir}/src/buildbot/master')
        #r.sudo('chown -R {bb_user}:{bb_group} {project_dir}/src/buildbot/worker')
        r.sudo('chmod -R {perms} {project_dir}')

    @task
    def rsync_paths(self):
        r = self.local_renderer
        for from_path, to_path, to_user, to_group, to_perms in r.env.rsync_paths:
            assert os.path.isfile(from_path), 'File %s does not exist locally.' % from_path
            r.env.from_path = from_path
            r.env.to_path = to_path
            r.env.to_user = to_user
            r.env.to_group = to_group
            r.env.to_path_fq = os.path.join(to_path, os.path.split(from_path)[-1])
            r.env.to_perms = to_perms
#             r.local('rsync '
#                 '--verbose --compress '
#                 '--rsh "ssh -t -o StrictHostKeyChecking=no -i {key_filename}" '
#                 '{from_path} {user}@{host_string}:{to_path}')
            r.put(local_path=r.env.from_path, remote_path=r.env.to_path, use_sudo=True)
            r.sudo('chown {to_user}:{to_group} {to_path_fq}')
            r.sudo('chmod {to_perms} {to_path_fq}')

    @task
    def setup_dir(self, clean=0):
        pip = self.get_satchel('pip')
        clean = int(clean)
        r = self.local_renderer
        if clean:
            r.sudo('rm -Rf {virtualenv_dir} || true')
        r.sudo('mkdir -p {project_dir}')
        pip.update_install(
            requirements=self.env.requirements,
            virtualenv_dir=self.env.virtualenv_dir,
            user=self.env.user,
            group=self.env.group,
            perms=self.env.perms,
        )
        #r.sudo('{virtualenv_dir}/bin/pip install -U pip')
        r.sudo('chown -R {user}:{group} {project_dir}')
        r.sudo('chmod -R {perms} {project_dir}')

    @task
    def deploy_code(self):
        r = self.local_renderer

        r.sudo('chown -R {user}:{group} {project_dir}')
        r.sudo('chmod -R {perms} {project_dir}')

        for delete_path in r.env.delete_deploy_paths:
            r.sudo('rm -Rf %s' % delete_path)

        r.local('rsync '
            '--recursive --verbose --perms --times --links '
            '--compress --copy-links '
            '--exclude=*.pyc --exclude=gitpoller-workdir --exclude=*.log --exclude=twistd.pid '
            '--exclude=*.sqlite '
            '--exclude=build '
            '--exclude=worker '
            '--exclude=*_runtests '
            '--delete --delete-before '
            '--rsh "ssh -t -o StrictHostKeyChecking=no -i {key_filename}" '
            'src {user}@{host_string}:{project_dir}')

        for path in self.env.extra_deploy_paths:
            if path.endswith('/'):
                # Directory.
                r.env.tmp_path = path[:-1]
                r.env.tmp_remote_path = os.path.split(path[:-1])[0]
                r.sudo('mkdir -p {project_dir}/src/{tmp_remote_path}')
            else:
                # File.
                r.env.tmp_path = path
                r.env.tmp_remote_path = os.path.split(path)[0]

            r.pc('Fixing permissions...')
            r.sudo('chown -R {bb_user}:{bb_group} {project_dir}')
            r.sudo('chmod -R {perms} {project_dir}')
            r.local('rsync '
                '--recursive --verbose --times --omit-dir-times --links '
                '--compress --copy-links '
                '--delete --delete-before '
                '--rsh "ssh -t -o StrictHostKeyChecking=no -i {key_filename}" '
                'src/{tmp_path} {user}@{host_string}:{project_dir}/src/{tmp_remote_path}')

        self.rsync_paths()

        self.set_permissions()

    @task
    def view_log(self, name='master', section='twistd'):
        r = self.local_renderer
        r.env.name = name
        assert section in ('twistd', 'http')
        r.env.section = section
        r.run('tail -f --lines=100 {project_dir}/src/buildbot/{name}/{section}.log')

    @task
    def manhole(self):
        r = self.local_renderer
        r.env.host_string = '127.0.0.1'#self.genv.host_string
        r.run('ssh -p{manhole_port} {manhole_user}@{host_string}')

    @task
    def check_ok(self):
        """
        Ensures all tests have passed for this branch.

        This should be called before deployment, to prevent accidental deployment of code
        that hasn't passed automated testing.
        """
        import requests

        if not self.env.check_ok:
            return

        # Find current git branch.
        branch_name = self._local('git rev-parse --abbrev-ref HEAD', capture=True).strip()

        check_ok_paths = self.env.check_ok_paths or {}

        if branch_name in check_ok_paths:
            check = check_ok_paths[branch_name]
            if 'username' in check:
                auth = (check['username'], check['password'])
            else:
                auth = None
            ret = requests.get(check['url'], auth=auth)
            passed = check['text'] in ret.content
            assert passed, 'Check failed: %s' % check['url']

    @task
    def setup_apache(self):
        r = self.local_renderer
        if r.env.enable_apache_site and self.is_first_host:
            apache = self.get_satchel('apache')
            apache.enable_mod('proxy_http')

    @task
    def setup_user(self):
        r = self.local_renderer
        user = self.get_satchel('user')
        group = self.get_satchel('group')
        group.create(self.env.bb_group)
        user.create(
            username=r.env.bb_user,
            groups=r.env.bb_group,
            create_home=True,
            home_dir=r.format(r.env.home_dir),
            password=False,
        )
        #user.create(self.env.bb_user, self.env.bb_group)

    def deploy_pre_run(self):
        self.check_ok()

    @task
    def configure_ssh_key(self):
        r = self.local_renderer
        r.env.private_remote_path = '{ssh_dir}/id_rsa'
        r.env.public_remote_path = '{ssh_dir}/id_rsa.pub'
        if r.env.use_ssh_key:
            #https://www.cyberciti.biz/faq/how-to-set-up-ssh-keys-on-linux-unix/
            assert r.env.ssh_private_key, 'No SSH private key specified!'
            assert r.env.ssh_public_key, 'No SSH public key specified!'
            r.sudo('mkdir -p {ssh_dir}')
            r.put(local_path=r.env.ssh_private_key, remote_path=r.env.private_remote_path, use_sudo=True)
            r.put(local_path=r.env.ssh_public_key, remote_path=r.env.public_remote_path, use_sudo=True)
            r.sudo('chown -R {bb_user}:{bb_group} {ssh_dir}')
            r.sudo('chmod -R 0770 {ssh_dir}')
            r.sudo('chmod -R 0600 {ssh_dir}/*')
        else:
            r.sudo('rm -F {private_remote_path}')
            r.sudo('rm -F {public_remote_path}')

    @task
    def delete_logs(self):
        r = self.local_renderer
        names = ('master', 'worker')
        logs = ('twistd.log', 'http.log')
        for name in names:
            r.env.name = name
            for log in logs:
                r.env.log = log
                r.sudo('rm -f {project_dir}/src/buildbot/{name}/{log}')

    @task
    def install_cron_check(self):
        r = self.local_renderer

        # Install script to perform the actual check.
        assert r.env.cron_check_worker_pid_path, 'Worker PID path not set.'
        self.restart_master_command
        self.get_restart_worker_command()
        self.install_script(
            local_path=r.env.cron_check_command_template,
            remote_path=r.env.cron_check_command_path,
            render=True,
            extra=r.collect_genv())
        r.sudo('chown root:root {cron_check_command_path}')

        # Install crontab to schedule running the script.
        self.install_script(
            local_path=r.env.cron_check_crontab_template,
            remote_path=r.env.cron_check_crontab_path,
            render=True,
            extra=r.collect_genv())
        r.sudo('chown root:root {cron_check_crontab_path}')
        r.sudo('chmod 600 {cron_check_crontab_path}')
        r.sudo('service cron restart')

    @task
    def uninstall_cron_check(self):
        r = self.local_renderer
        r.sudo('rm -f {cron_check_crontab_path}')
        r.sudo('rm -f {cron_check_command_path}')
        r.sudo('service cron restart')

    @task
    def install_supervisor(self):
        r = self.local_renderer
        if r.env.supervisor_enabled:
            extra = {'workerN': r.genv.hosts.index(r.genv.host_string)+1}
            self.install_script(
                local_path='buildbot/supervisor.conf.template',
                remote_path='/etc/supervisor/conf.d/buildbot.conf',
                render=True,
                extra=extra)
        else:
            r.sudo('rm -f /etc/supervisor/conf.d/buildbot.conf')
            r.sudo('supervisorctl reload')

    # @task
    # def update_cron_check(self):
        # if not self.is_first_host:
            # return
        # elif self.param_changed_to('cron_check_enabled', True):
            # self.install_cron_check()
        # elif self.param_changed_to('cron_check_enabled', False):
            # self.uninstall_cron_check()

    @task
    def uninstall(self):
        r = self.local_renderer

        with settings(warn_only=True):
            self.stop()

        self.uninstall_cron_check()

        self.uninstall_cron()

        r.sudo('rm -Rf {virtualenv_dir} || true')
        r.sudo('rm -Rf {project_dir} || true')

    def get_trackers(self):
        r = self.local_renderer
        return [

            SettingsTracker(
                satchel=self,
                names='bb_user bb_group home_dir',
                action=self.setup_user),

            ORTracker(
                SettingsTracker(satchel=self, names='virtualenv_dir project_dir'),
                FilesystemTracker(base_dir=r.format('roles/{ROLE}'), extensions='pip-requirements.txt'),
                action=self.setup_dir),

            SettingsTracker(
                satchel=self,
                names='enable_apache_site',
                action=self.setup_apache),

            SettingsTracker(
                satchel=self,
                names='ssh_dir ssh_private_key ssh_public_key bb_user bb_group',
                action=self.configure_ssh_key),

            FilesystemTracker(
                base_dir=r.format(r.env.src_dir), extensions='*.py *.tac *.cfg htpasswd',
                action=self.deploy_code),

            # SettingsTracker(
                # satchel=self,
                # names='project_dir cron_path cron_perms',
                # action=self.install_cron),

            SettingsTracker(
                satchel=self,
                # names='project_dir cron_path cron_perms',
                action=self.install_supervisor),

            # SettingsTracker(
                # satchel=self,
                # names='cron_check_enabled',
                # action=self.update_cron_check),

        ]

    @task(precursors=['packager', 'user', 'apache'])
    def configure(self):
        r = self.local_renderer

        has_changes = self.has_changes
        if has_changes:
            self.vprint('Stopping any existing buildbot server...')
            with settings(warn_only=True):
                self.stop()

        super(BuildBotSatchel, self).configure()

        if has_changes:
            self.restart()
            if self.is_first_host:
                apache = self.get_satchel('apache')
                apache.reload()

buildbot = BuildBotSatchel()
