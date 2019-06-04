# =============================================================================
# Module: file_transfer.py
# Contacts: Punit Kenia (ardentisys-Punit)
#           Insight Reduced Team
# =============================================================================
'''
Class which contains common functionalities for transfering files
via rsync, sftp.
'''

import os
from abc import ABCMeta
from abc import abstractmethod

class FileTransfer(metaclass=ABCMeta):

    @abstractmethod
    def verify_settings(self, settings):
        try:
            for key, val in settings.items():
                if key.endswith("optional") == 1:
                    continue
                if len(val.strip()) == 0 or val is None:
                    message = "Field: {0} field is not populated".format(key)
                    return False, message
            else:
                return True, None
        except Exception as e:
            return False, e.__str__()

    @abstractmethod
    def connect(self, settings):
        '''
        Method to establish connection.
        '''
        raise NotImplementedError("connect method not defined")

    @abstractmethod
    def get_delta(self, settings):
        '''
        Method to get files or directories received post the specific period of time from the specified source.
        '''
        raise NotImplementedError("get_delta method not defined")

    @abstractmethod
    def get(self, settings):
        '''
        Method to get files and directories from the specified source.
        '''
        raise NotImplementedError("get method not defined")

    @abstractmethod
    def put(self, settings):
        '''
        Method to put all the files from local machine to destination.
        '''
        raise NotImplementedError("put method not defined")
