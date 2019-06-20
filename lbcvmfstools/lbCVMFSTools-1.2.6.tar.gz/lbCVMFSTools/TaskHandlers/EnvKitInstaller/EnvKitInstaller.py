###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Tar installer
@author: Stefan-Gabriel CHITIC
'''
import logging
import os
import shutil
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
import tempfile
import subprocess
from lbmessaging.services.LbCIService import LbCIService

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface

FREQ = 0


class EnvKitInstaller(TaskHandlerInterface, object):

    def __init__(self, flavour, platform, version, url, installOnCvmfs=True,
                 *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(EnvKitInstaller, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        self.url = url
        self.flavour = flavour
        self.platform = platform
        self.root = '/'
        self.version = version
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        logging.getLogger().setLevel(logging.INFO)

    def get_list_of_tasks(self):
        if self.url == 'None':
            self.url = None
        url = LbCIService.getEnvKitUrl(self.flavour,
                                       self.platform,
                                       self.version,
                                       self.url)
        prefix = LbCIService.getEnvKitPrefix(self.flavour,
                                             self.platform)
        return [{
            'url': url,
            'root': self.root,
            'prefix': prefix,
        }]

    def _comnunicate(self, command):
        command = command.split(' ')
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed: %s" % (command, err))
        return out

    def perform_task(self, tasks):
        # Download the url
        url = tasks['url']
        dirpath = tempfile.mkdtemp()
        file_name = os.path.join(dirpath, url.split('/')[-1])
        logging.info("Downloading %s to %s" % (url, file_name))
        u = urlopen(url)
        with open(file_name, 'wb') as f:
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
        # Remove old path
        if tasks['prefix'].startswith('/'):
            tasks['prefix'] = tasks['prefix'][1:]
        remove_path = os.path.join(tasks['root'], tasks['prefix'])
        if os.path.exists(remove_path):
            shutil.rmtree(remove_path)
            logging.info("Removing path %s" % (remove_path))
        # Extract the url
        try:
            if not os.path.exists(tasks['root']):
                os.mkdir(tasks['root'])
            self._comnunicate(
                "tar -x -j --directory=%s -f %s" % (tasks['root'], file_name))
            logging.info("Successfully extracted %s to %s" % (file_name,
                                                              tasks['root']))
        except Exception as e:
            logging.error(e)
            raise Exception("Failed extracting %s to %s" % (file_name,
                                                            tasks['root']))
