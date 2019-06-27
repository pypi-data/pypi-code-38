from __future__ import print_function

import os
import sys
from functools import partial

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task


class ApacheSatchel(ServiceSatchel):
    name = 'apache'

    post_deploy_command = 'reload'

    templates = [
        '{site_template}',
    ]

    @property
    def packager_system_packages(self):

        mod_lst = []

        if self.env.modevasive_enabled:
            mod_lst.append('libapache2-mod-evasive')

        if self.env.modsecurity_enabled:
            mod_lst.append('libapache2-modsecurity')

        if self.env.modrpaf_enabled:
            mod_lst.append('libapache2-mod-rpaf')

        if self.env.visitors_enabled:
            # TODO:fix? package removed in Ubuntu 16?
            mod_lst.append('visitors')

        if sys.version_info.major == 3:
            # Note that for Python 3, libapache2-mod-wsgi may need to be removed if installed.
            mod_lst.extend(['apache2-dev', 'libapache2-mod-wsgi-py3'])
        else:
            mod_lst.append('libapache2-mod-wsgi')

        return {
            FEDORA: ['httpd'] + mod_lst,
            UBUNTU: ['apache2', 'apache2-utils'] + mod_lst,
            (UBUNTU, '12.04'): ['apache2'] + mod_lst,
            (UBUNTU, '12.10'): ['apache2'] + mod_lst,
            (UBUNTU, '14.04'): ['apache2', 'apache2-utils'] + mod_lst,
            (UBUNTU, '14.10'): ['apache2', 'apache2-utils'] + mod_lst,
            (UBUNTU, '16.04'): ['apache2', 'apache2-utils'] + mod_lst,
            (UBUNTU, '16.10'): ['apache2', 'apache2-utils'] + mod_lst,
            (UBUNTU, '16.10'): ['apache2', 'apache2-utils'] + mod_lst,
        }

    def set_defaults(self):

        self.env.service_commands = {
            START: {
                FEDORA: 'systemctl start httpd.service',
                UBUNTU: 'service apache2 start',
            },
            STOP: {
                FEDORA: 'systemctl stop httpd.service',
                UBUNTU: 'service apache2 stop',
            },
            DISABLE: {
                FEDORA: 'systemctl disable httpd.service',
                UBUNTU: 'chkconfig apache2 off',
                (UBUNTU, '14.04'): 'update-rc.d -f apache2 remove',
            },
            ENABLE: {
                FEDORA: 'systemctl enable httpd.service',
                UBUNTU: 'chkconfig apache2 on',
                (UBUNTU, '14.04'): 'update-rc.d apache2 defaults',
            },
            RELOAD: {
                FEDORA: 'systemctl reload httpd.service',
                UBUNTU: 'service apache2 reload',
            },
            RESTART: {
                FEDORA: 'systemctl restart httpd.service',
                # UBUNTU: 'service apache2 restart',
                # Note, the sleep 5 is necessary because the stop/start appears to
                # happen in the background but gets aborted if Fabric exits before
                # it completes.
                UBUNTU: 'service apache2 restart; sleep 3',
            },
        }

        # An Apache-conf file and filename friendly string that uniquely identifies
        # your web application.
        self.env.application_name = None

        # The Jinja-formatted template file used to render site configurations.
        self.env.site_template = 'apache/apache_site.template.conf'

        self.env.error_log = '/var/log/apache2/error.log'
        self.env.log_level = 'warn'

        self.env.auth_basic = False
        self.env.auth_basic_authuserfile = '{apache_docroot}/.htpasswd_{apache_site}'
        self.env.auth_basic_users = []  # [(user,password)]

        # If true, activates a rewrite rule that causes domain.com to redirect
        # to www.domain.com.
        self.env.enforce_subdomain = True

        self.env.ssl = True
        self.env.ssl_chmod = 440
        self.env.ssl_port = 443

        # A list of path patterns that should have HTTPS enforced.
        self.env.ssl_secure_paths_enforce = True
        self.env.ssl_secure_paths = ['/admin/(.*)']

        self.env.web_user = 'www-data'
        self.env.web_group = 'www-data'
        self.env.wsgi_user = 'www-data'
        self.env.wsgi_group = 'www-data'
        self.env.chmod = 775

        self.env.mods_enabled = ['rewrite', 'wsgi', 'ssl']

        # The value of the Apache's ServerName field. Usually should be set
        # to the domain.
        self.env.server_name = None

        self.env.server_aliases_template = ''

        self.env.docroot = '/usr/local/{apache_application_name}'
        self.env.ports_path = '{apache_root}/ports.conf'
        self.env.ssl_path = '{apache_root}/ssl'

        self.env.domain_with_sub_template = ''
        self.env.domain_without_sub_template = ''
        self.env.domain_with_sub = None
        self.env.domain_without_sub = None

        self.env.maintenance_template = 'apache/maintenance.html.template'
        self.env.maintenance_fn = 'maintenance.html'
        self.env.maintenance_path = '{apache_docroot}/{maintenance_fn}'

        self.env.wsgi_enabled = False
        self.env.wsgi_template = 'django/django.template.wsgi'
        self.env.wsgi_python_path = None
        self.env.wsgi_scriptalias = None
        self.env.wsgi_server_memory_gb = 8
        self.env.wsgi_processes = 5
        self.env.wsgi_threads = 15

        self.env.domain_redirect_templates = []  # [(wrong_domain,right_domain)]
        self.env.domain_redirects = []  # [(wrong_domain,right_domain)]

        self.env.extra_rewrite_rules = ''

        self.env.modrpaf_enabled = False

        self.env.visitors_enabled = False

        self.env.modevasive_enabled = False
        self.env.modevasive_DOSEmailNotify = 'admin@localhost'
        self.env.modevasive_DOSPageInterval = 1  # seconds
        self.env.modevasive_DOSPageCount = 2
        self.env.modevasive_DOSSiteCount = 50
        self.env.modevasive_DOSSiteInterval = 1  # seconds
        self.env.modevasive_DOSBlockingPeriod = 10  # seconds

        self.env.modsecurity_enabled = False
        self.env.modsecurity_download_url = 'https://github.com/SpiderLabs/owasp-modsecurity-crs/tarball/master'

        # OS specific default settings.
        self.env.specifics = type(self.genv)()
        self.env.specifics[LINUX] = type(self.genv)()

        self.env.specifics[LINUX][FEDORA] = type(self.genv)()
        self.env.specifics[LINUX][FEDORA].root = '/etc/httpd'
        self.env.specifics[LINUX][FEDORA].conf = '/etc/httpd/conf/httpd.conf'
        self.env.specifics[LINUX][FEDORA].sites_available = '/etc/httpd/sites-available'
        self.env.specifics[LINUX][FEDORA].sites_enabled = '/etc/httpd/sites-enabled'
        self.env.specifics[LINUX][FEDORA].log_dir = '/var/log/httpd'
        self.env.specifics[LINUX][FEDORA].pid = '/var/run/httpd/httpd.pid'

        self.env.specifics[LINUX][UBUNTU] = type(self.genv)()
        self.env.specifics[LINUX][UBUNTU].root = '/etc/apache2'
        self.env.specifics[LINUX][UBUNTU].conf = '/etc/apache2/httpd.conf'
        self.env.specifics[LINUX][UBUNTU].sites_available = '/etc/apache2/sites-available'
        self.env.specifics[LINUX][UBUNTU].sites_enabled = '/etc/apache2/sites-enabled'
        self.env.specifics[LINUX][UBUNTU].log_dir = '/var/log/apache2'
        self.env.specifics[LINUX][UBUNTU].pid = '/var/run/apache2/apache2.pid'

        self.env.delete_site_command = None

        self.env.manage_httpd_conf = True
        self.env.manage_ports_conf = True
        self.env.manage_site_conf = True

        self.env.ssl_certificates = None
        self.env.ssl_certificates_templates = []

        # Apache site config files use a similar syntax to our template syntax,
        # so instead of having to escape all of Apache's variables, we list them here so
        # our templating system knows to not try interpolating them.
        self.env.ignored_template_variables = [
            'APACHE_LOG_DIR',
            'GLOBAL',
            'DOCUMENT_ROOT',
            'SCRIPT_FILENAME',
            'SERVER_NAME',
            'REQUEST_URI',
            'GROUP',
            'Referer',
            'User-Agent',
            'X-Forwarded-For',
            'HTTP:X-Forwarded-Proto',
            'HTTPS',
            'HTTP',
            'HTTP_HOST',
            'HTTP_USER_AGENT',
            'REMOTE_ADDR',
        ]

        # The local and remote relative directory where the SSL certificates are stored.
        self.env.ssl_dir_local = 'ssl'

        # The default remote directory to store SSL certificates.
        self.env.ssl_dir = '/etc/apache2/ssl/'

        # An optional segment to insert into the domain, customizable by role.
        # Useful for easily keying domain-local.com/domain-dev.com/domain-staging.com.
        self.env.locale = ''

        self.env.sync_sets = {}  # {name:[dict(local_path='static/', remote_path='$AWS_BUCKET:/')]}

        # This will be appended to the custom Apache configuration file.
        self.env.httpd_conf_append = []

    @task
    def enable_mod(self, name):
        self.sudo('a2enmod %s' % name)

    @task
    def disable_mod(self, name):
        with self.settings(warn_only=True):
            self.sudo('a2dismod %s' % name)

    @task
    def enable_mods(self):
        """
        Enables all modules in the current module list.
        Does not disable any currently enabled modules not in the list.
        """
        r = self.local_renderer
        for mod_name in r.env.mods_enabled:
            with self.settings(warn_only=True):
                self.enable_mod(mod_name)

    @task
    def enable_site(self, name):
        self.sudo('a2ensite %s' % name)

    @task
    def disable_site(self, name):
        self.sudo('a2dissite %s' % name)

    @task
    def optimize_wsgi_processes(self):
        """
        Based on the number of sites per server and the number of resources on the server,
        calculates the optimal number of processes that should be allocated for each WSGI site.
        """
        r = self.local_renderer
        # r.env.wsgi_processes = 5
        r.env.wsgi_server_memory_gb = 8

        verbose = self.verbose

        all_sites = list(self.iter_sites(site=ALL, setter=self.set_site_specifics))

        # (current_mem/current_sites)/current_process = ()
        # (16/x)/(8/16) = y
        # (16/x)*(16/8) = y
        # (16*16)/(num_sites*8) = y

    #     @task
    #     def visitors(self, force=0):
    #         """
    #         Generates an Apache access report using the Visitors command line tool.
    #         Requires the APACHE2_VISITORS service to be enabled for the current host.
    #         """
    #         if not int(force):
    #             assert ApacheVisitors.name.upper() in self.genv.services or ApacheVisitors.name.lower() in self.genv.services, \
    #                 'Visitors has not been configured for this host.'
    #         self.run('visitors -o text /var/log/apache2/%(apache_application_name)s-access.log* | less' % self.genv)

    def create_local_renderer(self):
        """
        Instantiates a new local renderer.
        Override this to do any additional initialization.
        """
        r = super(ApacheSatchel, self).create_local_renderer()

        # Dynamically set values based on target operating system.
        os_version = self.os_version
        apache_specifics = r.env.specifics[os_version.type][os_version.distro]
        r.env.update(apache_specifics)

        return r

    def iter_certificates(self):
        r = self.local_renderer
        for cert_type, cert_file_template in r.env.ssl_certificates_templates:
            if self.verbose:
                print('cert_type, cert_file_template:', cert_type, cert_file_template, file=sys.stderr)
            _local_cert_file = os.path.join(r.env.ssl_dir_local, cert_file_template % self.genv)
            local_cert_file = self.find_template(_local_cert_file)
            assert local_cert_file, 'Unable to find local certificate file: %s' % (_local_cert_file,)
            remote_cert_file = os.path.join(r.env.ssl_dir, cert_file_template % self.genv)
            yield cert_type, local_cert_file, remote_cert_file

    @task
    def install_ssl(self, site=ALL):
        from burlap.common import iter_sites
        verbose = self.verbose

        for _site, site_data in iter_sites(site=site, setter=self.set_site_specifics):

            site_secure = _site
            self.set_site_specifics(site_secure)

            self.sudo_or_dryrun('mkdir -p %(apache_ssl_dir)s' % self.genv)

            if self.genv.apache_ssl:
                for cert_type, local_cert_file, remote_cert_file in self.iter_certificates():
                    if verbose:
                        print('=' * 80)
                        print('Installing certificate %s->%s...' % (local_cert_file, remote_cert_file,))
                    self.put_or_dryrun(
                        local_path=local_cert_file,
                        remote_path=remote_cert_file,
                        use_sudo=True)

        self.sudo_or_dryrun('mkdir -p %(apache_ssl_dir)s' % self.genv)
        self.sudo_or_dryrun('chown -R %(apache_web_user)s:%(apache_web_group)s %(apache_ssl_dir)s' % self.genv)
        self.sudo_or_dryrun('chmod -R %(apache_ssl_chmod)s %(apache_ssl_dir)s' % self.genv)

    @task
    def install_auth_basic_user_file(self, site=None):
        """
        Installs users for basic httpd auth.
        """
        r = self.local_renderer

        hostname = self.current_hostname

        target_sites = self.genv.available_sites_by_host.get(hostname, None)

        for _site, site_data in self.iter_sites(site=site, setter=self.set_site_specifics):
            if self.verbose:
                print('~' * 80, file=sys.stderr)
                print('Site:', _site, file=sys.stderr)
                print('env.apache_auth_basic:', r.env.auth_basic, file=sys.stderr)

            # Only load site configurations that are allowed for this host.
            if target_sites is not None:
                assert isinstance(target_sites, (tuple, list))
                if _site not in target_sites:
                    continue

            if not r.env.auth_basic:
                continue

            assert r.env.auth_basic_users, 'No apache auth users specified.'
            for username, password in r.env.auth_basic_users:
                r.env.auth_basic_username = username
                r.env.auth_basic_password = password
                r.env.apache_site = _site
                r.env.fn = r.format(r.env.auth_basic_authuserfile)
                if self.files.exists(r.env.fn):
                    r.sudo('htpasswd -b {fn} {auth_basic_username} {auth_basic_password}')
                else:
                    r.sudo('htpasswd -b -c {fn} {auth_basic_username} {auth_basic_password}')

    @task
    def install_auth_basic_user_file_all(self):
        self.install_auth_basic_user_file(site='all')

    @task
    def view_error_log(self):
        self.run('tail -f {apache_error_log}')

    @task
    def sync_media(self, sync_set=None, clean=0, iter_local_paths=0):
        """
        Uploads select media to an Apache accessible directory.
        """

        # Ensure a site is selected.
        self.genv.SITE = self.genv.SITE or self.genv.default_site

        r = self.local_renderer

        clean = int(clean)
        self.vprint('Getting site data for %s...' % self.genv.SITE)

        self.set_site_specifics(self.genv.SITE)

        sync_sets = r.env.sync_sets
        if sync_set:
            sync_sets = [sync_set]

        ret_paths = []
        for _sync_set in sync_sets:
            for paths in r.env.sync_sets[_sync_set]:
                r.env.sync_local_path = os.path.abspath(paths['local_path'] % self.genv)
                if paths['local_path'].endswith('/') and not r.env.sync_local_path.endswith('/'):
                    r.env.sync_local_path += '/'

                if iter_local_paths:
                    ret_paths.append(r.env.sync_local_path)
                    continue

                r.env.sync_remote_path = paths['remote_path'] % self.genv

                if clean:
                    r.sudo('rm -Rf {apache_sync_remote_path}')

                print('Syncing %s to %s...' % (r.env.sync_local_path, r.env.sync_remote_path))

                r.env.tmp_chmod = paths.get('chmod', r.env.chmod)
                r.sudo('mkdir -p {apache_sync_remote_path}')
                r.sudo('chmod -R {apache_tmp_chmod} {apache_sync_remote_path}')
                r.local('rsync -rvz --progress --recursive --no-p --no-g '
                        '--rsh "ssh -o StrictHostKeyChecking=no -i {key_filename}" {apache_sync_local_path} {user}@{host_string}:{apache_sync_remote_path}')
                r.sudo('chown -R {apache_web_user}:{apache_web_group} {apache_sync_remote_path}')

        if iter_local_paths:
            return ret_paths

    def get_media_timestamp(self):
        """
        Called after a deployment to record any data necessary to detect changes
        for a future deployment.
        """
        from burlap.common import get_last_modified_timestamp
        data = 0
        for path in self.sync_media(iter_local_paths=1):
            data = min(data, get_last_modified_timestamp(path) or data)
        # TODO:hash media names and content
        if self.verbose:
            print('date:', data)
        return data

    @task
    def record_manifest(self):
        """
        Called after a deployment to record any data necessary to detect changes
        for a future deployment.
        """
        manifest = super(ApacheSatchel, self).record_manifest()
        manifest['available_sites'] = self.genv.available_sites
        manifest['available_sites_by_host'] = self.genv.available_sites_by_host
        manifest['media_timestamp'] = self.get_media_timestamp()
        return manifest

    @task
    def configure_modevasive(self):
        """
        Installs the mod-evasive Apache module for combating DDOS attacks.

        https://www.linode.com/docs/websites/apache-tips-and-tricks/modevasive-on-apache
        """
        r = self.local_renderer
        if r.env.modevasive_enabled:
            self.install_packages()

            # Write conf for each Ubuntu version since they don't conflict.
            fn = r.render_to_file('apache/apache_modevasive.template.conf')

            # Ubuntu 12.04
            r.put(
                local_path=fn,
                remote_path='/etc/apache2/mods-available/mod-evasive.conf',
                use_sudo=True)

            # Ubuntu 14.04
            r.put(
                local_path=fn,
                remote_path='/etc/apache2/mods-available/evasive.conf',
                use_sudo=True)

            self.enable_mod('evasive')
        else:
            #             print('self.last_manifest:', self.last_manifest)
            #             print('a:', self.last_manifest.apache_modevasive_enabled)
            #             print('b:', self.last_manifest.modevasive_enabled)
            if self.last_manifest.modevasive_enabled:
                self.disable_mod('evasive')

    @task
    def configure_modsecurity(self):
        """
        Installs the mod-security Apache module.

        https://www.modsecurity.org
        """
        r = self.local_renderer
        if r.env.modsecurity_enabled and not self.last_manifest.modsecurity_enabled:

            self.install_packages()

            # Write modsecurity.conf.
            fn = self.render_to_file('apache/apache_modsecurity.template.conf')
            r.put(local_path=fn, remote_path='/etc/modsecurity/modsecurity.conf', use_sudo=True)

            # Write OWASP rules.
            r.env.modsecurity_download_filename = '/tmp/owasp-modsecurity-crs.tar.gz'
            r.sudo('cd /tmp; wget --output-document={apache_modsecurity_download_filename} {apache_modsecurity_download_url}')
            r.env.modsecurity_download_top = r.sudo(
                "cd /tmp; "
                "tar tzf %(apache_modsecurity_download_filename)s | sed -e 's@/.*@@' | uniq" % self.genv)
            r.sudo('cd /tmp; tar -zxvf %(apache_modsecurity_download_filename)s' % self.genv)
            r.sudo('cd /tmp; cp -R %(apache_modsecurity_download_top)s/* /etc/modsecurity/' % self.genv)
            r.sudo('mv /etc/modsecurity/modsecurity_crs_10_setup.conf.example  /etc/modsecurity/modsecurity_crs_10_setup.conf')

            r.sudo('rm -f /etc/modsecurity/activated_rules/*')
            r.sudo('cd /etc/modsecurity/base_rules; '
                   'for f in * ; do ln -s /etc/modsecurity/base_rules/$f /etc/modsecurity/activated_rules/$f ; done')
            r.sudo('cd /etc/modsecurity/optional_rules; '
                   'for f in * ; do ln -s /etc/modsecurity/optional_rules/$f /etc/modsecurity/activated_rules/$f ; done')

            r.env.httpd_conf_append.append('Include "/etc/modsecurity/activated_rules/*.conf"')

            self.enable_mod('evasive')
            self.enable_mod('headers')
        elif not self.env.modsecurity_enabled and self.last_manifest.modsecurity_enabled:
            self.disable_mod('modsecurity')

    @task
    def configure_modrpaf(self):
        """
        Installs the mod-rpaf Apache module.

        https://github.com/gnif/mod_rpaf
        """
        r = self.local_renderer
        if r.env.modrpaf_enabled:
            self.install_packages()
            self.enable_mod('rpaf')
        else:
            if self.last_manifest.modrpaf_enabled:
                self.disable_mod('mod_rpaf')

    @task
    def configure_site(self, full=1, site=None, delete_old=0):
        """
        Configures Apache to host one or more websites.
        """
        from burlap import service

        r = self.local_renderer

        print('Configuring Apache...', file=sys.stderr)

        site = site or self.genv.SITE

        if int(delete_old) and site == ALL:
            # Delete all existing enabled and available sites.
            r.sudo('rm -f {sites_available}/*')
            r.sudo('rm -f {sites_enabled}/*')

        if r.env.manage_site_conf:

            # Run an optional customizable command to clear or delete old sites before writing the new ones.
            if r.env.delete_site_command:
                r.sudo(r.env.delete_site_command)

            for _site, site_data in self.iter_sites(site=site, setter=self.set_site_specifics):
                r = self.local_renderer

                if self.verbose:
                    print('-' * 80, file=sys.stderr)
                    print('Site:', _site, file=sys.stderr)
                    print('-' * 80, file=sys.stderr)

                r.env.apache_site = _site
                r.env.server_name = r.format(r.env.domain_template)

                # Write WSGI template
                if r.env.wsgi_enabled:
                    r.pc('Writing WSGI template for site %s...' % _site)
                    r.env.wsgi_scriptalias = r.format(r.env.wsgi_scriptalias)
                    fn = self.render_to_file(r.env.wsgi_template)
                    r.env.wsgi_dir = r.env.remote_dir = os.path.split(r.env.wsgi_scriptalias)[0]
                    r.sudo('mkdir -p {remote_dir}')
                    r.put(local_path=fn, remote_path=r.env.wsgi_scriptalias, use_sudo=True)

                # Write site configuration.
                r.pc('Writing site configuration for site %s...' % _site)
                r.env.auth_basic_authuserfile = r.format(self.env.auth_basic_authuserfile)
                r.env.ssl_certificates = list(self.iter_certificates())
                if r.env.server_aliases_template:
                    r.env.server_aliases = r.format(r.env.server_aliases_template)
                if r.env.domain_with_sub_template:
                    r.env.domain_with_sub = r.format(r.env.domain_with_sub_template)
                if r.env.domain_without_sub_template:
                    r.env.domain_without_sub = r.format(r.env.domain_without_sub_template)
                if r.env.domain_template:
                    r.env.domain = r.format(r.env.domain_template)
                genv = r.collect_genv()
                genv['current_hostname'] = self.current_hostname
                fn = self.render_to_file(
                    self.env.site_template,
                    extra=genv,
                    formatter=partial(r.format, ignored_variables=self.env.ignored_template_variables))
                r.env.site_conf = _site + '.conf'
                r.env.site_conf_fqfn = os.path.join(r.env.sites_available, r.env.site_conf)
                r.put(local_path=fn, remote_path=r.env.site_conf_fqfn, use_sudo=True)

                self.enable_site(_site)

                self.clear_local_renderer()

        self.enable_mods()

        if int(full):
            # Write master Apache configuration file.
            if r.env.manage_httpd_conf:
                fn = self.render_to_file('apache/apache_httpd.template.conf')
                r.put(local_path=fn, remote_path=r.env.conf, use_sudo=True)

            # Write Apache listening ports configuration.
            if r.env.manage_ports_conf:
                fn = self.render_to_file('apache/apache_ports.template.conf')
                r.put(local_path=fn, remote_path=r.env.ports_path, use_sudo=True)

        r.sudo('chown -R {apache_web_user}:{apache_web_group} {apache_root}')

    @task
    def maint_up(self):
        """
        Forwards all traffic to a page saying the server is down for maintenance.
        """
        r = self.local_renderer
        fn = self.render_to_file(r.env.maintenance_template, extra={'current_hostname': self.current_hostname})
        r.put(local_path=fn, remote_path=r.env.maintenance_path, use_sudo=True)
        r.sudo('chown -R {apache_web_user}:{apache_web_group} {maintenance_path}')

    @task
    def maint_down(self):
        """
        Removes down-for-maintenance splash page.
        """
        r = self.local_renderer
        r.sudo('[ -f {maintenance_path} ] && rm -f {maintenance_path} || true')

    @task(precursors=['packager', 'user', 'hostname', 'ip'])
    def configure(self):
        self.configure_modevasive()
        self.configure_modsecurity()
        self.configure_modrpaf()
        self.configure_site(full=1, site=ALL)
        self.install_auth_basic_user_file(site=ALL)
        self.sync_media()
        self.install_ssl(site=ALL)


apache = ApacheSatchel()
