#!/usr/bin/env python3
# Author:  Name name
# Contact: bsc.mail@bsc.es
''' **GeNESiS** set up.
'''

# Imports
from setuptools.command.install import install

def name():
    ''' Set name for GeNESiS package.

    :param: None
    :return: GeNESiS name
    :rtype: string
    '''
    return 'GeNESiS-SDK'


def description():
    ''' Descripton of GeNESiS code
    '''
    GeNESiS_description = ('')

    return GeNESiS_description


def long_description():
    ''' Read long description of GeNESiS of DESCRIPTION.rst file.

    :param: None
    :return: GeNESiS description
    :rtype: string
    '''
    with open(os.path.join('DESCRIPTION.rst')) as f:
        return f.read()


def get_ext_modules():
    ''' Get paths of extension modules.

    :param: None
    :return: numpy path include
    '''
    try:
        import numpy
        numpy_includes = [numpy.get_include()]
    except ImportError:
        numpy_includes = []

    return numpy_includes

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Prepare the environemnt
        cmd = "export GENESIS_METADATA_PATH=$(pip show genesis-sdk | grep \"Location\" | awk '{print $2\"/genesis/meta\"}')"
        cmd = "echo \"\n# GeNESiS environment setup\n" + cmd + "\" >> ~/.bashrc"
        os.system(cmd)

        install.run(self)

if __name__ == '__main__':
    from setuptools import setup

    import os

    # Get the GeNESiS libraries before packing
    os.system("cp -R ../../modules/genesis/ .; cp -R ../../meta genesis")

    # GeNESiS setup
    setup(name=name(),
          maintainer="juan.rodriguez",
          maintainer_email="juan.rodriguez@bsc.es",
          version='0.1.11',
          long_description=long_description(),
          description=description(),
          url="https://www.bsc.es/",
          download_url="http://GeNESiS.bsc.es",
          license='To be defined',
          packages=['genesis'],
          include_dirs=get_ext_modules(),
          install_requires=['numpy'],
          setup_requires=['sphinx'],
          classifiers=['Development Status :: 3 - Alpha',
                       'License :: Free for non-commercial use',
                       'Intended Audience :: Science/Research',
                       'Intended Audience :: Developers',
                       'Programming Language :: Python :: 3.5',
                       'Topic :: Scientific/Engineering',
                       'Topic :: Software Development :: Libraries',
                       'Operating System :: POSIX :: Linux'],
          keywords=['HPC, Hererogeneous Computing, Geophysics'],
          platforms="Linux",
          include_package_data=True,
          cmdclass={
            'install': PostInstallCommand,
          }
          )

else:
    pass
