'''
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
'''

import logging
import os
from abc import ABCMeta

from jsoncfg.functions import save_config, ConfigWithWrapper

logger = logging.getLogger(__name__)


class PeekFileConfigABC(metaclass=ABCMeta):
    """
    This class creates a basic agent configuration
    """

    DEFAULT_FILE_CHMOD = 0o600
    DEFAULT_DIR_CHMOD = 0o700

    __instance = None

    def __new__(cls):
        if cls.__instance is not None:
            return cls.__instance

        self = super(PeekFileConfigABC, cls).__new__(cls)
        cls.__instance = self
        return self

    def __init__(self):
        '''
        Constructor
        '''
        from peek_platform import PeekPlatformConfig
        assert PeekPlatformConfig.componentName is not None

        self._homePath = os.path.join(
            os.path.expanduser('~'),
            '%s.home' % PeekPlatformConfig.componentName)

        if not os.path.isdir(self._homePath):
            assert (not os.path.exists(self._homePath))
            os.makedirs(self._homePath, self.DEFAULT_DIR_CHMOD)

        self._configFilePath = os.path.join(self._homePath, 'config.json')

        if not os.path.isfile(self._configFilePath):
            assert (not os.path.exists(self._configFilePath))
            with open(self._configFilePath, 'w') as fobj:
                fobj.write('{}')

        self._cfg = ConfigWithWrapper(self._configFilePath)

        self._hp = '%(' + self._homePath + ')s'

    def _save(self):
        save_config(self._configFilePath, self._cfg)

    def _chkDir(self, path):
        if not os.path.isdir(path):
            assert not os.path.exists(path)
            os.makedirs(path, self.DEFAULT_DIR_CHMOD)
        return path
