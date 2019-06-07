# -*- coding: utf-8 -*-
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from distutils.version import LooseVersion
from setuptools import setup, find_packages
from setuptools.extension import Extension
from setuptools.command.install import install
#from Cython.Build import cythonize
import sys
import os
import platform
import zipfile
from shutil import move, rmtree
# needed to compile quickparanoid during the installation
import subprocess

#import numpy


#from os import path
#here = path.abspath(path.dirname(__file__))

_CYTHON_INSTALLED = False
min_cython_ver = '0.27'
try:
    import Cython
    ver = Cython.__version__
    _CYTHON_INSTALLED = ver >= LooseVersion(min_cython_ver)
except ImportError:
    _CYTHON_INSTALLED = False
    raise ImportError('\nWARNING: SonicParanoid requires a version of Cython higher than {:s}:\npip install cython\n'.format(min_cython_ver))

# exit with an error if Cython is not installed
if not _CYTHON_INSTALLED:
    sys.stderr.write('\nWARNING: SonicParanoid requires a version of Cython equal or higher than {:s}:\npip install cython\n'.format(min_cython_ver))

# load cythonize if cython has been installed
if _CYTHON_INSTALLED:
    from Cython.Build import cythonize



def makedir(path):
    """Create a directory including the intermediate directories in the path if not existing."""
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise



def untar(tarpath, outDir=os.getcwd(), debug=True):
    import tarfile
    if debug:
        print('Tar.gz path:\t%s'%tarpath)
        print('Output dir:\t%s'%outDir)
    #check if the tar file is valid
    if not tarfile.is_tarfile(tarpath):
        sys.stderr.write('\nERROR: %s is not a valid tar.gz file.'%tarpath)
        sys.exit(-2)
    #create the output directory if does not exist yet
    if outDir[-1] != '/':
        outDir += '/'
    #create output directory
    makedir(outDir)
    #change current directory
    cwd = os.getcwd()
    if os.path.dirname(outDir) != cwd:
        os.chdir(outDir)
    #open the tar file
    tar = tarfile.open(tarpath)
    tar.extractall()
    tar.close()
    #set the current directory to the starting one
    os.chdir(cwd)
    if debug:
        print('Extracted in %s'%outDir)



extensions = [
    Extension(
        "sonicparanoid.inpyranoid_c",
        ["sonicparanoid/inpyranoid_c.pyx"],
        ##include_dirs=[numpy.get_include()], # not needed for fftw unless it is installed in an unusual place
        #libraries=['fftw3', 'fftw3f', 'fftw3l', 'fftw3_threads', 'fftw3f_threads', 'fftw3l_threads'],
        #library_dirs=['/some/path/to/include/'], # not needed for fftw unless it is installed in an unusual place
    ),
    Extension(
        "sonicparanoid.mmseqs_parser_c",
        ["sonicparanoid/mmseqs_parser_c.pyx"],
        ##include_dirs=[numpy.get_include()], # not needed for fftw unless it is installed in an unusual place
        #libraries=['fftw3', 'fftw3f', 'fftw3l', 'fftw3_threads', 'fftw3f_threads', 'fftw3l_threads'],
        #library_dirs=['/some/path/to/include/'], # not needed for fftw unless it is installed in an unusual place
    ),
    Extension(
        "sonicparanoid.remap_tables_c",
        ["sonicparanoid/remap_tables_c.pyx"],
    ),
    Extension(
        "sonicparanoid.graph_c",
        ["sonicparanoid/graph_c.pyx"],
    ),
    Extension(
        "sonicparanoid.mcl_c",
        ["sonicparanoid/mcl_c.pyx"],
    ),
]

# To use a consistent encoding
from codecs import open
from os import path
from os import chdir

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# constant variables to be used inside the setup function
LICENSE = 'GNU GENERAL PUBLIC LICENSE, Version 3.0 (GPLv3)'



