#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from .console import Console
import logging
from . import config

class File():
    """
    Handle file operations
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def core_sync(self):
        """
        Synchronize core content between source and execution folders
        """
        self.logger.info('Synchronizing core files...')
        c = Console()
        cmd = """
/bin/mkdir -p "%(HTML_DST)s/"
/usr/bin/rsync -av "%(REPO_DIR)s/raspiot/" "%(CORE_DST)s/" --exclude "/tests/" --exclude "modules/**/" --delete --exclude "*.pyc"
/usr/bin/rsync -av "%(REPO_DIR)s/html/" "%(HTML_DST)s/" --delete --exclude "js/modules/"
/usr/bin/rsync -av "%(REPO_DIR)s/bin/raspiot" "%(BIN_DST)s/raspiot"
/usr/bin/rsync -av "%(REPO_DIR)s/medias/sounds" "%(MEDIA_DST)s/sounds/" --delete
    """ % {'REPO_DIR': config.REPO_DIR, 'CORE_DST': config.CORE_DST, 'HTML_DST':config.HTML_DST, 'BIN_DST':config.BIN_DST, 'MEDIA_DST':config.MEDIA_DST}
        self.logger.debug('Coresync cmd: %s' % cmd)
        resp = c.command(cmd, 15)
        self.logger.debug('Coresync response: %s' % resp)
        if resp['error'] or resp['killed']:
            self.logger.error('Error occured while sync core content: %s' % ('killed' if resp['killed'] else resp['stderr']))
            return False

        self.logger.info('Done')
        return True

    def module_sync(self, module_name):
        """ 
        Copy specified module content to valid execution location
        """
        self.logger.info('Synchronizing module "%s" files...' % module_name)
        if not os.path.exists(os.path.join(config.MODULES_SRC, module_name)):
            sys.exit('Module "%s" doesn\'t exist [%s]' % (module_name, os.path.join(config.MODULES_SRC, module_name)))
    
        if not os.path.exists(os.path.join(config.MODULES_DST, module_name)):
            os.mkdir(os.path.join(config.MODULES_DST, module_name))

        mod_backend_src = os.path.join(config.MODULES_SRC, module_name, 'backend/')
        mod_backend_dst = os.path.join(config.MODULES_DST, module_name)
        mod_frontend_src = os.path.join(config.MODULES_SRC, module_name, 'frontend/')
        mod_frontend_dst = os.path.join(config.MODULES_HTML_DST, module_name)
        mod_scripts_src = os.path.join(config.MODULES_SRC, module_name, 'scripts/')
        mod_scripts_dst = os.path.join(config.MODULES_SCRIPTS_DST, module_name)

        c = Console()
        cmd = """ 
if [ -d "%(BACKEND_SRC)s" ]; then
    /bin/mkdir -p "%(BACKEND_DST)s"
    rsync -av "%(BACKEND_SRC)s" "%(BACKEND_DST)s" --delete --exclude "*.pyc"
fi
if [ -d "%(FRONTEND_SRC)s" ]; then
    /bin/mkdir -p "%(FRONTEND_DST)s"
    rsync -av "%(FRONTEND_SRC)s" "%(FRONTEND_DST)s" --delete
fi
if [ -d "%(SCRIPTS_SRC)s" ]; then
    /bin/mkdir -p "%(SCRIPTS_DST)s"
    rsync -av "%(SCRIPTS_SRC)s" "%(SCRIPTS_DST)s" --delete
fi
    """ % { 
            'BACKEND_SRC': mod_backend_src, 'BACKEND_DST': mod_backend_dst,
            'FRONTEND_SRC': mod_frontend_src, 'FRONTEND_DST': mod_frontend_dst,
            'SCRIPTS_SRC': mod_scripts_src, 'SCRIPTS_DST': mod_scripts_dst
        }
        self.logger.debug('Modsync cmd: %s' % cmd)
        resp = c.command(cmd, 15) 
        #self.logger.debug('Modsync resp: %s' % resp)
        if resp['error'] or resp[u'killed']:
            self.logger.error(u'Error occured while sync module content: %s' % (u'killed' if resp[u'killed'] else resp[u'stderr']))
            return False

        self.logger.info('Done')
        return True

