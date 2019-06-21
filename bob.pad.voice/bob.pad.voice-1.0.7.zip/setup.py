#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST
#
# Copyright (C) Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This file contains the python (distutils/setuptools) instructions so your
# package can be installed on **any** host system. It defines some basic
# information like the package name for instance, or its homepage.
#
# It also defines which other packages this python package depends on and that
# are required for this package's operation. The python subsystem will make
# sure all dependent packages are installed or will install them for you upon
# the installation of this package.
#
# The 'buildout' system we use here will go further and wrap this package in
# such a way to create an isolated python working environment. Buildout will
# make sure that dependencies which are not yet installed do get installed, but
# **without** requiring administrative privileges on the host system. This
# allows you to test your package with new python dependencies w/o requiring
# administrative interventions.

from setuptools import setup, dist

dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages

install_requires = load_requirements()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name='bob.pad.voice',
    version=open("version.txt").read().rstrip(),
    description='Package extends bob.pad.base for attack detection in speech',

    url='https://gitlab.idiap.ch/bob/bob.pad.voice',
    license='GPLv3',
    author='Pavel Korshunov',
    author_email='<pavel.korshunov@idiap.ch>',
    keywords="presentation attack detection, voice biometrics, framework",

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,

    # This line defines which packages should be installed when you "install"
    # this package. All packages that are mentioned here, but are not installed
    # on the current system will be installed locally and only visible to the
    # scripts of this package. Don't worry - You won't need administrative
    # privileges when using buildout.
    install_requires=install_requires,

    # Your project should be called something like 'bob.<foo>' or
    # 'bob.<foo>.<bar>'. To implement this correctly and still get all your
    # packages to be imported w/o problems, you need to implement namespaces
    # on the various levels of the package and declare them here. See more
    # about this here:
    # http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
    #
    # Our database packages are good examples of namespace implementations
    # using several layers. You can check them out here:
    # https://github.com/idiap/bob/wiki/Satellite-Packages


    # This entry defines which scripts you will have inside the 'bin' directory
    # once you install the package (or run 'bin/buildout'). The order of each
    # entry under 'console_scripts' is like this:
    #   script-name-at-bin-directory = module.at.your.library:function
    #
    # The module.at.your.library is the python file within your library, using
    # the python syntax for directories (i.e., a '.' instead of '/' or '\').
    # This syntax also omits the '.py' extension of the filename. So, a file
    # installed under 'example/foo.py' that contains a function which
    # implements the 'main()' function of particular script you want to have
    # should be referred as 'example.foo:main'.
    #
    # In this simple example we will create a single program that will print
    # the version of bob.
    entry_points={
        'console_scripts': [
        ],

        # bob database declaration for the dummy test database
        'bob.db': [
            'dummy-speech = bob.pad.voice.test.dummy.database:Interface',  # driver for bobdb_manage
        ],

        'bob.pad.database': [
            'dummy-speech            = bob.pad.voice.test.dummy.database:database',
            'avspoof            = bob.pad.voice.config.database.avspoof:database',
            'asvspoof            = bob.pad.voice.config.database.asvspoof:database',
            'voicepa            = bob.pad.voice.config.database.voicepa:database',
            'asvspoof2017            = bob.pad.voice.config.database.asvspoof2017:database',
        ],

        'bob.pad.algorithm': [
            'tensorflow  = bob.pad.voice.config.algorithm.tensorfloweval:algorithm',
            'dummy-algo  = bob.pad.voice.algorithm.dummy:algorithm',
            # compute scores based on different energy bands
            'logregr  = bob.pad.voice.algorithm.LogRegr:algorithm',
            'pcalogregr  = bob.pad.voice.config.algorithm.PCALogRegr:algorithm',
            # the best performing LR classifier:
            'normlogregr  = bob.pad.voice.config.algorithm.NormLogRegr:algorithm',
            'histdistance  = bob.pad.voice.algorithm.HistDistance:algorithm',
            'gmm  = bob.pad.voice.algorithm.GMM:algorithm',
            # the same as above but with smaller thresholds
            'gmm-scfc  = bob.pad.voice.config.algorithm.gmm_scfc:algorithm',
        ],

        'bob.pad.preprocessor': [
            'cqcc20p            = bob.bio.spear.config.extractor.cqcc20:cqcc20',  # Empty preprocessor for CQCC features
            'dummytfp            = bob.pad.voice.extractor.dummy_tensorflow:dummytf',  # For tensorflow
            'energy-2gauss = bob.bio.spear.config.preprocessor.energy_2gauss:preprocessor',  # two Gauss energy
            'energy-thr        = bob.bio.spear.config.preprocessor.energy_thr:preprocessor',
            # thresholded energy
            'mod-4hz           = bob.bio.spear.config.preprocessor.mod_4hz:preprocessor',  # mod_4hz
            'external            = bob.bio.spear.config.preprocessor.external:preprocessor',  # external VAD
        ],

        'bob.pad.extractor': [
            'cqcc20e = bob.bio.spear.config.extractor.cqcc20:cqcc20',  # Extractor (reads Matlab files) for CQCC features
            'audiotf            = bob.pad.voice.extractor.audio_tensorflow:audiotf',  # For audio tensorflow
            'dummytfe            = bob.pad.voice.extractor.dummy_tensorflow:dummytf',  # For tensorflow
            'glcms              =  bob.pad.voice.extractor.glcms:extractor',
            'lbp-hist              =  bob.pad.voice.extractor.lbp_histograms:extractor',
            # LBP-based features as per the paper from Eurecom
            'lbp-eurecom              =  bob.pad.voice.config.extractor.lbp_eurecom:extractor',
            'lbp-regular8-2         = bob.pad.voice.config.extractor.lbp_regular8_2hist:extractor',
            'ratios  = bob.pad.voice.extractor.ratios:extractor',

            # SSFCs with delta and delta-delta, plus mod_4hz labels
            'ssfc20  = bob.bio.spear.config.extractor.ssfc20:extractor',
            # SCFCs with delta and delta-delta, plus mod_4hz labels
            'scfc20  = bob.bio.spear.config.extractor.scfc20:extractor',
            # SCMCs with delta and delta-delta, plus mod_4hz labels
            'scmc20  = bob.bio.spear.config.extractor.scmc20:extractor',
            # RFCCs with delta and delta-delta, plus mod_4hz labels
            'rfcc20  = bob.bio.spear.config.extractor.rfcc20:extractor',
            # MFCC with delta and delta-delta, plus mod_4hz labels
            'mfcc20  = bob.bio.spear.config.extractor.mfcc20:extractor',
            # IMFCC with delta and delta-delta, plus mod_4hz labels
            'imfcc20  = bob.bio.spear.config.extractor.imfcc20:extractor',
            # LFCCs with delta and delta-delta, plus mod_4hz labels
            'lfcc20  = bob.bio.spear.config.extractor.lfcc20:extractor',

        ],

        'bob.bio.preprocessor': [
            # Just store WAV files 'as is' in HDF5
            'dummytfp            = bob.pad.voice.extractor.dummy_tensorflow:dummytf',
        ],

        'bob.bio.extractor': [
            'audiotf            = bob.pad.voice.extractor.audio_tensorflow:audiotf',  # For audio tensorflow
        ],

        'bob.pad.grid': [
            'modest         = bob.bio.spear.config.grid.modest:grid',
        ],
    },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers=[
        'Framework :: Bob',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
