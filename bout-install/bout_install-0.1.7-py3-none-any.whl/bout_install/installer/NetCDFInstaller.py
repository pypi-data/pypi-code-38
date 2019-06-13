import os
import shutil
from pathlib import Path
from bout_install.Installer import Installer
from bout_install.installer.HDF5Installer import HDF5Installer


class NetCDFInstaller(Installer):
    """
    Installer object for installing NetCDF
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 netcdf_log_path=
                 Path(__file__).parents[1].joinpath('log', 'netcdf.log'),
                 netcdf_cxx_log_path=
                 Path(__file__).parents[1].joinpath('log', 'netcdf_cxx.log'),
                 hdf5_log_path=
                 Path(__file__).parents[1].joinpath('log', 'hdf5.log'),
                 overwrite_on_exist=False):
        """
        Gets the version and url of NetCDF and calls the super constructor

        The constructor will also make an object of the HDF5 installer and
        the CXX interface installer

        Parameters
        ----------
        config_path : Path or str
            The path to the get_configure_command file
        netcdf_log_path : None or Path or str
            Path to the log file for NetCDF
            If None, the log will directed to stderr
        netcdf_cxx_log_path : None or Path or str
            Path to the log file for the NetCDF CXX interface
            If None, the log will directed to stderr
        hdf5_log_path : None or Path or str
            Path to the log file for HDF5
            If None, the log will directed to stderr
        overwrite_on_exist : bool
            Whether to overwrite the package if it is already found
        """

        self.overwrite_on_exist = overwrite_on_exist

        super().__init__(config_path=config_path, log_path=netcdf_log_path)

        self.netcdf_version = self.config['versions']['netcdf']
        self.netcdf_url = (f'http://www.unidata.ucar.edu/downloads/netcdf/ftp/'
                           f'netcdf-{self.netcdf_version}.tar.gz')

        # CPPFLAGS and LDFLAGS must be exported
        # https://www.unidata.ucar.edu/support/help/MailArchives/netcdf/msg13261.html
        # http://www.unidata.ucar.edu/software/netcdf/docs/getting_and_building_netcdf.html#build_default
        os.environ['CPPFLAGS'] = f'-I{self.local_dir.joinpath("include")}'
        os.environ['LDFLAGS'] = f'-L{self.local_dir.joinpath("lib")}'

        # Create dependency installer
        self.hdf5 = HDF5Installer(config_path=config_path,
                                  log_path=hdf5_log_path)

        # Create the cxx interface installer
        self.netcdf_cxx = NetCDFCXXInstaller(config_path=config_path,
                                             log_path=netcdf_cxx_log_path)

        self.file_from_make = self.local_dir.joinpath('bin', 'ncdump')

        self.extra_config_options = {'disable-dap': None}

    def install(self):
        """
        Installs HDF5, the NetCDF package and the CXX interface
        """

        self.install_dependencies()

        self.logger.info('Installing NetCDF')

        if shutil.which('ncdump') is None or not self.use_preinstalled:
            self.install_package(url=self.netcdf_url,
                                 file_from_make=self.file_from_make,
                                 extra_config_option=self.extra_config_options,
                                 overwrite_on_exist=self.overwrite_on_exist)
            self.logger.info('Installation completed successfully')
        else:
            self.logger.info('Found ncdump in PATH, skipping...')

        # Install the cxx interface
        self.netcdf_cxx.install()

    def install_dependencies(self):
        """
        Installs NetCDF dependencies
        """

        self.hdf5.install()


class NetCDFCXXInstaller(Installer):
    """
    Installer object for installing NetCDFs CXX interface
    """

    def __init__(self,
                 config_path=Path(__file__).parent.joinpath('config.ini'),
                 log_path=
                 Path(__file__).parents[1].joinpath('log', 'netcdf_cxx.log'),
                 overwrite_on_exist=False):
        """
        Gets the NetCDF CXX version, sets the NetCDF CXX url and calls the
        super constructor

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

        self.netcdf_cxx_version = self.config['versions']['netcdf_cxx']
        self.netcdf_cxx_url = (f'http://github.com/Unidata/netcdf-cxx4/archive/'
                               f'v{self.netcdf_cxx_version}.tar.gz')

        self.file_from_make = self.local_dir.joinpath('bin', 'ncxx4-config')

    def install(self):
        """
        Installs the NetCDF CXX interface
        """

        self.logger.info('Installing NetCDF CXX interface')

        if shutil.which('ncxx4-config') is None or not self.use_preinstalled:
            self.install_package(url=self.netcdf_cxx_url,
                                 file_from_make=self.file_from_make,
                                 overwrite_on_exist=self.overwrite_on_exist)
            self.logger.info('Installation completed successfully')
        else:
            self.logger.info('Found ncxx4-config in PATH, skipping...')
