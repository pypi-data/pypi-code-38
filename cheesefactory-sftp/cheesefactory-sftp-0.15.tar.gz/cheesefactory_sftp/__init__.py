# __init__.py
__authors__ = ["tsalazar"]
__version__ = "0.11"

# v0.1 (tsalazar) -- Stand-alone SFTP package, split from cheesefactory package.
# v0.2 (tsalazar) -- 2018/08/18 Removed misplaced __connect() in __init__()
# v0.3 (tsalazar) -- 2018/08/22 Converted to dataframe.  Updated docstrings.
# v0.4 (tsalazar) -- 2018/09/29 Added regex to filter out files during walktree()
# v0.5 (tsalazar) -- 2018/10/01 Added callback for directory during walktree()
# v0.6 (tsalazar) -- 2018/10/05 Added is_dir() check during walktree()
# v0.7 (tsalazar) -- 2018/10/06 Fixed recursion problems for file/dir creation during walktree()
# v0.8 (tsalazar) -- 2018/10/10 Added ability to remove source file after successful get()
# v0.9 (tsalazar) -- 2018/10/16 Added ability to remove source file after successful get()
# v0.10 (tsalazar) -- 2019/01/27 Added put_new_files()
# v0.11 (tsalazar -- 2019/06/25 Moved from re.match to re.search


