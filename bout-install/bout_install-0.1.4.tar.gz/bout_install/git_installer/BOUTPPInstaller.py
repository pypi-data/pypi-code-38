from pathlib import Path
from bout_install.InstallerUsingGit import InstallerUsingGit


class BOUTPPInstaller(InstallerUsingGit):
    """
    Installer object for installing BOUT++
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=Path(__file__).parents[1].joinpath('log',
                                                             'boutpp.log'),
                 overwrite_on_exist=False):
        """
        Gets the BOUT++ version, sets the BOUT++ url and calls the super
        constructor

        Notes
        -----
        The BOUTPPInstaller does not install its dependencies.
        See bout_install.main.install_bout for installation of dependencies

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
        section = 'bout_options'
        name = 'BOUT-dev'

        super().__init__(name,
                         section,
                         config_path=config_path,
                         log_path=log_path)

        self.boutpp_url = 'https://github.com/boutproject/BOUT-dev.git'
        self.file_from_make = self.git_dir.joinpath('lib', 'libbout++.a')

        checks = self.config['bout_options']['enable_checks']
        optimize = self.config['bout_options']['enable_optimize']

        self.extra_config_options = {'enable-checks': checks,
                                     'enable-optimize': optimize}

        if self.config.getboolean('required', 'fftw') or \
                not self.use_preinstalled:
            self.extra_config_options['with-fftw'] = self.local_dir
        if self.config.getboolean('required', 'netcdf') or \
                not self.use_preinstalled:
            self.extra_config_options['with-netcdf'] = self.local_dir

        if self.config.getboolean('required', 'hdf5'):
            self.extra_config_options['with-hdf5'] =\
                self.local_dir.joinpath('bin', 'h5cc')
        if self.config.getboolean('optional', 'sundials'):
            self.extra_config_options['with-sundials'] = self.local_dir
        if self.config.getboolean('optional', 'petsc'):
            self.extra_config_options['with-petsc'] = self.local_dir
        if self.config.getboolean('optional', 'slepc'):
            self.extra_config_options['with-slepc'] = self.local_dir

    def install(self):
        """
        Installs the BOUT++ package
        """

        self.logger.info('Installing BOUT++')
        self.install_package(url=self.boutpp_url,
                             file_from_make=self.file_from_make,
                             overwrite_on_exist=self.overwrite_on_exist,
                             extra_config_option=self.extra_config_options)
        self.logger.info('Installation completed successfully')
