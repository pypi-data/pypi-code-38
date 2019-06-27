#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
from .console import EndlessConsole, Console
import logging
from . import config
import importlib
from datetime import datetime

class Docs():
    """
    Handle documentation operations
    @see https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__endless_command_running = False
        self.__endless_command_return_code = 0
        self.__module_version = None
        self.__module_author = None

    def __console_callback(self, stdout, stderr):
        self.logger.info((stdout if stdout is not None else '') + (stderr if stderr is not None else ''))

    def __console_end_callback(self, return_code, killed):
        self.__endless_command_running = False
        self.__endless_command_return_code = return_code

    def __get_module_data(self, module_name):
        """
        Return useful module data

        Returns:
            dict of data::

                {
                    version (string): module version
                    author (string): module author
                }

        """
        if self.__module_version:
            return {
                'version': self.__module_version,
                'author': self.__module_author
            }

        try:
            module_ = importlib.import_module(u'raspiot.modules.%s.%s' % (module_name, module_name))
            module_class_ = getattr(module_, module_name.capitalize())
            self.__module_version = module_class_.MODULE_VERSION
            self.__module_author = module_class_.MODULE_AUTHOR
            return {
                'version': self.__module_version,
                'author': self.__module_author
            }
        except:
            self.logger.exception('Unable to get module infos. Is module valid?')
            return None

    def generate_module_docs(self, module_name, preview=False):
        """
        Generate module documentation

        Args:
            module_name (string): module name
            preview (bool): preview generated documentation as text
        """
        #checking module path
        path = os.path.join(config.MODULES_SRC, module_name, 'docs')
        if not os.path.exists(path):
            self.logger.error('Docs directory for module "%s" does not exist' % (module_name))
            return False

        module_data = self.__get_module_data(module_name)
        self.logger.debug('Module data: %s' % module_data)
        if module_data is None:
            return False

        today = datetime.today()

        self.logger.info('Generating documentation...')
        cmd = """
cd "%(DOCS_PATH)s"
/bin/rm -rf "%(BUILD_DIR)s" "%(SOURCE_DIR)s"
/usr/local/bin/sphinx-apidoc -o "%(SOURCE_DIR)s/" "../backend"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "Building html documentation..."
/usr/local/bin/sphinx-build -M html "." "%(BUILD_DIR)s" -D project="%(MODULE_NAME_CAPITALIZED)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "Building text documentation..."
/usr/local/bin/sphinx-build -M text "." "%(BUILD_DIR)s" -D project="%(MODULE_NAME_CAPITALIZED)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "Packaging html documentation..."
/usr/bin/find "%(BUILD_DIR)s/" -type f -print0 | xargs -0 sed -i "s/backend/%(MODULE_NAME)s/g"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
/usr/bin/find "%(BUILD_DIR)s/" -type f -print0 | xargs -0 sed -i "s/Backend/%(MODULE_NAME_CAPITALIZED)s/g"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
/usr/bin/find "%(BUILD_DIR)s/" -iname \*.* | rename -v "s/backend/%(MODULE_NAME)s/g"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
#/bin/tar -czvf "%(MODULE_NAME)s-docs.tar.gz" "%(BUILD_DIR)s/html" --transform='s/%(BUILD_DIR)s\//\//g' && ARCHIVE=`/usr/bin/realpath "%(MODULE_NAME)s-docs.tar.gz"` && echo "ARCHIVE=$ARCHIVE"
cd "_build"; /usr/bin/zip "../%(MODULE_NAME)s-docs.zip" -r "html"; cd ..
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
/bin/cp -a "%(BUILD_DIR)s/text/source/%(MODULE_NAME)s.txt" "%(MODULE_NAME)s-docs.txt"
%(DISPLAY_TEXT)s
        """ % {
            'DOCS_PATH': path,
            'SOURCE_DIR': 'source',
            'BUILD_DIR': '_build',
            'MODULE_NAME': module_name,
            'MODULE_NAME_CAPITALIZED': module_name.capitalize(),
            'YEAR': today.year,
            'AUTHOR': module_data['author'],
            'VERSION': module_data['version'],
            'DISPLAY_TEXT': 'echo; echo; echo "========== DOC PREVIEW =========="; echo; cat "%s-docs.txt"' % module_name if preview else '',
        }

        self.logger.debug('Docs cmd: %s' % cmd)
        self.__endless_command_running = True
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        return True

    def get_module_docs_archive_path(self, module_name):
        """
        Display module docs archive path if exists
        """
        #checking module path
        docs_path = os.path.join(config.MODULES_SRC, module_name, 'docs')
        if not os.path.exists(docs_path):
            self.logger.error('Docs directory for module "%s" does not exist' % (module_name))
            return False

        zip_path = os.path.join(docs_path, '%s-docs.zip' % module_name)
        if not os.path.exists(zip_path):
            self.logger.error('There is no documentation archive generated for module "%s"' % (module_name))
            return False

        self.logger.info('DOC_ARCHIVE=%s' % zip_path)
        return True

