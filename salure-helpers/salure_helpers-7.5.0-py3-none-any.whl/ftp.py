import os
import ftplib
import io
import pandas as pd
import pysftp
from ftplib import FTP


class FTPS:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password


    def upload_file(self, local_path, filename, remote_path):
        """
        Upload a file from the client to another client or server
        :param local_path: the path where the upload file is located
        :param filename: The file which should be uploaded
        :param remote_path: The path on the destination client where the file should be saved
        :return: a status if the upload is succesfull or not
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            with open(local_path + filename, 'rb') as fp:
                res = ftp.storbinary("STOR " + filename, fp)
                ftp.close()
                return res



    def upload_multiple_files(self, local_path, remote_path):
        """
        Upload all files in a directory from the client to another client or server
        :param local_path: the path from where all the files should be uploaded
        :param remote_path: The path on the destination client where the file should be saved
        :return: a status if the upload is succesfull or not
        """
        ftp = FTP(host=self.host, user=self.username, passwd=self.password)
        ftp.cwd(remote_path)
        for filename in os.listdir(local_path):
            file = local_path + filename
            if os.path.isfile(file):
                with open(file, 'rb') as fp:
                    res = ftp.storbinary("STOR " + filename, fp)
        ftp.close()
        return 'All files are transfered'


    def download_file(self, local_path, remote_path, filename, remove_after_download=False):
        """
        Returns a single file from a given remote path
        :param local_path: the folder where the downloaded file should be stored
        :param remote_path: the folder on the server where the file should be downloaded from
        :param filename: the filename itself
        :param remove_after_download: Should the file be removed on the server after the download or not
        :return: a status
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            with open('{}/{}'.format(local_path, filename), 'wb') as fp:
                res = ftp.retrbinary('RETR {}/{}'.format(remote_path, filename), fp.write)
                if not res.startswith('226 Successfully transferred'):
                    # Remove the created file on the local client if the download is failed
                    if os.path.isfile('{}/{}'.format(local_path, filename)):
                        os.remove('{}/{}'.format(local_path, filename))
                else:
                    if remove_after_download:
                        ftp.delete(filename)

                return res

    def make_dir(self, dir_name):
        """
        Create a directory on a remote machine
        :param dir_name: give the path name which should be created
        :return: the status if the creation is successfull or not
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            status = ftp.mkd(dir_name)
            return status


    def list_directories(self, remote_path=''):
        """
        Give a NoneType of directories and files in a given directory. This one is only for information. The Nonetype
        can't be iterated or something like that
        :param remote_path: give the folder where to start in
        :return: a NoneType with folders and files
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            return ftp.dir()


    def list_files(self, remote_path=''):
        """
        Give a list with files in a certain folder
        :param remote_path: give the folder where to look in
        :return: a list with files
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            return ftp.nlst()


class SFTP:
    def __init__(self, host, username, local_base_dir, remote_base_dir, private_key=None, private_key_pass=None, password=None):
        self.host = host
        self.username = username
        self.private_key = private_key
        self.private_key_pass = private_key_pass
        self.password = password
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None
        self.remote_base_dir = remote_base_dir
        self.local_base_dir = local_base_dir


    def upload_file(self, local_path, remote_path):
        with pysftp.Connection(host=self.host, username=self.username, password=self.password, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            connection.put(local_path, remote_path)


    def download_file(self, file_name):
        with pysftp.Connection(host=self.host, username=self.username, password=self.password, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            with connection.cd(self.remote_base_dir):
                connection.get(file_name, self.local_base_dir)


    def make_dir(self, dir_name):
        with pysftp.Connection(host=self.host, username=self.username, password=self.password, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            with connection.cd(self.remote_base_dir):
                try:
                    connection.mkdir(dir_name)
                except OSError:
                    error_message = '%s already exists' % (self.remote_base_dir + dir_name)
                    raise OSError(error_message)


    def list_dir(self, remote_path_from_base=''):
        with pysftp.Connection(host=self.host, username=self.username, password=self.password, private_key=self.private_key,
                               private_key_pass=self.private_key_pass, cnopts=self.cnopts) as connection:
            with connection.cd(self.remote_base_dir + remote_path_from_base):
                return connection.listdir()

