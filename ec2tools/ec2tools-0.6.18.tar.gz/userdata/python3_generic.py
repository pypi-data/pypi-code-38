#!/usr/bin/env python3
"""
Summary.

    Advanced EC2 userdata configuration script

TODO:
    1. download os_distro.sh from s3
    2. install os_distro.sh >> ~/.config/bash dir
    3. run yum update AFTER installing python3 with amazon-linux-extras utility
    4. run chown -R ec2-user:ec2-user ~/.config to flip ownership to user from root

"""

import os
import sys
import json
import inspect
import platform
import subprocess
import urllib
from pwd import getpwnam as userinfo
from shutil import which
import logging
import logging.handlers
import distro


map_url = 'https://s3.us-east-2.amazonaws.com/http-imagestore/ec2tools/config/s3map.json'
url_bashrc = 'https://s3.us-east-2.amazonaws.com/http-imagestore/ec2tools/config/bash/bashrc'
url_aliases = 'https://s3.us-east-2.amazonaws.com/http-imagestore/ec2tools/config/bash/bash_aliases'
url_colors = 'https://s3.us-east-2.amazonaws.com/http-imagestore/ec2tools/config/bash/colors.sh'
s3_origin = 'https://s3.us-east-2.amazonaws.com/http-imagestore/ec2tools'

homedir_files = ['bashrc', 'bash_aliases']

config_bash_files = [
    'colors.sh',
    'loadavg-flat-layout.sh',
    'os_distro.sh'
]


def directory_operations(path, groupid, userid, permissions):
    """
    Summary.

        Recursively sets owner and permissions on all file objects
        within path given as a parameter

    Args:
        path (str):  target directory
        userid (integer):  os identifier for user
        groupid (integer):  os identifier for user group membership
        permissions:  octal permissions (example: 0644)

    """
    for root, dirs, files in os.walk(path):
        for d in dirs:
            try:
                os.chmod(os.path.join(root, d), permissions)
                logger.info('Changed permissions on fs object {} to {}'.format(d, permissions))

                os.chown(os.path.join(root, d), groupid, userid)
                logger.info('Changed owner on fs object {} to {}'.format(d, userid))
            except OSError as e:
                fx = inspect.stack()[0][3]
                logger.exception(
                    '{}: Error during owner or perms reset on fs object {}:\n{}'.format(fx, d, e))
                continue

        for f in files:
            try:
                os.chmod(os.path.join(root, f), permissions)
                logger.info('Changed permissions on fs object {} to {}'.format(f, permissions))
                os.chown(os.path.join(root, f), groupid, userid)
                logger.info('Changed owner on fs object {} to {}'.format(f, userid))
            except OSError as e:
                fx = inspect.stack()[0][3]
                logger.exception(
                    '{}: Error during owner or perms reset on fs object {}:\n{}'.format(fx, f, e))
                continue
    return True


def download(url_list):
    """
    Retrieve remote file object
    """
    def exists(fname):
        if os.path.exists(os.getcwd() + '/' + fname):
            return True
        else:
            msg = 'File object %s failed to download to %s. Exit' % (fname, os.getcwd())
            logger.warning(msg)
            return False
    try:
        for url in url_list:

            if which('wget'):
                cmd = 'wget ' + url
                subprocess.getoutput(cmd)
                logger.info("downloading " + url)

            elif which('curl'):
                cmd = 'curl -o ' + os.path.basename(url) + ' ' + url
                subprocess.getoutput(cmd)
                logger.info("downloading " + url)

            else:
                logger.info('Failed to download {} no url binary found'.format(os.path.basename(url)))
                return False
    except Exception as e:
        logger.info(
            'Error downloading file: {}, URL: {}, Error: {}'.format(os.path.basename(url), url, e)
        )
        return False
    return True


def getLogger(*args, **kwargs):
    """
    Summary:
        custom format logger

    Args:
        mode (str):  The Logger module supprts the following log modes:
            - log to system logger (syslog)

    Returns:
        logger object | TYPE: logging
    """
    syslog_facility = 'local7'
    syslog_format = '[INFO] - %(pathname)s - %(name)s - [%(levelname)s]: %(message)s'

    # all formats
    asctime_format = "%Y-%m-%d %H:%M:%S"

    # objects
    logger = logging.getLogger(*args, **kwargs)
    logger.propagate = False

    try:
        if not logger.handlers:
            # branch on output format, default to stream
            sys_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=syslog_facility)
            sys_formatter = logging.Formatter(syslog_format)
            sys_handler.setFormatter(sys_formatter)
            logger.addHandler(sys_handler)
            logger.setLevel(logging.DEBUG)
    except OSError as e:
        raise e
    return logger


