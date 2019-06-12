import configparser
import logging
import os
import requests
import shutil
import subprocess
import tarfile
from pathlib import Path


class Installer(object):
    """
    Class for building packages from scratch

    This class serves as the top-most parent class for most of the installer
    classes.

    Contains member functions for
    * Downloading a tar file for a package
    * Untar the downloaded tar file for the package
    * Configure the package
    * Making the package (including make install)

    Examples
    --------
    The following example will install FFTW.
    See also the examples of the child-classes of the Installer

    >>> from bout_install.Installer import Installer
    >>>
    >>> # Instantiate the installer
    >>> installer = Installer()
    >>>
    >>> # Get the fftw-version from the configuration
    >>> fftw_version = installer.config['versions']['fftw']
    >>> fftw_url = f'http://www.fftw.org/fftw-{fftw_version}.tar.gz'
    >>>
    >>> bin_file = installer.local_dir.joinpath('bin', 'fftw-wisdom')
    >>>
    >>> # Install FFTW
    >>> installer.install_package(fftw_url, bin_file)
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=None):
        """
        Makes the logger and installation paths (obtained from config.ini)

        Notes
        -----
        `self.local_dir.joinpath('bin')` will be set to the environments
        `PATH` variable and `self.local_dir.joinpath('lib')` will be set to the
        environments `LD_LIBRARY_PATH` variable in order to ensure a proper
        installation

        Parameters
        ----------
        config_path : Path or str
            The path to the get_configure_command file
        log_path : None or Path or str
            Path to the log file containing the log of Installer.
            If None, the log will directed to stderr
        """

        self.config = configparser.ConfigParser(allow_no_value=True)
        with Path(config_path).open() as f:
            self.config.read_file(f)

        # Set input
        self.log_path = log_path

        # Obtain install options
        self.use_preinstalled = \
            self.config.getboolean('install_options', 'use_preinstalled')
        main_dir = self.config['install_options']['main_dir']
        install_dir = self.config['install_options']['install_dir']
        local_dir = self.config['install_options']['local_dir']
        examples_dir = self.config['install_options']['examples_dir']

        self.main_dir = main_dir if main_dir != '' else None
        self.install_dir = install_dir if install_dir != '' else None
        self.local_dir = local_dir if local_dir != '' else None
        self.examples_dir = examples_dir if examples_dir != '' else None

        # Setup the install dirs
        self.setup_install_dirs(main_dir=self.main_dir,
                                install_dir=self.install_dir,
                                local_dir=self.local_dir,
                                examples_dir=self.examples_dir)

        # Set the environment variables
        # Set the local path first
        os.environ['PATH'] = (f'{self.local_dir.joinpath("bin")}'
                              f'{os.pathsep}'
                              f'{os.environ["PATH"]}')
        if 'LD_LIBRARY_PATH' not in os.environ:
            os.environ['LD_LIBRARY_PATH'] = f'{self.local_dir.joinpath("lib")}'
        else:
            os.environ['LD_LIBRARY_PATH'] = (f'{self.local_dir.joinpath("lib")}'
                                             f'{os.pathsep}'
                                             f'{os.environ["LD_LIBRARY_PATH"]}')

        # Declare other class variables
        self.config_log_path = None

        # Setup the logger
        self._setup_logger()

    def _setup_logger(self):
        """
        Sets up the logger instance.
        """
        formatter = logging.Formatter('[{asctime}][{levelname:<7}] {message}',
                                      style='{')

        if self.log_path is not None:
            log_path = Path(self.log_path).absolute()
            log_dir = log_path.parent
            log_dir.mkdir(exist_ok=True, parents=True)
            handler = logging.FileHandler(str(log_path))
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(formatter)

        self.logger = logging.getLogger('bout_install')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def setup_install_dirs(self,
                           main_dir=None,
                           install_dir=None,
                           local_dir=None,
                           examples_dir=None):
        """
        Set the install directories for the packages

        Parameters
        ----------
        main_dir : None or str or Path
            The super directory of install_dir, local_dir and example_dir
            (if not set).
            If None, the home directory will be used.
            install_dir, local_dir and example_dir have precedence over main_dir
        install_dir : None or str or Path
            The directory to put the files to install from.
             If None, the directory will be made under main_dir
        local_dir : None or str or Path
            The directory to put the installed files.
             If None, the directory will be made under main_dir
        examples_dir : None or str or Path
            The directory to put the examples (needed for installing ffmpeg).
            If None, the directory will be made under main_dir
        """

        if main_dir is None:
            self.main_dir = Path(__file__).home().absolute()
        else:
            self.main_dir = Path(main_dir).absolute()

        if install_dir is None:
            self.install_dir = self.main_dir.joinpath('install')
        else:
            self.install_dir = Path(install_dir).absolute()

        if local_dir is None:
            self.local_dir = self.main_dir.joinpath('local')
        else:
            self.local_dir = Path(local_dir).absolute()

        if examples_dir is None:
            self.examples_dir = self.main_dir.joinpath('examples')
        else:
            self.examples_dir = Path(examples_dir).absolute()

        # Make the directories
        if not (install_dir is None and
                local_dir is None and
                examples_dir is None):
            self.main_dir.mkdir(parents=True, exist_ok=True)

        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.examples_dir.mkdir(parents=True, exist_ok=True)

    def get_tar_file(self, url):
        """
        Obtain a tar file from url

        Parameters
        ----------
        url : str
            The url to get the tar file from
        """

        try:
            response = requests.get(url, stream=True)
        except requests.exceptions.SSLError:
            msg = (f'SSL error occurred in {url}, trying to download without '
                   f'SSL verification. Use with care!')
            self.logger.warning(msg)
            response = requests.get(url, stream=True, verify=False)

        response.raise_for_status()

        tar_file_path = self.get_tar_file_path(url)

        with tar_file_path.open('wb') as f:
            # Decode in case transport encoding was applied
            # https://stackoverflow.com/questions/32463419/having-trouble-getting-requests-2-7-0-to-automatically-decompress-gzip
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

    def get_tar_file_path(self, url):
        """
        Returns the path to the tar file

        Parameters
        ----------
        url : str
            The url to get the tar file from

        Returns
        -------
        tar_file_path : Path
            The path to the tar file
        """

        # The file name is the last part of the url
        file_name = url.split('/')[-1]
        tar_file_path = self.install_dir.joinpath(file_name)
        return tar_file_path

    @staticmethod
    def untar(tar_path):
        """
        Untar a tar file

        Parameters
        ----------
        tar_path : str or Path
            Tar file to extract
        """

        tar_path = Path(tar_path).absolute()
        tar_extract_dir = tar_path.parent

        tar = tarfile.open(tar_path)
        tar.extractall(path=tar_extract_dir)
        tar.close()

    @staticmethod
    def get_tar_dir(tar_path):
        """
        Returns the path to the tar directory (directory of untarred files)

        Parameters
        ----------
        tar_path : str or Path
            Path to tar file

        Returns
        -------
        tar_dir : Path
            The untarred directory
        """

        dir_name = Path(tarfile.open(tar_path).getnames()[0]).parts[0]
        tar_dir = Path(tar_path).absolute().parent.joinpath(dir_name)
        return tar_dir

    @staticmethod
    def get_configure_command(config_options=None):
        """
        Get the command to configure the package

        Parameters
        ----------
        config_options : dict
            Configuration options to use with `./configure`.
            The configuration options will be converted to `--key=val` during
            runtime

        Returns
        -------
        config_str : str
            The configuration command
        """

        options = ''
        if config_options is not None:
            for key, val in config_options.items():
                if val is not None:
                    options += f' --{key}={val}'
                else:
                    options += f' --{key}'

        config_str = f'./configure{options}'
        return config_str

    def run_subprocess(self, command, path):
        """
        Run a subprocess

        Parameters
        ----------
        command : str
            The command to run
        path : Path or str
            Path to the location to run the command from
        """

        result = subprocess.run(command.split(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=path)

        if result.returncode != 0:
            self._raise_subprocess_error(result)

    def make(self, path):
        """
        Make the package

        Parameters
        ----------
        path : Path or str
            Path to the get_configure_command file
        """

        make_str = 'make'
        self.run_subprocess(make_str, path)

        make_install_str = 'make install'
        self.run_subprocess(make_install_str, path)

    def run_download_tar(self, url, tar_file_path, overwrite_on_exist):
        """
        Downloads the tar-file if not found

        Parameters
        ----------
        url : str
            The url to download the tar-file from
        tar_file_path : Path
            Path to the tar file
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        if not tar_file_path.is_file() or overwrite_on_exist:
            self.logger.info(f'Downloading {url}')
            self.get_tar_file(url)
        else:
            self.logger.info(f'{tar_file_path} found, skipping download')

    def run_untar(self, tar_file_path, tar_dir, overwrite_on_exist):
        """
        Untars the tar file

        Parameters
        ----------
        tar_file_path : Path
            Path to the tar file
        tar_dir : Path
            Directory to the tar file
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        if not tar_dir.is_dir() or overwrite_on_exist:
            self.logger.info(f'Untarring {tar_file_path}')
            self.untar(tar_file_path)
        else:
            self.logger.info(f'{tar_dir} found, skipping untarring')

    def run_configure(self,
                      tar_dir,
                      config_log_path,
                      extra_config_option,
                      overwrite_on_exist):
        """
        Configures the package

        Parameters
        ----------
        tar_dir : Path
            Directory of the tar file
        config_log_path : Path
            Path to the Makefile
        extra_config_option:
            Configure option to include.
            --prefix=self.local_dir is already added as an option
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        if not config_log_path.is_file() or overwrite_on_exist:
            config_options = dict(prefix=str(self.local_dir))
            if extra_config_option is not None:
                config_options = {**config_options, **extra_config_option}

            config_str = \
                self.get_configure_command(config_options=config_options)

            self.logger.info(f'Configuring with: {config_str}')
            self.run_subprocess(config_str, tar_dir)
        else:
            self.logger.info(f'{config_log_path} found, skipping configuring')

    def run_make(self, tar_dir, file_from_make, overwrite_on_exist):
        """
        Runs make and make install

        Parameters
        ----------
        tar_dir : Path
            Directory of the tar file
        file_from_make : Path or str
            File originating from the make processes (used to check if the
            package has been made)
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        if not file_from_make.is_file() or overwrite_on_exist:
            self.logger.info(f'Making (including make install)')
            self.make(tar_dir)
        else:
            self.logger.info(f'{file_from_make} found, skipping making')

    def install_package(self,
                        url,
                        file_from_make,
                        path_config_log='config.log',
                        overwrite_on_exist=False,
                        extra_config_option=None):
        """
        Installs a package if it's not installed

        Parameters
        ----------
        url : str
            Url to the tar file of the package
        file_from_make : Path or str
            File originating from the make processes (used to check if the
            package has been made)
        path_config_log : str or Path
            Name of the log file for configure relative to the configuration
            file
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        extra_config_option : dict
            Configure option to include.
            The installation prefix of self.local_dir is already added as an
            option
        """

        # Download the tar file
        tar_file_path = self.get_tar_file_path(url)
        self.run_download_tar(url, tar_file_path, overwrite_on_exist)

        # Untar
        tar_dir = self.get_tar_dir(tar_file_path)
        self.run_untar(tar_file_path, tar_dir, overwrite_on_exist)

        # Configure and make
        config_log_path = tar_dir.joinpath(path_config_log)
        self.run_configure(tar_dir,
                           config_log_path,
                           extra_config_option,
                           overwrite_on_exist)
        self.run_make(tar_dir, file_from_make, overwrite_on_exist)

    def _raise_subprocess_error(self, result):
        """
        Raises errors from the subprocess in a clean way

        Parameters
        ----------
        result : subprocess.CompletedProcess
            The result from the subprocess
        """

        self.logger.error('Subprocess failed with stdout:')
        self.logger.error(result.stdout)
        self.logger.error('and stderr:')
        self.logger.error(result.stderr)

        result.check_returncode()
