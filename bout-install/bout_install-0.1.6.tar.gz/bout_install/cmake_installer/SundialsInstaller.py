from pathlib import Path
from bout_install.InstallerUsingCMake import InstallerUsingCMake


class SundialsInstaller(InstallerUsingCMake):
    """
    Installer object for installing Sundials
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=Path(__file__).parents[1].joinpath('log',
                                                             'sundials.log'),
                 overwrite_on_exist=False):
        """
        Gets the Sundials version, sets the url and calls the super constructor

        Parameters
        ----------
        config_path : Path or str
            The path to the get_configure_command file
        log_path : None or Path or str
            Path to the log file containing the log of Installer.
            If None, the log will directed to stderr
            Whether to overwrite the package if it is already found
        """

        self.overwrite_on_exist = overwrite_on_exist

        super().__init__(config_path=config_path, log_path=log_path)

        self.sundials_version = self.config['versions']['sundials']
        self.sundials_url = (f'http://computation.llnl.gov/projects/'
                             f'sundials/download/'
                             f'sundials-{self.sundials_version}.tar.gz')

        self.file_from_make = self.local_dir.joinpath('lib',
                                                      'libsundials_cvode.a')

        self.extra_config_options = \
            {'DEXAMPLES_INSTALL_PATH': str(self.examples_dir),
             'DOPENMP_ENABLE': 'ON',
             'DMPI_ENABLE': 'ON',
             'DCMAKE_LINKER': f'{self.local_dir.joinpath("lib")}',
             'DBUILD_SHARED_LIBS': 'OFF'}

    def install(self):
        """
        Installs the Sundials package
        """

        self.logger.info('Installing Sundials')
        self.install_package(url=self.sundials_url,
                             file_from_make=self.file_from_make,
                             extra_cmake_option=self.extra_config_options,
                             overwrite_on_exist=self.overwrite_on_exist)
        self.logger.info('Installation completed successfully')