class S3Map():
    """Dict mapping download artifacts to localhost destinations"""
    def __init__(self, s3_urlpath):
        self.map = self._construct_map(s3_urlpath)

    def _construct_map(self, path):
        try:
            urllib.request.urlretrieve(path, 's3map.json')
            with open('s3map.json') as f1:
                s3map = json.loads(f1.read())
        except OSError:
            logger.exception('Failed to parse {}'.format(path))
        return s3map

    def download_artifacts(self):
        for k, v in self.map.items():
            fname = k
            src = v['source']
            dst = v['destination'] + '/' + fname
            try:
                urllib.request.urlretrieve(src, dst)
                if os.path.exists(dst):
                    logger.info('Successful download and placement of {}'.format(dst))
            except OSError as e:
                fx = inspect.stack()[0][3]
                logger.exception('Problem paring s3 map file: {}'.format(e))


def os_dependent():
    """Determine linux os distribution"""
    d = distro.linux_distribution()[0].lower()
    logger.info('Distro identified as {}'.format(d))

    if 'amazon' in d:
        return 'config-amazonlinux.conf'
    elif 'redhat' or 'rhel' in d:
        return 'config-redhat.config'
    elif 'ubuntu' in d:
        return 'config-redhat.config'
    return None


def os_type():
    """
    Summary.

        Identify operation system environment

    Return:
        os type (str) Linux | Windows
        If Linux, return Linux distribution
    """
    if platform.system() == 'Windows':
        return 'Windows'
    elif platform.system() == 'Linux':
        return 'Linux'


def local_profile_setup(distro):
    """Configures local user profile"""
    home_dir = None

    if os.path.exists('/home/ec2-user'):
        userid = userinfo('ec2-user').pw_uid
        groupid = userinfo('ec2-user').pw_gid
        home_dir = '/home/ec2-user'

    elif os.path.exists('/home/ubuntu'):
        userid = userinfo('ubuntu').pw_uid
        groupid = userinfo('ubuntu').pw_gid
        home_dir = '/home/ubuntu'

    elif os.path.exists('/home/centos'):
        userid = userinfo('centos').pw_uid
        groupid = userinfo('centos').pw_gid
        home_dir = '/home/centos'

    else:
        logger.warning('Unable to id home directory for regular user. Exit userdata configuration')
        return False

    try:

        os.chdir(home_dir)

        m = S3Map(map_url)

        for k, v in m.map.items():
            fname = k
            src = v['source']
            dst = v['destination'] + '/' + fname

            try:
                urllib.request.urlretrieve(src, dst)
                os.chown(dst, groupid, userid)
                os.chmod(dst, 0o644)

                if os.path.exists(dst):
                    logger.info('Successful download and placement of {}'.format(dst))
                else:
                    logger.warning('Failed to download and place {}'.format(dst))
            except OSError as e:
                logger.exception('Problem paring s3 map file: {}'.format(e))
                continue

        # reset owner to normal user for .config/bash (desination):
        directory_operations(home_dir, groupid, userid, 0o644)

        return True

    except OSError as e:
        logger.exception(
            'Unknown problem downloading or installing local user profile artifacts:\n{}'.format(e)
            )
        return False
    return True


# --- main -----------------------------------------------------------------------------------------


if __name__ == '__main__':
    # setup logging facility
    logger = getLogger('1.0')

    if platform.system() == 'Linux':
        logger.info('Operating System type identified: Linux, {}'.format(os_type()))

        try:

            linux_distro = distro.linux_distribution()[0].lower()
            logger.info('Linux distribution identified as {}'.format(linux_distro))

        except Exception:
            logger.exception('Unable to id distribution using python distro library')
            linux_distro = os_type()

        # start configuration
        local_profile_setup(linux_distro)
    else:
        logger.info('Operating System type identified: {}'.format(os_type()))

    sys.exit(0)