class QuickParaCompile(install):
    def run(self):
        try:
            # note cwd - this makes the current directory
            # the one with the Makefile.
            prevDir = here
            cmpDir = path.join(here, 'sonicparanoid/quick_multi_paranoid/')
            chdir(cmpDir)
            # clean the directory from installations
            sys.stdout.write('\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-')
            print('\nCompiling the program for multi-species orthology...')
            print('Cleaning any previous installation...')
            cleanCmd = 'make clean'
            process = subprocess.Popen(cleanCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()
            # compile the source
            compileCmd = 'make qa'
            process = subprocess.Popen(compileCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()
            # reset the current directory
            chdir(prevDir)
            sys.stdout.write('-#-#-#-#-#-#- DONE -#-#-#-#-#-#-')

            sys.stdout.write('\n\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-\n')
            # clean the directory from installations
            # Now lets compile MCL
            prevDir = here
            cmpDir = os.path.join(here, 'sonicparanoid/mcl_package/')
            chdir(cmpDir)
            # remove old binaries if required
            mclBinDir = os.path.join(cmpDir, 'bin/')
            print(mclBinDir)
            if os.path.isdir(mclBinDir):
                print("Wiping MCL bin directory")
                # remove all its content
                rmtree(mclBinDir)
                makedir(mclBinDir)

            print('\nBuilding MCL clustering algorithm...')
            # check if the archive has been already decompressed
            confPath = os.path.join(cmpDir, "configure")
            if os.path.isfile(confPath):
                print('Cleaning any previous installation...')
                # clean configuration
                cleanCmd = 'make distclean'
                process = subprocess.Popen(cleanCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_val, stderr_val = process.communicate() #get stdout and stderr
                process.wait()
                # remove binaries
                cleanCmd = 'make clean'
                process = subprocess.Popen(cleanCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_val, stderr_val = process.communicate() #get stdout and stderr
                process.wait()
            else: # extract the archive
                archPath: str = os.path.join(cmpDir, "mcl_src_slim.tar.gz")
                if not os.path.isfile(archPath):
                    sys.stderr.write("ERROR: the archive the MCL source code is missing\n{:s}\nPlease try to download SonicParanoid again.".format(archPath))
                    sys.exit(-2)
                else:
                    untar(archPath, cmpDir, debug=False)
            # configure MCL
            print("\nConfiguring the MCL installation...")
            compileCmd = './configure --prefix={:s}'.format(cmpDir)
            process = subprocess.Popen(compileCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()

            # binary paths
            mclBin = os.path.join(cmpDir, "bin/mcl")
            if os.path.isfile(mclBin):
                print("Removing old MCL binaries...")
                os.remove(mclBin)

            # compile MCL
            compileCmd = 'make install'
            print("Building MCL...")
            process = subprocess.Popen(compileCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()

            if not os.path.isfile(mclBin):
                sys.stderr.write("ERROR: the MCL binaries could not be build.\n")
                sys.exit(-2)

            # reset the current directory
            chdir(prevDir)
            sys.stdout.write('-#-#-#-#-#-#- MCL compilation done -#-#-#-#-#-#-')


        except Exception as e:
            print(e)
            print("ERROR: failed to compile the program for multi-species orthology.")
            exit(-5)
        else:
            install.run(self)



# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='sonicparanoid',  # Required
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version = "1.2.3", # Required
    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='SonicParanoid: fast, easy and accurate orthology inference',  # Required
    long_description=long_description,  # Optional
    url='http://iwasakilab.bs.s.u-tokyo.ac.jp/sonicparanoid/',  # Optional
    # This should be your name or the name of the organization which owns the
    # project.
    author="Salvatore Cosentino",  # Optional
    # This should be a valid email address corresponding to the author listed
    # above.
    author_email="salvo@gmail.com",  # Optional
    # license
    license=LICENSE,
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    # compile multi-species orthology source files
    cmdclass={'install': QuickParaCompile,},
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='bioinformatic inparanoid orthology_inference phylogeny evolution orthology',  # Optional
    #package_dir={'': 'sonicparanoid'},
    package_dir={'sonicparanoid': 'sonicparanoid/'},
    #packages = find_packages('sonicparanoid'),
    #packages = find_packages('sonicparanoid'),
    packages = ['sonicparanoid',],
    # required python version
    python_requires='>=3.5, <3.8',
    include_package_data=True,
    package_data={'sonicparanoid': ['config.json', 'example/test_output/*', 'example/test_input/*', 'mmseqs2_src/*', 'bin/README.txt',
            'quick_multi_paranoid/dump.cpp',
            'quick_multi_paranoid/gen_header.cpp',
            'quick_multi_paranoid/hashtable_itr.c',
            'quick_multi_paranoid/hashtable_itr.h',
            'quick_multi_paranoid/hashtable_private.h',
            'quick_multi_paranoid/hashtable.c',
            'quick_multi_paranoid/hashtable.h',
            'quick_multi_paranoid/Makefile',
            'quick_multi_paranoid/Makefile.in',
            'quick_multi_paranoid/ortholog.c',
            'quick_multi_paranoid/qa.h',
            'quick_multi_paranoid/qa1.cpp',
            'quick_multi_paranoid/qa2.cpp',
            'quick_multi_paranoid/qa1',
            'quick_multi_paranoid/qa2',
            'quick_multi_paranoid/hashtable.o',
            'quick_multi_paranoid/qp',
            'quick_multi_paranoid/qp.c',
            'quick_multi_paranoid/qps.c',
            'mcl_package/mcl_src_slim.tar.gz',
            'mcl_package/bin/mcl',
            ]},  # Optional
    # required packages
    install_requires=['scipy>=1.1.0', 'numpy>=1.13.0', 'pandas>=0.22.0', 'cython>=0.27.0', 'sh>=1.12.14', 'setuptools>=24.2.0', 'pip>=9.0.1', 'biopython>=1.67',], # specify minimum version
    # external to be compiled
    ext_modules = cythonize(extensions, compiler_directives={'language_level': 3}),
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'sonicparanoid = sonicparanoid.sonic_paranoid:main',
            'sonicparanoid-get-mmseqs2 = sonicparanoid.get_mmseqs2:main',
            'sonicparanoid-set-mmseqs2 = sonicparanoid.set_mmseqs2:main',
            'sonicparanoid-get-test-data = sonicparanoid.get_test_data:main',
            'sonicparanoid-extract = sonicparanoid.sonic_paranoid_extract:main',
        ],
    },

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
        'Source': 'https://gitlab.com/salvo981/sonicparanoid2',
    },
)