import logging
import pysftp
import pysftp.exceptions
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class SFTP:
    """Methods for interacting with an SFTP server.

    host: SFTP server hostname or IP.
    port: SFTP server port.
    username: SFTP server account username.
    password: SFTP server account password.
    """

    host: str = '127.0.0.1'
    port: str = '22'
    username: str = None
    password: str = None
    _local_directory: Path = Path('/')    # Default local directory for transferred files.
    _remote_directory: Path = Path('/')   # Default remote directory to get files from.
    _new_file_count: int = 0              # Counter to determine total number of new files received.
    _existing_file_count: int = 0         # Counter to determine total number of files not transferred.
    _ignore_regex: str = None             # String regex used to ignore files when performing walktree()
    _remove_source: bool = False

    def __post_init__(self):

        self.__logger = logging.getLogger(__name__)

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  # Accept unknown hostkeys

        # Establish SFTP connection
        self.__sftp_connection = pysftp.Connection(
            self.host,
            port=int(self.port),
            username=self.username,
            password=self.password,
            cnopts=cnopts
        )

        self.__logger.info(f'SFTP connection established to: {self.host}')

    @property
    def status(self):
        if self.__sftp_connection.exists('/etc/hosts'):
            return f'Connected to {self.username}@{self.host}:{self.port}{self._remote_directory}'
        else:
            return 'Not connected.'

    def get(self, filename: str=None, local_directory: str='/', remote_directory: str='/', remove_source: bool=False):
        """Download a file from an SFTP server.

        :param filename: The name of the file to download.
        :param local_directory: The local directory to download the file into.
        :param remote_directory: Remote SFTP directory.
        :param remove_source: Remove source file after successful get()
        """
        try:
            with self.__sftp_connection.cd(remote_directory):
                self.__sftp_connection.get(
                    filename,
                    localpath=f'{local_directory}/{filename}'
                )
                if remove_source is True or self._remove_source is True:
                    self.__sftp_connection.remove(filename)

            self.__logger.info(f'File retrieved: {remote_directory}/{filename} to {local_directory}.')

        except ValueError:
            self.__logger.critical(f'Problem encountered when retrieving file: {remote_directory}/{filename}')
            exit(1)

    def put(self, filename: str=None, confirm: bool=True, remote_directory: str='/'):
        """Upload a file to an SFTP server.

        :param filename: The name of the file to upload.
        :param confirm: Confirm that the transfer was successful using stat().
        :param remote_directory: Remote SFTP directory.
        """
        try:
            with self.__sftp_connection.cd(remote_directory):
                self.__sftp_connection.put(
                    filename,
                    confirm=confirm
                )
            self.__logger.info(f'File put: {remote_directory}/{filename}')

        except ValueError:
            self.__logger.critical('Problem encountered when uploading file.')
            exit(1)

    def get_new_files(self, remote_directory: str='/', local_directory: str='/', recursive: bool=True,
                      ignore_regex: str=None, remove_source: bool=False):
        """Get all unretrieved files from remote SFTP directory

        :param remote_directory: Remote SFTP directory.
        :param local_directory: Local directory to copy the files to.
        :param recursive: Recursively search for new files.
        :param ignore_regex: A regex string used to filter out unwanted files and paths.
        :param remove_source: Remove source file after successful get()
        """
        self._ignore_regex = ignore_regex
        self.__sftp_connection.cd(remote_directory)
        self._remote_directory = Path(remote_directory)
        self._local_directory = Path(local_directory)
        self._remove_source = remove_source

        # Create the local directory if it does not exist
        self._local_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.__logger.info(f'Retrieving new files from remote directory: {str(self._remote_directory)}')
        self.__sftp_connection.walktree(
            str(self._remote_directory),
            self.__is_this_a_new_file,       # file
            self.__is_this_a_new_directory,  # directory
            self.__is_this_a_new_file,       # unknown
            recursive
        )
        self.__logger.info(f'{str(self._new_file_count)} files retrieved')
        self.__logger.info(f'{str(self._existing_file_count)} files already existed.  Skipped.')

    def __is_this_a_new_directory(self, directory: str):
        """Test to see if the current directory exists.  If not, then create it.

        :param directory:  Directory to test for.
        """
        full_dir_path: Path = self._local_directory.joinpath(directory[1:])  # Remove first "/" for joinpath()
        self.__logger.debug(f'full_dir_path being tested: {str(full_dir_path)}')

        if full_dir_path.is_dir():
            self.__logger.debug(f'Directory exists: {str(full_dir_path)}')
        else:
            full_dir_path.mkdir(parents=True, exist_ok=True)
            self.__logger.info(f'Created directory: {str(full_dir_path)}')

    def __is_this_a_new_file(self, filename: str):
        """Test to see if the current file has been retrieved yet.

        :param filename:  File to test for.
        """
        remote_file: Path = self._remote_directory.joinpath(filename)
        local_file: Path = self._local_directory.joinpath(filename[1:])  # Remove first "/" for joinpath()

        if self._ignore_regex is not None and re.search(self._ignore_regex, str(remote_file)):
            self.__logger.debug(f'Remote file ignored: {str(remote_file)} (regex: {self._ignore_regex})')

        elif local_file.exists():
            self.__logger.debug(f'File exists: {str(local_file)} -- Skipping.')
            self._existing_file_count += 1

        else:
            self.__logger.debug(f'File not found: {str(local_file)} -- Transferring.')
            self.get(
                filename=remote_file.name,
                local_directory=str(local_file.parent),
                remote_directory=str(remote_file.parent)
            )
            self._new_file_count += 1
            self.__logger.info(f'Retrieved file: {str(remote_file)}')

    def put_new_files(self, local_path_list: List=None, remote_directory: str=None,
                      transfer_file: str='.transferred'):
        """Find files that have not yet been pushed and then push them.

        :param local_path_list: A list of local files that need to be transferred if they haven't already been.
        :param remote_directory: The remote directory that untransferred files need to be uploaded to.
        :param transfer_file: A local file that keeps a list of all transferred files.
        """
        with open(transfer_file, 'r') as fp:
            transfer_file_list = fp.readlines()
            self.__logger.debug(f'{transfer_file} opened. Contents read into transfer_file_list.')

        with open(transfer_file, 'w') as fp:
            for local_path in local_path_list:
                if local_path not in transfer_file_list:
                    self.put(filename=local_path, remote_directory=remote_directory)
                    fp.write(local_path)
                    self.__logger.debug(f'Uploaded file and updated {transfer_file}: {local_path}')
                else:
                    self.__logger.debug(f'File already uploaded: {local_path}')

    def close(self):
        """Close a connection to an SFTP server."""
        try:
            self.__sftp_connection.close()
        except ConnectionError:
            self.__logger.critical('Problem closing connection.')
            exit(1)
