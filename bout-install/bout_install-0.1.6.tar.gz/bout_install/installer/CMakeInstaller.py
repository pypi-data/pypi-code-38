from pathlib import Path
from bout_install.Installer import Installer


class CMakeInstaller(Installer):
    """
    Installer object for installing CMake
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=Path(__file__).parents[1].joinpath('log',
                                                             'cmake.log'),
                 overwrite_on_exist=False):
        """
        Gets the CMake version, sets the CMake url, calls the super constructor

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

        self.cmake_version = self.config['versions']['cmake']
        cmake_major_minor_version = '.'.join(self.cmake_version.split('.')[:2])
        self.cmake_url = (f'http://cmake.org/files/'
                          f'v{cmake_major_minor_version}/'
                          f'cmake-{self.cmake_version}.tar.gz')

        self.file_from_make = self.local_dir.joinpath('bin', 'cmake')

    def run_configure(self,
                      tar_dir,
                      config_log_path,
                      extra_config_option,
                      overwrite_on_exist):
        """
        Configures the package with the bootstrap script

        Parameters
        ----------
        tar_dir : Path
            Directory of the tar file
        config_log_path : Path
            Path to config.log
        extra_config_option:
            Configure option to include.
            --prefix=self.local_dir is already added as an option
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        # The bootstrap of CMake does not necessarily create a config.log
        # file, but it will at least create a Makefile which didn't exist before

        make_path = Path(config_log_path).parent.joinpath('Makefile')

        if not make_path.is_file() or overwrite_on_exist:
            config_options = dict(prefix=str(self.local_dir))
            if extra_config_option is not None:
                config_options = {**config_options, **extra_config_option}
            self.logger.info(f'Configuring with options {config_options}')
            config_str = \
                self.get_configure_command(config_options=config_options)

            # Calling the bootstrap script rather than configure
            config_str = config_str.replace('configure', 'bootstrap')
            self.run_subprocess(config_str, tar_dir)
        else:
            self.logger.info(f'{make_path} found, skipping configuring')

    def install(self):
        """
        Installs the CMake package
        """

        self.logger.info('Installing CMake')
        self.install_package(url=self.cmake_url,
                             file_from_make=self.file_from_make,
                             overwrite_on_exist=self.overwrite_on_exist)
        self.logger.info('Installation completed successfully')
