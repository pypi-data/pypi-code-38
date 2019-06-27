#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from .console import Console
import logging
from . import config

class Git():
    """
    Git commands
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def __get_private_repo_git_command(self):
        if not config.PRIVATE_REPO:
            return ''
        dir_name = os.path.dirname(os.path.realpath(__file__))
        return 'GIT_ASKPASS=%s' % os.path.join(dir_name, 'git_password.sh')

    def pull_core(self):
        """
        Pull core content
        """
        self.logger.info('Pulling core repository...')
        c = Console()
        cmd = 'cd "%s"; %s git pull -q' % (config.REPO_DIR, self.__get_private_repo_git_command())
        self.logger.debug('cmd: %s' % cmd)
        resp = c.command(cmd, 60)
        self.logger.debug('Pull resp: %s' % resp)
        if resp['error'] or resp['killed']:
            self.logger.error('Error occured while pulling repository: %s' % ('killed' if resp['killed'] else resp['stderr']))
            return False

        if not os.path.exists(os.path.join(config.REPO_DIR, 'modules')):
            os.mkdir(os.path.join(config.REPO_DIR, 'modules'))

        self.logger.info('Done')
        return True

    def clone_core(self):
        """
        Clone core content from official repository
        """
        #clone repo
        self.logger.info('Cloning core repository...')
        c = Console()
        url = config.REPO_PRIVATE_URL if config.PRIVATE_REPO else config.REPO_PUBLIC_URL
        cmd = '%s git clone -q "%s" "%s"' % (self.__get_private_repo_git_command(), url, config.REPO_DIR)
        self.logger.debug('cmd: %s' % cmd)
        resp = c.command(cmd, 60)
        self.logger.debug('Clone resp: %s' % resp)
        if resp['error'] or resp['killed']:
            self.logger.error('Error occured while cloning repository: %s' % ('killed' if resp['killed'] else resp['stderr']))
            return False
        
        if not os.path.exists(os.path.join(config.REPO_DIR, 'modules')):
            os.mkdir(os.path.join(config.REPO_DIR, 'modules'))

        self.logger.info('Done')
        return True

