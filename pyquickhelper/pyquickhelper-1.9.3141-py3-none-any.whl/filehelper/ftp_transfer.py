"""
@file
@brief provides some functionalities to upload file to a website
"""
from ftplib import FTP, error_perm
import os
import sys
import time
import datetime
from io import BytesIO
from ..loghelper.flog import noLOG


class CannotReturnToFolderException(Exception):
    """
    raised when a transfer is interrupted by an exception
    and the class cannot return to the original folder
    """
    pass


class CannotCompleteWithoutNewLoginException(Exception):
    """
    raised when a transfer is interrupted by a new login
    """
    pass


class TransferFTP:

    """
    this class uploads files to a website,
    if the remote does not exists, it creates it first

    .. exref::
        :title: Transfer files to webste through FTP

        Simple sketch to transfer a list of ``files`` to
        a website through FTP

        ::

            ftp = TransferFTP('ftp.<website>', alias, password, fLOG=print)

            issues = [ ]
            done = [ ]
            notdone = [ ]
            for file in files :

                try :
                    r = ftp.transfer (file, path)
                    if r : done.append( (file, path) )
                    else : notdone.append ( (file, path) )
                except Exception as e :
                    issues.append( (file, e) )

            try :
                ftp.close()
            except Exception as e :
                print ("unable to close FTP connection using ftp.close")
    """

    errorNoDirectory = "Can't change directory"
    blockSize = 2 ** 20

    def __init__(self, site, login, password, fLOG=noLOG):
        """
        constructor

        @param      site        website
        @param      login       login
        @param      password    password
        @param      fLOG        logging function
        """
        if site is not None:
            self._ftp = FTP(site, login, password)
            self._logins = [(datetime.datetime.now(), site)]
        else:
            # mocking
            self._logins = []
            self._ftp = FTP(site)
        self.LOG = fLOG
        self._atts = dict(site=site, login=login, password=password)

    @property
    def Site(self):
        """
        return the website
        """
        return self._atts["site"]

    def _private_login(self):
        """
        logs in
        """
        self.LOG("reconnecting to ", self.Site, " - ", len(self._logins))
        try:
            self._ftp.login()
            self._logins.append((datetime.datetime.now(), self.Site))
        except Exception as e:
            se = str(e)
            if "You're already logged in" in se:
                return
            elif "An existing connection was forcibly closed by the remote host" in se or \
                 "An established connection was aborted by the software in your host machine" in se:
                # it starts a new connection
                self.LOG("reconnecting failed, starting a new connection",
                         self.Site, " - ", len(self._logins))
                self._ftp = FTP(self.Site, self._atts[
                                "login"], self._atts["password"])
                self._logins.append((datetime.datetime.now(), self.Site))
            else:
                raise e

    def run_command(self, command, *args):
        """
        run a FTP command

        @param      command     command
        @param      args        list of argument
        @return                 output of the command or True for success, False for failure
        """
        try:
            t = command(*args)
            if command == self._ftp.pwd or command == self._ftp.dir or \
                    command == self._ftp.mlsd or command == self._ftp.nlst:
                return t
            elif command != self._ftp.cwd:
                pass
            return True
        except Exception as e:
            if TransferFTP.errorNoDirectory in str(e):
                raise e
            self.LOG(e)
            self.LOG("    ** run exc ", str(command), str(args))
            self._private_login()
            if command == self._ftp.pwd or command is self._ftp.pwd:
                t = command(self)
            else:
                t = command(self, *args)
            self.LOG("    ** run ", str(command), str(args))
            return t

    def print_list(self):
        """
        return the list of files in the current directory
        the function sends eveything to the logging function

        @return         output of the command or True for success, False for failure
        """
        return self.run_command(self._ftp.retrlines, 'LIST')

    def mkd(self, path):
        """
        creates a directory

        @param        path      path to the directory
        @return                 True or False
        """
        self.LOG("[mkd]", path)
        return self.run_command(self._ftp.mkd, path)

    def cwd(self, path, create=False):
        """
        go to a directory, if it does not exist, create it
        (if create is True)

        @param      path        path to the directory
        @param      create      True to create it
        @return                 True or False
        """
        try:
            self.run_command(self._ftp.cwd, path)
        except EOFError as e:
            raise EOFError("unable to go to: {0}".format(path)) from e
        except Exception as e:
            if create and TransferFTP.errorNoDirectory in str(e):
                self.mkd(path)
                self.cwd(path, create)
            else:
                raise e

    def pwd(self):
        """
        Return the pathname of the current directory on the server.

        @return         pathname
        """
        return self.run_command(self._ftp.pwd)

    def dir(self, path='.'):
        """
        Lists the content of a path.

        @param      path        path
        @return                 list of path

        See :meth:`enumerate_ls <pyquickhelper.filehelper.ftp_transfer.TransferFTP.enumerate_ls>`
        """
        return list(self.enumerate_ls(path))

    def ls(self, path='.'):
        """
        list the content of a path

        @param      path        path
        @return                 list of path

        see :meth:`enumerate_ls <pyquickhelper.filehelper.ftp_transfer.TransferFTP.enumerate_ls>`

        .. exref::
            :title: List files from FTP site

            ::

                from pyquickhelper.filehelper import TransferFTP
                ftp = TransferFTP("ftp....", "login", "password")
                res = ftp.ls("path")
                for v in res:
                    print(v["name"])
                ftp.close()
        """
        return list(self.enumerate_ls(path))

    def enumerate_ls(self, path='.'):
        """
        enumerate the content of a path

        @param      path        path
        @return                 list of dictionaries

        One dictionary::

            {'name': 'www',
             'type': 'dir',
             'unique': 'aaaa',
             'unix.uid': '1111',
             'unix.mode': '111',
             'sizd': '5',
             'unix.gid': '000',
             'modify': '111111'}
        """
        for a in self.run_command(self._ftp.mlsd, path):
            r = dict(name=a[0])
            r.update(a[1])
            yield r

    def transfer(self, file, to, name, debug=False, blocksize=None, callback=None):
        """
        transfers a file

        @param      file        file name or stream (binary, BytesIO)
        @param      to          destination (a folder)
        @param      name        name of the stream on the website
        @param      debug       if True, displays more information
        @param      blocksize   see :tpl:`py,m='ftplib',o='FTP.storbinary'`
        @param      callback    see :tpl:`py,m='ftplib',o='FTP.storbinary'`
        @return                 status

        When an error happens, the original current directory is restored.
        """
        path = to.split("/")
        path = [_ for _ in path if len(_) > 0]
        nb_logins = len(self._logins)
        cpwd = self.pwd()

        done = []
        exc = None
        for p in path:
            try:
                self.cwd(p, True)
            except Exception as e:
                exc = e
                break
            done.append(p)

        if nb_logins != len(self._logins):
            raise CannotCompleteWithoutNewLoginException(
                "Cannot reach folder '{0}' without new login".format(to))

        bs = blocksize if blocksize else TransferFTP.blockSize
        if exc is None:
            try:
                if isinstance(file, str):
                    if not os.path.exists(file):
                        raise FileNotFoundError(file)
                    with open(file, "rb") as f:
                        r = self.run_command(
                            self._ftp.storbinary, 'STOR ' + name, f, bs, callback)
                elif isinstance(file, BytesIO):
                    r = self.run_command(self._ftp.storbinary, 'STOR ' +
                                         name, file, bs, callback)
                elif isinstance(file, bytes):
                    st = BytesIO(file)
                    r = self.run_command(self._ftp.storbinary, 'STOR ' +
                                         name, st, bs, callback)
                else:
                    r = self.run_command(self._ftp.storbinary, 'STOR ' +
                                         name, file, bs, callback)
            except Exception as ee:
                exc = ee

        if nb_logins != len(self._logins):
            try:
                self.cwd(cpwd)
                done = []
            except Exception as e:
                raise CannotCompleteWithoutNewLoginException(
                    "Cannot transfer '{0}' without new login".format(to))

        # It may fail here, it hopes not.
        nbtry = 0
        nbth = len(done) * 2 + 1
        while len(done) > 0:
            if nb_logins != len(self._logins):
                try:
                    self.cwd(cpwd)
                    break
                except Exception as e:
                    raise CannotCompleteWithoutNewLoginException(
                        "Cannot return to original folder'{0}' without new login".format(to)) from e

            nbtry += 1
            try:
                self.cwd("..")
                done.pop()
            except Exception as e:
                time.sleep(0.5)
                self.LOG(
                    "    issue with command .. len(done) == {0}".format(len(done)))
                if nbtry > nbth:
                    raise CannotReturnToFolderException(
                        "len(path)={0} nbtry={1} exc={2} nbl={3} act={4}".format(
                            len(done), nbtry, exc, nb_logins, len(self._logins))) from e

        if exc is not None:
            raise exc
        else:
            return r

    def retrieve(self, fold, name, file, debug=False):
        """
        downloads a file

        @param      file        file name or stream (binary, BytesIO)
        @param      fold        full remote path
        @param      name        name of the stream on the website
        @param      debug       if True, displays more information
        @return                 status
        """
        path = fold.split("/")
        path = [_ for _ in path if len(_) > 0]

        for p in path:
            self.cwd(p, True)

        raise_exc = None

        if isinstance(file, str):
            with open(file, "wb") as f:
                def callback(block):
                    f.write(block)
                try:
                    data = self.run_command(
                        self._ftp.retrbinary, 'RETR ' + name, callback, TransferFTP.blockSize)
                    f.write(data)
                    r = True
                except error_perm as e:
                    raise_exc = e
                    r = False
        elif isinstance(file, BytesIO):
            def callback(block):
                file.write(block)
            try:
                r = self.run_command(
                    self._ftp.retrbinary, 'RETR ' + name, callback, TransferFTP.blockSize)
            except error_perm as e:
                raise_exc = e
                r = False
        else:
            b = BytesIO()

            def callback(block):
                b.write(block)
            try:
                self.run_command(self._ftp.retrbinary, 'RETR ' + name,
                                 callback, TransferFTP.blockSize)
            except error_perm as e:
                raise_exc = e

            r = b.getvalue()

        for p in path:
            self.cwd("..")

        if raise_exc:
            raise raise_exc

        return r

    def close(self):
        """
        close the connection
        """
        self._ftp.close()
