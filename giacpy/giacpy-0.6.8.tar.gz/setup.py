#!/usr/bin/env python

# Set this to True to enable building extensions using Cython.
# Set it to False to build extensions from the CPP file (that
# was previously created using Cython).
# Set it to 'auto' to build with Cython if available, otherwise
# from the CPP file.
# Warning: I can notice some runtime errors with cython 0.15 that disappear with 0.17
#USE_CYTHON = False
USE_CYTHON = 'auto'

###############################################################
#If you have QT support, you can enable qcas with --enable-qcas
#    But to use qcas you should create first: qcas/libqcas.a with:
#       qmake libqcas.pro ;make
import sys
if "--enable-qcas" in sys.argv:
    USE_QCAS=True
    sys.argv.remove("--enable-qcas")
else:
    USE_QCAS=False
#######################################

try:
    from setuptools import setup
    from setuptools import Extension
except:
    # python 2.6
    from distutils.core import setup
    from distutils.extension import Extension


if USE_CYTHON:
    try:
        from Cython.Distutils import build_ext
        from Cython.Build import cythonize
    except ImportError:
        if USE_CYTHON=='auto':
            USE_CYTHON=False
        else:
            raise

cmdclass = { }
ext_modules = [ ]
# default configuration
package_data={'giacpy' : ['__init__.py', 'GPL-2', 'giacpymisc.h', 'giacpy.pxd']}
# NB: 'giacpymisc.h', 'giacpy.pxd' are usefull for cython users.
package_dir={'giacpy' : 'giacpy'}

conf = {'CXXFLAGS' : [], 'LDFLAGS' : []}

# librairies to compile giacpy
# with giac 1.2 -lao is not required anymore
libraries=['giac']
library_dirs=[]
include_dirs=['.']
#libraries to compile giacpy2qcas
#include_dirs2 = ['./qcas','/usr/include/qt4/QtCore','/usr/include/qt4/QtGui','/usr/include/qt4/QtXml','/usr/include/qt4/QtSvg','/usr/include/qt4','./qcas/qt','./qcas/giac','.']

#qt5inc = '/usr/include/qt5/'

# Guess QT config
QTVERSION=None
import subprocess
try:
    QTVERSION=subprocess.check_output(['qmake','-query', 'QT_VERSION']).decode()
    QTHEADERS=subprocess.check_output(['qmake','-query', 'QT_INSTALL_HEADERS']).decode()
    QTHEADERS=QTHEADERS.replace("\n","")
except:
    pass

if QTVERSION == None:
    try:
        QTVERSION=subprocess.check_output(['qmake-qt5','-query', 'QT_VERSION']).decode()
        QTHEADERS=subprocess.check_output(['qmake-qt5','-query', 'QT_INSTALL_HEADERS']).decode()
        QTHEADERS=QTHEADERS.replace("\n","")
    except:
        pass

if QTVERSION == None:
    try:
        QTVERSION=subprocess.check_output(['qmake-qt4','-query', 'QT_VERSION']).decode()
        QTHEADERS=subprocess.check_output(['qmake-qt4','-query', 'QT_INSTALL_HEADERS']).decode()
        QTHEADERS=QTHEADERS.replace("\n","")
    except:
        pass
#
if QTVERSION != None:
    QTVERSION=QTVERSION[0]
    if QTHEADERS[-1] != "/":
        #print(QTHEADERS)
        QTHEADERS=QTHEADERS+'/'
else:
    QTHEADERS="/usr/include/qt5/"

if QTVERSION=='4':
    include_dirs2 = [QTHEADERS+'QtCore', QTHEADERS+'QtGui', QTHEADERS+'QtXml', QTHEADERS+'QtSvg', QTHEADERS] # FIX + libqcas
    libraries2=['qcas','dl','giac','gmp','QtSvg','QtXml','QtGui','QtCore','pthread']
