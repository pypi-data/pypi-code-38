
import requests
import json
from distutils.version import LooseVersion

from osnap import get_logger, __application_name__
from osnap import init_logger, __version__

log = get_logger(__application_name__)


class AppUpdaterBaseClass:
    def __init__(self, application_name, author, this_version):
        """
        updates an osnap application using a .zip of an osnapp dir
        :param application_name: name of the application to update
        :param author: author string, e.g. github account name
        :param this_version: version string of the currently running version
        """
        self.application_name = application_name
        self.author = author
        self.this_version = this_version

    def get_update_file_name(self, version_to_download):
        # derived class provides this
        raise NotImplementedError

    def get_download_url(self, version_to_download):
        # derived class provides this
        raise NotImplementedError

    def is_update_available(self):
        """
        Check if an update to this application is available.

        :return: True if update available, False if app is current, None if could not be accessed
        """
        latest_version = self._get_latest_version()
        if latest_version:
            update_available = LooseVersion(latest_version) > LooseVersion(self.this_version)
        else:
            log.info('could not get latest version')
            update_available = None
        log.info('this_version=%s , latest_version=%s' % (self.this_version, latest_version))
        sha256, size = self._get_sha256_and_size()
        return update_available, latest_version, sha256, size

    def _get_latest_version(self):
        # users of this class should not call this directly - use is_update_available() to get the latest version
        # derived classes provide this
        raise NotImplementedError

    def _get_sha256_and_size(self):
        return 'tbdsha256', 8675309


class AppUpdaterGithub(AppUpdaterBaseClass):
    """
    get latest version from github.com and github LFS
    """
    def __init__(self, application_name, author, this_version):
        super().__init__(application_name, author, this_version)
        self.tags_domain = 'https://api.github.com'
        self.download_domain = 'https://github.com'

    def get_update_file_name(self, version_to_download):
        return '%s_update_%s.zip' % (self.application_name, version_to_download)

    def get_download_url(self, version_to_download):
        # https://github.com/jamesabel/propmtime/raw/master/installers/propmtime_installer.exe
        download_url = '%s/%s/%s/raw/master/installers/%s' % \
                       (self.download_domain, self.author, self.application_name,
                        self.get_update_file_name(version_to_download))
        log.info('download_url : %s' % download_url)
        return download_url

    def _get_latest_version(self):
        tags_url = '%s/repos/%s/%s/tags' % (self.tags_domain, self.author, self.application_name)
        log.info('getting list of release versions (tags) from %s' % tags_url)
        tags = None
        latest_version = None
        try:
            tags = json.loads(requests.get(tags_url).text)
        except requests.exceptions.ConnectionError as e:
            error_message = 'ConnectionError:%s' % str(e)
            log.info(error_message)
        if tags:
            log.debug(tags)
            try:
                latest_version = tags[0]['name'].replace('v', '')  # vx.y.z is OK, but convert it to x.y.z
            except KeyError as e:
                log.info('could not get tags from %s (tags=%s)' % (tags_url, tags))
                error_message = 'KeyError : %s' % str(e)
                log.info(error_message)
                latest_version = None
        return latest_version


class AppUpdaterGithubEmulationLocal(AppUpdaterGithub):
    """
    access the local test server for updates
    """
    def __init__(self, application_name, author, this_version):
        super().__init__(application_name, author, this_version)
        self.tags_domain = 'http://localhost:55016'  # see osnaptest.test


def main():
    # use osnaptest for this test example
    application = 'osnaptest'
    author = 'jamesabel'  # github account name
    version = '0.0.0'  # fake to always show there's a new version
    init_logger(application, author, 'temp', True, delete_existing_log_files=True)
    if False:
        app_updater = AppUpdaterGithub(application, author, version)
    else:
        app_updater = AppUpdaterGithubEmulationLocal(application, author, version)
    is_update_available, latest_version = app_updater.is_update_available()
    log.info('is_update_available : %s , latest_version : %s' % (is_update_available, latest_version))


if __name__ == '__main__':
    main()
