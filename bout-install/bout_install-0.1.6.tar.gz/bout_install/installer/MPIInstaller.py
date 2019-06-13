import shutil
from pathlib import Path
from bout_install.Installer import Installer


class MPIInstaller(Installer):
    """
    Installer object for installing MPI
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=Path(__file__).parents[1].joinpath('log', 'mpi.log'),
                 overwrite_on_exist=False):
        """
        Gets the MPI version, sets the MPI url and calls the super constructor

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

        self.mpi_version = self.config['versions']['mpi']
        self.mpi_url = (f'http://www.mpich.org/static/downloads/'
                        f'{self.mpi_version}/mpich-{self.mpi_version}.tar.gz')
        self.file_from_make = self.local_dir.joinpath('bin', 'mpicxx')

    def install(self):
        """
        Installs the MPI package
        """

        self.logger.info('Installing MPI')

        if shutil.which('mpicxx') is None or not self.use_preinstalled:
            self.install_package(url=self.mpi_url,
                                 file_from_make=self.file_from_make,
                                 overwrite_on_exist=self.overwrite_on_exist)
            self.logger.info('Installation completed successfully')
        else:
            self.logger.info('mpicxx found in PATH, skipping...')
