from pathlib import Path
from bout_install.Installer import Installer


class GCCInstaller(Installer):
    """
    Installer object for installing GCC
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=Path(__file__).parents[1].joinpath('log', 'gcc.log'),
                 overwrite_on_exist=False):
        """
        Gets the GCC version, sets the GCC url and calls the super constructor

        Parameters
        ----------
        config_path : Path or str
            The path to the get_configure_command file
        log_path : None or Path or str
            Path to the log file containing the log of Installer.
            If None, the log will directed to stderr
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        self.overwrite_on_exist = overwrite_on_exist

        super().__init__(config_path=config_path, log_path=log_path)

        self.gcc_version = self.config['versions']['gcc']
        self.gcc_url = (f'http://mirror.koddos.net/gcc/releases/'
                        f'gcc-{self.gcc_version}/gcc-{self.gcc_version}.tar.gz')
        self.file_from_make = self.local_dir.joinpath('bin', 'gcc')

    def install_package(self,
                        url,
                        file_from_make,
                        path_config_log='config.log',
                        overwrite_on_exist=False,
                        extra_config_option=None):
        """
        Installs GCC if it's not installed

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
            --prefix=self.local_dir is already added as an option

        References
        ----------
        http://luiarthur.github.io/gccinstall
        """

        # Download the tar file
        tar_file_path = self.get_tar_file_path(url)
        self.run_download_tar(url, tar_file_path, overwrite_on_exist)

        # Untar
        tar_dir = self.get_tar_dir(tar_file_path)
        self.run_untar(tar_file_path, tar_dir, overwrite_on_exist)

        # Download prerequisites
        self.logger.info('Downloading prerequisites')
        prereq_path = Path('contrib').joinpath('download_prerequisites')
        self.run_subprocess(f'./{prereq_path}', tar_dir)

        # Configure and make
        config_log_path = tar_dir.joinpath(path_config_log)
        self.run_configure(tar_dir,
                           config_log_path,
                           extra_config_option,
                           overwrite_on_exist)
        self.run_make(tar_dir, file_from_make, overwrite_on_exist)

    def install(self):
        """
        Installs the GCC package
        """

        self.logger.info('Installing GCC')
        self.install_package(url=self.gcc_url,
                             file_from_make=self.file_from_make,
                             overwrite_on_exist=self.overwrite_on_exist)
        self.logger.info('Installation completed successfully')