else:
    # QT5
    include_dirs2 = ['libqcas',QTHEADERS,QTHEADERS+'QtCore',QTHEADERS+'QtGui',QTHEADERS+'QtWidgets',QTHEADERS+'QtXml',QTHEADERS+'QtSvg']
    # with giac 1.2 -lao is not required anymore
    libraries2=['qcas','dl','giac','gmp','Qt5Svg','Qt5Xml','Qt5Widgets','Qt5Gui','Qt5Core','pthread']

#
library_dirs2=[''] # if you have a system wide libqcas
#library_dirs2=['./qcas']  #  if you have libqcas from giacpy tree
#

if sys.platform == "win32":
    USE_QCAS=False
    import platform
    if platform.architecture()[0] == "64bit":
        package_data={'giacpy' : ['../giacpy/__init__.py', '../giacpy/GPL-2', '*.dll']}
        package_dir={'giacpy' : 'win64'}
        library_dirs+=['./win64']
        include_dirs+=['./win64/include']
        conf['CXXFLAGS']=['-UHAVE_CONFIG_H','-DMS_WIN64','-DIN_GIAC','-D__MINGW_H','-DGIAC_MPQS','-fexceptions', '-fwrapv']
        #conf['LDFLAGS']=['-static-libgcc', '-static-libstdc++']
    else:
        package_data={'giacpy' : ['../giacpy/__init__.py', '../giacpy/GPL-2', '*.dll']}
        package_dir={'giacpy' : 'win32'}
        library_dirs+=['./win32']
        include_dirs+=['./win32/include']
        conf['CXXFLAGS']=['-UHAVE_CONFIG_H','-DMS_WIN64','-DIN_GIAC','-D__MINGW_H','-DGIAC_MPQS','-fexceptions', '-fwrapv']


if USE_CYTHON:
    ext_modules+=cythonize([Extension(
                   "giacpy.giacpy",                 # name of extension
                   ["giacpy/giacpy.pyx"], #  our Cython source
                   libraries=libraries,
                   library_dirs=library_dirs,
                   include_dirs=include_dirs,
                   extra_compile_args=conf["CXXFLAGS"],
                   extra_link_args=conf["LDFLAGS"],
                   language="c++")],include_path=include_dirs)

    if USE_QCAS:
        ext_modules+=cythonize([Extension(
                   "giacpy.giacpy2qcas",                 # name of extension
                   ["giacpy/giacpy2qcas.pyx"], #  our Cython source
                   libraries=libraries2,
                   library_dirs=library_dirs2,
                   include_dirs=include_dirs2,

                   extra_compile_args=conf["CXXFLAGS"],
                   extra_link_args=conf["LDFLAGS"],
                   language="c++")], include_path=include_dirs2)


    cmdclass={'build_ext': build_ext}

else:
    ext_modules+=[Extension(
                   "giacpy.giacpy",                 # name of extension
                   ["giacpy/giacpy.cpp"], #  the cpp file already created by Cython
                   library_dirs=library_dirs,
                   libraries=libraries,
                   include_dirs=include_dirs,
                   extra_compile_args=conf["CXXFLAGS"],
                   extra_link_args=conf["LDFLAGS"],
                   language="c++")]

    if USE_QCAS:
        ext_modules+=[Extension(
                   "giacpy.giacpy2qcas",                 # name of extension
                   ["giacpy/giacpy2qcas.cpp"], #  our Cython source
                   libraries=libraries2,
                   library_dirs=library_dirs2,
                   include_dirs=include_dirs2,
                   extra_compile_args=conf["CXXFLAGS"],
                   extra_link_args=conf["LDFLAGS"],
                   language="c++")]



setup(


    name='giacpy',
    version='0.6.8',
    description='A Cython frontend to the c++ library giac. (Computer Algebra System)',
    author='Frederic Han',
    author_email="frederic.han@imj-prg.fr",
    url='http://www.imj-prg.fr/~frederic.han/xcas/giacpy/',
    long_description=open('README.txt').read(),
    license='GPLv2 or above',
    ext_modules=ext_modules,
    packages = ['giacpy'],
    package_dir=package_dir,
    package_data=package_data
    #include_package_data=True#, (on unix (but not on windows) this will include all the *.cpp, and all files listed in MANIFEST.in in the module dir)
    #cmdclass=cmdclass
    )
