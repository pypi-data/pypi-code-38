#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import configparser
from pathlib import Path
from bout_install.git_installer.BOUTPPInstaller import BOUTPPInstaller
from bout_install.installer.CMakeInstaller import CMakeInstaller
from bout_install.installer.FFMPEGInstaller import FFMPEGInstaller
from bout_install.installer.FFTWInstaller import FFTWInstaller
from bout_install.installer.GCCInstaller import GCCInstaller
from bout_install.installer.HDF5Installer import HDF5Installer
from bout_install.installer.MPIInstaller import MPIInstaller
from bout_install.installer.NetCDFInstaller import NetCDFInstaller
from bout_install.installer.PETScInstaller import PETScInstaller
from bout_install.installer.SLEPcInstaller import SLEPcInstaller
from bout_install.cmake_installer.SundialsInstaller import SundialsInstaller


def install_bout(config_path=None, add_to_bashrc=False):
    """
    Function which installs BOUT++ and its dependencies.

    Parameters
    ----------
    config_path : None or str or Path
        Path to the configuration file
        If None, the default configuration in bout_install.config.ini is
        used
    add_to_bashrc : bool
        Whether or not to add binaries and library path of the dependencies
        to .bashrc
    """

    if config_path is None:
        root_dir = Path(__file__).absolute().parents[1]
        config_path = root_dir.joinpath('bout_install', 'config.ini')

    # String to print when installation is complete
    final_str = '\n'

    config = configparser.ConfigParser(allow_no_value=True)
    with config_path.open() as f:
        config.read_file(f)

    if config.getboolean('optional', 'gcc'):
        print('Installing gcc...')
        gcc_installer = GCCInstaller(config_path=config_path)
        gcc_installer.install()
        final_str += (f'export PATH="'
                      f'{gcc_installer.local_dir.joinpath("bin")}:$PATH"\n')
        final_str += (f'export LD_LIBRARY_PATH = '
                      f'{gcc_installer.local_dir.joinpath("lib64")}:'
                      f'$LD_LIBRARY_PATH"\n')
        print('..done')

    if config.getboolean('required', 'mpi'):
        print('Installing mpi...')
        mpi_installer = MPIInstaller(config_path=config_path)
        mpi_installer.install()
        print('...done')

    if config.getboolean('optional', 'cmake'):
        print('Installing cmake...')
        cmake_installer = CMakeInstaller(config_path=config_path)
        cmake_installer.install()
        print('...done')

    if config.getboolean('optional', 'ffmpeg'):
        print('Installing ffmpeg...')
        ffmpeg_installer = FFMPEGInstaller(config_path=config_path)
        ffmpeg_installer.install()
        print('...done')

    if config.getboolean('required', 'fftw'):
        print('Installing fftw...')
        fftw_installer = FFTWInstaller(config_path=config_path)
        fftw_installer.install()
        print('...done')

    if config.getboolean('required', 'hdf5'):
        print('Installing hd5...')
        hdf5_installer = HDF5Installer(config_path=config_path)
        hdf5_installer.install()
        print('...done')

    if config.getboolean('required', 'netcdf'):
        print('Installing netcdf...')
        netcdf_installer = NetCDFInstaller(config_path=config_path)
        netcdf_installer.install()
        print('...done')

    if config.getboolean('optional', 'sundials'):
        print('Installing sundials...')
        sundials_installer = SundialsInstaller(config_path=config_path)
        sundials_installer.install()
        print('...done')

    if config.getboolean('optional', 'petsc'):
        print('Installing petsc...')
        petsc_installer = PETScInstaller(config_path=config_path)
        petsc_installer.install()
        print('...done')

    if config.getboolean('optional', 'slepc'):
        print('Installing slepc...')
        slepc_installer = SLEPcInstaller(config_path=config_path)
        slepc_installer.install()
        print('...done')

    print('Installing BOUT++...')
    boutpp_installer = BOUTPPInstaller(config_path=config_path)
    boutpp_installer.install()
    print('...done')

    final_str += (f'export LD_LIBRARY_PATH='
                  f'{boutpp_installer.local_dir.joinpath("lib")}:'
                  f'LD_LIBRARY_PATH\n\n')

    if add_to_bashrc:
        add_str_to_bashrc(final_str)
    else:
        print('Make sure that all binaries and libraries are in the PATH')
        print('You can do so by making sure that the following is in .bashrc:')
        print(final_str)


def add_str_to_bashrc(bashrc_str):
    """
    Adds the bashrc_str to .bashrc

    .bashrc will be created if non-existent

    Parameters
    ----------
    bashrc_str : str
        The string to add to bashrc
    """

    bashrc_str = f'# Added by bout_installer.py\n{bashrc_str}'
    bashrc_path = Path.home().joinpath('.bashrc')

    if not bashrc_path:
        bashrc_path.touch()

    print(f'Adding following to .bashrc:\n{bashrc_str}')

    with bashrc_path.open('a') as f:
        f.write(bashrc_str)


def get_args():
    """
    Returns the argument from the argument parser

    Returns
    -------
    config_path : None or str or Path
        Path to the configuration file
        If None, the default configuration in bout_install.config.ini is
        used
    add_to_bashrc : bool
        Whether or not to add binaries and library path of the dependencies
        to .bashrc
    """

    root_dir = Path(__file__).absolute().parents[1]
    config_path = root_dir.joinpath('bout_install', 'config.ini')

    parser = \
        argparse.ArgumentParser(description='Install BOUT++ with dependencies')

    parser.add_argument('-c',
                        '--config',
                        help=f'Path to the configuration file. '
                             f'Default is {config_path}',
                        default=str(config_path))
    parser.add_argument('-a',
                        '--add_to_bashrc',
                        help='If set, paths to binaries and libraries of '
                             'dependencies will be added to .bashrc. '
                             'Default is false',
                        action='store_true',
                        default=False)

    args = parser.parse_args()

    config_path = Path(args.config).absolute()
    add_to_bashrc = args.add_to_bashrc

    return config_path, add_to_bashrc


def bout_install_command_line():
    """
    The main routine which installs BOUT++ and dependencies

    Can be used for command line interface
    """
    config_path, add_to_bashrc = get_args()
    install_bout(config_path, add_to_bashrc=add_to_bashrc)
