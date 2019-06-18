"""
Wrapper around the Motion service.

http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome
"""
from __future__ import print_function
import re

import feedparser

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task

class SeleniumSatchel(Satchel):
    """
    Management commands for the Selenium browser automation and testing tool.

    http://www.seleniumhq.org/
    """

    name = 'selenium'

    def set_defaults(self):
        # See https://github.com/mozilla/geckodriver/releases for other versions and architectures.
        # If none provided, will track the most recent tagged release.
        self.env.geckodriver_version = None # '0.13.0'
        self.env.geckodriver_arch = 'linux64'
        self.env.geckodriver_url_template = \
            'https://github.com/mozilla/geckodriver/releases/download/' \
            'v{geckodriver_version}/geckodriver-v{geckodriver_version}-{geckodriver_arch}.tar.gz'
        self.env.geckodriver_install_bin_path = '/usr/local/bin'
        self.env.geckodriver_bin_name = 'geckodriver'
        #self.env.geckodriver_fingerprint_path = '/usr/local/lib/geckodriver/fingerprint.txt'
        self.env.geckodriver_feed = 'https://github.com/mozilla/geckodriver/tags.atom'

    @property
    def geckodriver_path(self):
        r = self.local_renderer
        return r.format('{geckodriver_install_bin_path}/{geckodriver_bin_name}')

    @task
    def install_geckodriver(self, version=None):
        r = self.local_renderer
        self.vprint('Checking geckdriver %s...' % r.env.geckodriver_version)
        r.env.geckodriver_version = version or r.env.geckodriver_version or self.get_target_geckodriver_version_number()
        self.vprint('Installing geckdriver %s...' % r.env.geckodriver_version)
        r.run(
            'cd /tmp; '
            'wget -O geckodriver.tar.gz {geckodriver_url_template}; '
            'tar -xvzf geckodriver.tar.gz')
        r.sudo('mv /tmp/{geckodriver_bin_name} {geckodriver_install_bin_path}')

    @task
    def uninstall_geckodriver(self):
        r = self.local_renderer
        r.sudo('rm -f {geckodriver_install_bin_path}/{geckodriver_bin_name}')

    @task
    def get_installed_version(self):
        r = self.local_renderer
        out = r.run('geckodriver --version') or ''
        print('out:', out)
        version = re.findall(r'geckodriver\s+([0-9\.]+)', out)
        if version:
            version = version[0]
            print('Geckodriver version %s found.' % version)
            return version
        print('Geckodriver is not installed.')

    @task
    def check_for_change(self):
        """
        Determines if a new release has been made.
        """
        r = self.local_renderer
        lm = self.last_manifest
        last_fingerprint = lm.fingerprint
        current_fingerprint = self.get_target_geckodriver_version_number()
        self.vprint('last_fingerprint:', last_fingerprint)
        self.vprint('current_fingerprint:', current_fingerprint)
        if last_fingerprint != current_fingerprint:
            print('A new release is available. %s' % self.get_most_recent_version())
            return True
        print('No updates found.')
        return False

    @task
    def get_most_recent_version(self):
        link = feedparser.parse(self.env.geckodriver_feed)['entries'][0]['link']
        self.vprint('link:', link)
        matches = re.findall(r'v([0-9]+.[0-9]+.[0-9]+)', link)
        if matches:
            version = matches[0]
            self.vprint('version:', version)
            return version

    @task
    def get_latest_geckodriver_version_number(self):
        """
        Retrieves the version number from the latest tagged release.
        """
        data = feedparser.parse(self.env.geckodriver_feed)
        from pprint import pprint
        print('feedparser for %s' % self.env.geckodriver_feed)
        pprint(data, indent=4)
        latest_url = data['entries'][0]['link']
        self.vprint('latest_url:', latest_url)
        version = latest_url.split('/')[-1][1:]
        self.vprint('version:', version)
        return version

    @task
    def get_target_geckodriver_version_number(self):
        return self.env.geckodriver_version or self.get_latest_geckodriver_version_number()

    def record_manifest(self):
        """
        Called after a deployment to record any data necessary to detect changes
        for a future deployment.
        """
        manifest = super(SeleniumSatchel, self).record_manifest()
        manifest['fingerprint'] = str(self.get_target_geckodriver_version_number())
        return manifest

    @task(precursors=['packager'])
    def configure(self):
        if self.env.enabled:
            self.install_geckodriver()
        else:
            self.uninstall_geckodriver()

selenium = SeleniumSatchel()
