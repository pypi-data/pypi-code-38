#!/usr/bin/env python

import os
import inspect
import platform
import subprocess
from pwd import getpwnam as userinfo
import logging
import logging.handlers


url_bashrc = 'https://s3.us-east-2.amazonaws.com/awscloud.center/files/bashrc'
url_aliases = 'https://s3.us-east-2.amazonaws.com/awscloud.center/files/bash_aliases'
url_colors = 'https://s3.us-east-2.amazonaws.com/awscloud.center/files/colors.sh'

package_list = ['distro']


def download(url_list):
    """
    Retrieve remote file object
    """
    def exists(object):
        if os.path.exists(os.getcwd() + '/' + filename):
            return True
        else:
            msg = 'File object %s failed to download to %s. Exit' % (filename, os.getcwd())
            logger.warning(msg)
            return False
    try:

        for url in url_list:

            if which('wget'):
                cmd = 'wget ' + url
                p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
                r = p.communicate()[0]
                logger.info('Downloading... \n{}'.format(r))

            elif which('curl'):
                cmd = 'curl -o ' + os.path.basename(url) + ' ' + url
                p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
                r = p.communicate()[0]
                logger.info('Downloading... \n{}'.format(r))

            else:
                logger.info('Failed to download {} no url binary found'.format(os.path.basename(url)))
                return False

    except Exception as e:
        logger.info(
            'Error downloading file: {}, URL: {}'.format(os.path.basename(url), url)
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
    syslog_format = '- %(pathname)s - %(name)s - [%(levelname)s]: %(message)s'

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
        return distribution.linux_distribution()[0]


def local_profile_setup():
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
        return False

    try:
        os.chdir(home_dir)

        filename = '.bashrc'
        if download([url_bashrc]):
            logger.info('Download of {} successful to {}'.format(filename, home_dir))
            os.rename(os.path.split(url_bashrc)[1], filename)
            os.chown(filename, groupid, userid)
            os.chmod(filename, 0o700)

        filename = '.bash_aliases'
        if download([url_aliases]):
            logger.info('Download of {} successful to {}'.format(filename, home_dir))
            os.rename(os.path.split(url_aliases)[1], '.bash_aliases')
            os.chown(filename, groupid, userid)
            os.chmod(filename, 0o700)

        filename = 'colors.sh'
        destination = home_dir + '/.config/bash'
        if download([url_colors]):
            logger.info('Download of {} successful to {}'.format(filename, home_dir))

            if not os.path.exists(destination):
                os.makedirs(destination)
            os.rename(filename, destination + '/' + filename)
            os.chown(filename, groupid, userid)
            os.chmod(filename, 0o700)
    except OSError as e:
        logger.exception(
            'Unknown problem downloading or installing local user profile artifacts')
        return False
    return True


def package_check(binary, pkg):
    """Checks if pip package installed"""
    cmd = binary + ' list | grep ' + pkg
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    r = p.communicate()[0]

    if r:
        logger.info('python package installed, output: {}'.format(r))
        return True
    logger.warning('python package ({}) not installed'.format(pkg))
    return False


def prerun(packages):
    """Installs dependent packages"""
    if which('pip'):
        bin = 'pip'
    elif which('pip2.7'):
        bin = 'pip2.7'
    else:
        logger.warning('Failed to find pip binary when installing dep python packages')
        return False
    for pkg in packages:
        cmd = bin + ' install ' + pkg + ' --user'
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        r = p.communicate()[0]
        logger.info(r)
        if package_check(bin, pkg) and pkg == 'distro':
            global distribution
            distribution = __import__(pkg)
    return True


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file


# --- main -----------------------------------------------------------------------------------------


# setup logging facility
logger = getLogger('1.0')

prerun(package_list)

if platform.system() == 'Linux':
    logger.info('Operating System type identified: Linux, {}'.format(os_type()))
    local_profile_setup()
else:
    logger.info('Operating System type identified: {}'.format(os_type()))
