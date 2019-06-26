import sys
import pexpect
from .file_transfer import FileTransfer
from .log import Logger

class RsyncLib(FileTransfer):
    '''
    Class to perform file transfer using rsync.
    Expected structure of settings:
    settings = {
        'source_path' : '',
        'remote_host' : '', #Username@ip
        'destination_path' : '',
        'options_optional' : '',
        'password_optional' : '',
    }
    '''

    connect = None
    get_delta = None


    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: Flag, success/failure message
    #    Desc: This function is used to validate settings passed for file
    #          transfer using rsync.
    # -------------------------------------------------------------------------
    def verify_settings(self, settings):
        flag, message = super(RsyncLib, self).verify_settings(settings)
        if flag:
            if len(settings["options_optional"].strip()) == 0 or settings["options_optional"] is None:
                settings["options_optional"] = "avpPz"
            return True, "SUCCESS"
        else:
            return False, message

    # -------------------------------------------------------------------------
    #    Args: command - string command used for rsync
    #          remote_host - remote host parameter from settings
    #          password - password if required to connect to remote host
    # Returns: Flag, success/failure message
    #    Desc: Method to execute rsync command, handle if password is required.
    # -------------------------------------------------------------------------
    def _execute_command(self, command, remote_host, password):
        try:
            child = pexpect.spawn(command)
            is_waiting = child.expect([remote_host, "password:", pexpect.EOF], timeout=60*30)
            if is_waiting == 0 or is_waiting == 1:
                child.sendline(password)
                child.expect(pexpect.EOF)
                return True, "Rsync was successful"

            if is_waiting == 2:
                return True, "Rsync was successful"

        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: Flag, success/failure message
    #    Desc: This function is used to receive files and / or directories
    #          using rsync.
    # -------------------------------------------------------------------------
    def get(self, settings):
        try:
            flag, message = self.verify_settings(settings)
            if not flag:
                return flag, message

            command = "rsync -{} {}:{} {}".format(settings['options_optional'], settings['remote_host'], settings['source_path'], settings['destination_path'])
            flag, message = self._execute_command(command, settings['remote_host'], settings['password_optional'])
            return flag, message

        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: Flag, success/failure message
    #    Desc: This function is used to send files and / or directories
    #          using rsync.
    # -------------------------------------------------------------------------
    def put(self, settings):
        try:
            flag, message = self.verify_settings(settings)
            if not flag:
                return flag, message

            command = "rsync -{} {} {}:{}".format(settings['options_optional'], settings['source_path'], settings['remote_host'], settings['destination_path'])

            flag, message = self._execute_command(command, settings['remote_host'], settings['password_optional'])

            return flag, message

        except Exception as e:
            return False, e.__str__()
    
