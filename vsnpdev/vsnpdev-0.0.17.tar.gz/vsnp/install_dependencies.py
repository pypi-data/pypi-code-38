#!/usr/bin/env python3
import urllib.request
import logging
import tarfile
import os
__author__ = 'adamkoziol'


def install_deps(dependency_root):
    """
    Install the vSNP dependencies .tar.gz file from figshare
    :param dependency_root: type STR: Absolute path to the folder in which the dependencies are to be installed
    :return:
    """
    dep_tar = os.path.join(dependency_root, '14619260')
    logging.info('Dependency path not found. Downloading dependencies')
    urllib.request.urlretrieve('https://ndownloader.figshare.com/files/14619260',
                               dep_tar)
    tar = tarfile.open(dep_tar)
    tar.extractall(path=dependency_root)
    tar.close()
    os.remove(dep_tar)
