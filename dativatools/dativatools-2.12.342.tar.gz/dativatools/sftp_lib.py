import glob
import os
import sys
from datetime import datetime, timedelta

from .file_transfer import FileTransfer
from .pysftp import Connection
from .log import Logger


class SFTPLib(FileTransfer):
    """
    Class which contains modules to connect and download or upload files using sftp connection.
    Expected structure of settings:
    settings = {
        'credentials' : {
            'remote_host': '',
            'user': '',
            'password_optional': '',
            'private_key_optional': '',
            'key_phrase_optional': '',
            'is_protected_optional':''
            },
        'get' : {
            'source_path': '',
            'destination_path': '',
            'days_optional': '1',
            'hours_optional': '0',
            'recursive': 'yes'
            },
        'put' : {
            'source_path': '',
            'destination_path': '',
            'recursive': 'yes'
        }
    }
    """

    # -------------------------------------------------------------------------
    #    Name: verify_settings()
    #    Args: settings - dictionary
    # Returns: boolean flag, None / message
    #    Desc: This function is used to verify settings passed for file transfer with the specified sftp server.
    #          Returns True and None on success else False and message.
    # -------------------------------------------------------------------------
    def verify_settings(self, settings):
        flag, message = super(SFTPLib, self).verify_settings(settings)
        if not flag:
            return False, message
        return True, None

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: boolean flag, None / message
    #    Desc: This function is used to verify credentials passed for setup
    #          connection with the specified sftp server.
    #          Returns True and None on success else False and message on failure.
    # -------------------------------------------------------------------------
    def verify_credentials(self, settings):
        if settings["credentials"]["password_optional"] is None and settings["credentials"]["private_key_optional"] is None:
            return False, "Password as well as Private Key path is missing"

        if settings["credentials"]["private_key_optional"] is not None and (settings["credentials"]["is_protected_optional"] == 'yes' and settings["credentials"]["key_phrase_optional"] is None):
            return False, "Passphrase is missing for key"

        return True, None

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: boolean flag, sftp connection object / message
    #    Desc: This function is used to setup connection with the specified sftp server.
    #          Returns True and sftp_connection on success else False and message on failure.
    # -------------------------------------------------------------------------
    def connect(self, settings):
        try:
            if bool(settings["password_optional"]):
                sftp_conn = Connection(host=settings["remote_host"], username=settings["user"], password=settings["password_optional"])
                return True, sftp_conn

            else:
                if bool(settings["private_key_optional"]) and settings["is_protected_optional"] == "yes":
                    sftp_conn = Connection(host=settings["remote_host"], username=settings["user"], private_key=settings["private_key_optional"], private_key_pass=settings["key_phrase_optional"])
                    return True, sftp_conn

                else:
                    sftp_conn = Connection(host=settings["remote_host"], username=settings["user"], private_key=settings["private_key_optional"])
                    return True, sftp_conn

        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: boolean flag, sftp connection object / message
    #    Desc: Helper method to get connection object.
    #          Returns True and connection object on success
    #          else False and message on failure.
    # -------------------------------------------------------------------------
    def get_connection(self, settings):
        # Verify credentials for sftp
        flag, message = self.verify_credentials(settings)
        if not flag:
            return flag, message

        # Setup connection
        flag, sftp_conn = self.connect(settings["credentials"])
        if not flag:
            return flag, sftp_conn
        
        return True, sftp_conn

    # -------------------------------------------------------------------------
    #    Args: source_path, path to check for existence
    #          action, get or put
    #          sftp_conn, connection to sftp server; None for put
    # Returns: boolean flag, sftp connection object / message
    #    Desc: Helper method to get connection object.
    #          Returns True and None on success else False and message on failure.
    # -------------------------------------------------------------------------
    def check_source(self, source_path, action, sftp_conn=None):
        if action == "get":
            if not sftp_conn.lexists(source_path):
                sftp_conn.close()
                msg = "{0} folder does not exists".format(source_path)
                return False, msg
        else:
            if not os.path.exists(source_path):
                msg = "{0} folder does not exists".format(source_path)
                return False, msg

        return True, None

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: delta date
    #    Desc: This function is used to get the delta datetime
    # -------------------------------------------------------------------------
    def get_delta_date(self, settings):
        timevalue = []
        timeunit = ['days', 'hours']
        timevalue.append(int(settings["get"]["days_optional"]))
        timevalue.append(int(settings["get"]["hours_optional"]))
        delta_date = datetime.now() - timedelta(**dict(zip(timeunit, timevalue)))
        return delta_date

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    #          sftp_conn - sftp connection object
    # Returns: boolean flag, None / message
    #    Desc: This function is used to receive files and / or directories
    #          using sftp which were added post the specified modified time.
    # -------------------------------------------------------------------------
    def _get_delta(self, settings, sftp_conn):
        try:
            # To get the delta values from the settings dictionary and calculate delta date
            delta_date  = self.get_delta_date(settings)

            if not sftp_conn.isfile(settings["get"]["source_path"]):
                files = sftp_conn.listdir(settings["get"]["source_path"])
            else:
                files = settings["get"]["source_path"]
            if isinstance(files, str):
                files = [files]

            for each in files:
                if (sftp_conn.isdir(os.path.join(settings["get"]["source_path"], each))) and settings["get"]["recursive"] != "yes":
                    continue
                # Get the modified time
                utime = sftp_conn.stat(os.path.join(settings["get"]["source_path"], each)).st_mtime
                last_modified = datetime.fromtimestamp(utime)
                # Calculate the time difference
                date_diff = datetime.now() - last_modified
                fdate = datetime.now() - date_diff
                # Look for modified time of the file and if it is within time range fetch the file
                if fdate > delta_date:
                    if sftp_conn.isfile(os.path.join(settings["get"]["source_path"], each)):
                        sftp_conn.get(os.path.join(settings["get"]["source_path"], each), os.path.join(settings["get"]["destination_path"], each), preserve_mtime=True)
                    else:
                        sftp_conn.get_r(os.path.join(settings["get"]["source_path"], each), settings["get"]["destination_path"], preserve_mtime=True)
            sftp_conn.close()
            return True, "File download completed"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: boolean flag, None / message
    #    Desc: This function is a wrapper function to receive files and / or directories
    #          from sftp server which were added post the specified modified time.
    # -------------------------------------------------------------------------
    def get_delta(self, settings):
        try:
            flag, message = self.verify_settings(settings["get"])
            if not flag:
                return flag, message

            if not os.path.exists(settings["get"]["destination_path"]):
                os.makedirs(settings["get"]["destination_path"])

            flag, message = self.get_connection(settings)
            if not flag:
                return flag, message
            
            sftp_conn = message
            flag, message = self.check_source(settings["get"]["source_path"], "get", sftp_conn)
            if not flag:
                return flag, message

            flag, message = self._get_delta(settings, sftp_conn)
            return flag, message

        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: boolean flag, None / message
    #    Desc: This function is used to receive files and / or directories
    #          using sftp.
    # -------------------------------------------------------------------------

    def _get(self, settings, sftp_conn):
        try:
            if settings["get"]["recursive"] == "no":
                if sftp_conn.isfile(settings["get"]["source_path"]):
                    sftp_conn.get(settings["get"]["source_path"], os.path.join(settings["get"]["destination_path"], settings["get"]["source_path"].split("/")[-1]), preserve_mtime=True)
                else:
                    sftp_conn.get_d(settings["get"]["source_path"], settings["get"]["destination_path"], preserve_mtime=True)
            else:
                sftp_conn.get_r(settings["get"]["source_path"], settings["get"]["destination_path"], preserve_mtime=True)

            sftp_conn.close()
            return True, "get operation was successful"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: boolean flag, None / message
    #    Desc: This function is a wrapper function to receive files and / or directories
    #          using sftp.
    # -------------------------------------------------------------------------
    def get(self, settings):
        try:
            flag, message = self.verify_settings(settings["get"])
            if not flag:
                return flag, message

            #self.logger_obj.info("Check if destination path exists.")
            if not os.path.exists(settings["get"]["destination_path"]):
                os.makedirs(settings["get"]["destination_path"])

            flag, message = self.get_connection(settings)
            if not flag:
                return flag, message
            
            sftp_conn = message
            flag, message = self.check_source(settings["get"]["source_path"], "get", sftp_conn)
            if not flag:
                return flag, message
            
            flag, message = self._get(settings, sftp_conn)
            return flag, message

        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: Flag, success/failure message
    #    Desc: This function is used to send files and / or directories
    #          using sftp.
    # -------------------------------------------------------------------------
    def _put(self, settings, sftp_conn):
        try:
            if settings["put"]["recursive"] == "no":
                if os.path.isfile(settings["put"]["source_path"]):
                    fname = settings["put"]["source_path"].split("/")[-1]
                    sftp_conn.put(localpath=settings["put"]["source_path"], remotepath=os.path.join(settings["put"]["destination_path"], fname), preserve_mtime=True)
                else:
                    files_list = [each for each in glob.glob(os.path.join(settings["put"]["source_path"], "*")) if os.path.isfile(each)]
                    for each in files_list:
                        fname = each.split("/")[-1]
                        sftp_conn.put(localpath=each, remotepath=os.path.join(settings["put"]["destination_path"], fname), preserve_mtime=True)
            else:
                sftp_conn.put_r(localpath=settings["put"]["source_path"], remotepath=settings["put"]["destination_path"], preserve_mtime=True)

            sftp_conn.close()
            return True, "put operation was successful"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: boolean flag, None / message
    #    Desc: This function is a wrapper function to send files and / or directories
    #          using sftp.
    # -------------------------------------------------------------------------
    def put(self, settings):
        try:
            flag, message = self.verify_settings(settings["put"])
            if not flag:
                return flag, message

            flag, message = self.check_source(settings["put"]["source_path"], "put")
            if not flag:
                return flag, message

            flag, message = self.get_connection(settings)
            if not flag:
                return flag, message
            sftp_conn = message

            flag, message = self._put(settings, sftp_conn)
            return flag, message 
          
        except Exception as e:
            return False, e.__str__()

