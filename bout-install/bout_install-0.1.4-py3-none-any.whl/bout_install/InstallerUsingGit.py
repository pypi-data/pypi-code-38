import shutil
from pathlib import Path
from bout_install.Installer import Installer


class InstallerUsingGit(Installer):
    """
    An Installer class which installs using git rather than tarballs
    """

    def __init__(self,
                 name,
                 section,
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
        section : str
            What section to use in the config file
        config_path : Path or str
            The path to the get_configure_command file
        log_path : None or Path or str
            Path to the log file containing the log of Installer.
            If None, the log will directed to stderr
        """

        super().__init__(config_path=config_path, log_path=log_path)

        # Obtain install dirs
        git_dir = self.config[section]['git_dir']
        checkout = self.config[section]['checkout']

        if git_dir == '':
            self.git_dir = Path().home().joinpath(name)
        else:
            self.git_dir = Path(git_dir)

        self.checkout = checkout if checkout != '' else 'master'

    def make(self, path):
        """
        Make the package

        Notes
        -----
        Will not make install

        Parameters
        ----------
        path : Path or str
            Path to the get_configure_command file
        """

        make_str = 'make'
        self.run_subprocess(make_str, path)

    def run_git(self, url, overwrite_on_exist=False):
        """
        Runs git

        Parameters
        ----------
        url : str
            URL to the package repository
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        if not self.git_dir.is_dir() or overwrite_on_exist:
            if self.git_dir.is_dir():
                shutil.rmtree(str(self.git_dir))
            command = f'git clone {url} {self.git_dir}'
            self.run_subprocess(command, self.git_dir.parent)

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
            Url to the package repository
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

        # Run git checkout
        self.run_git(url, overwrite_on_exist)

        # Configure and make
        config_log_path = self.git_dir.joinpath(path_config_log)
        self.run_configure(self.git_dir,
                           config_log_path,
                           extra_config_option,
                           overwrite_on_exist)
        self.run_make(self.git_dir, file_from_make, overwrite_on_exist)
