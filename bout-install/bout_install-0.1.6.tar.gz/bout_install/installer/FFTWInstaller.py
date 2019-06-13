from pathlib import Path
from bout_install.Installer import Installer


class FFTWInstaller(Installer):
    """
    Installer object for installing FFTW
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=Path(__file__).parents[1].joinpath('log', 'fftw.log'),
                 overwrite_on_exist=False):
        """
        Gets the FFTW version, sets the FFTW url and calls the super constructor

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

        self.fftw_version = self.config['versions']['fftw']
        self.fftw_url = f'http://www.fftw.org/fftw-{self.fftw_version}.tar.gz'
        self.file_from_make = self.local_dir.joinpath('bin', 'fftw-wisdom')

    def install(self):
        """
        Installs the FFTW package
        """

        self.logger.info('Installing FFTW')
        self.install_package(url=self.fftw_url,
                             file_from_make=self.file_from_make,
                             overwrite_on_exist=self.overwrite_on_exist)
        self.logger.info('Installation completed successfully')
