from pathlib import Path
from bout_install.Installer import Installer
from bout_install.installer.PETScInstaller import PETScInstaller


class SLEPcInstaller(Installer):
    """
    Installer object for installing SLEPc
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 slepc_log_path=Path(__file__).parents[1].joinpath('log',
                                                                   'slepc.log'),
                 petsc_log_path=Path(__file__).parents[1].joinpath('log',
                                                                   'petsc.log'),
                 mpi_log_path=Path(__file__).parents[1].joinpath('log',
                                                                 'mpi.log'),
                 overwrite_on_exist=False):
        """
        Gets the SLEPc version, sets the SLEPc url and calls the super
        constructor

        Parameters
        ----------
        config_path : Path or str
            The path to the get_configure_command file
        slepc_log_path : None or Path or str
            Path to the log file for SLEPc
            If None, the log will directed to stderr
        petsc_log_path : None or Path or str
            Path to the log file for PETSc
            If None, the log will directed to stderr
        mpi_log_path : None or Path or str
            Path to the log file for MPI
            If None, the log will directed to stderr
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        self.overwrite_on_exist = overwrite_on_exist

        super().__init__(config_path=config_path, log_path=slepc_log_path)

        self.petsc_version = self.config['versions']['petsc']
        self.slepc_version = self.config['versions']['slepc']

        # Create dependency installer
        self.petsc = PETScInstaller(config_path=config_path,
                                    petsc_log_path=petsc_log_path,
                                    mpi_log_path=mpi_log_path)

        self.slepc_url = (f'http://slepc.upv.es/download/distrib/'
                          f'slepc-{self.slepc_version}.tar.gz')

        self.file_from_make = self.local_dir.joinpath('lib', 'libslepc.a')

    @staticmethod
    def get_configure_command(config_options=None):
        """
        Get the command to configure the package.

        Notes
        -----
        Configuring happens through python 2

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

        config_str = f'python2 ./configure{options}'
        return config_str

    def make(self, path):
        """
        Make the package using make all and make test

        Parameters
        ----------
        path : Path or str
            Path to the get_configure_command file
        """

        make_options = \
            (f'SLEPC_DIR={self.install_dir}/slepc-{self.slepc_version}'
             f' PETSC_DIR={self.local_dir}')

        make_str = f'make {make_options}'
        self.run_subprocess(make_str, path)

        make_install_str = f'make {make_options} install'
        self.run_subprocess(make_install_str, path)

        make_test_options =  \
            (f'SLEPC_DIR={self.local_dir}'
             f' PETSC_DIR={self.local_dir}'
             f' PETSC_ARCH=')
        make_test_str = f'make {make_test_options} check'
        self.run_subprocess(make_test_str, path)

    def install(self):
        """
        Installs the SLEPc package and its dependencies
        """

        self.install_dependencies()

        # Set config log path
        # NOTE: The configuration log is hiding in strange places in SLEPc,
        #       we'll therefore try to glob us to the configure.log
        tar_dir = Path(self.get_tar_file_path(self.slepc_url)).\
            absolute().parent.joinpath(f'slepc-{self.slepc_version}')
        path_config_logs = sorted(tar_dir.glob('**/configure.log'))
        if len(path_config_logs) == 0:
            # No configuration file found, might as well set it to configure.log
            path_config_log = 'configure.log'
        else:
            # Configuration files found, use the first
            path_config_log = path_config_logs[0]

        self.logger.info('Installing SLEPc')
        self.install_package(url=self.slepc_url,
                             file_from_make=self.file_from_make,
                             path_config_log=path_config_log,
                             overwrite_on_exist=self.overwrite_on_exist)
        self.logger.info('Installation completed successfully')

    def install_dependencies(self):
        """
        Installs SLEPc dependencies
        """

        self.petsc.install()
