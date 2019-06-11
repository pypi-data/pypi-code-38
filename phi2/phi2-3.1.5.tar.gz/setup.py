# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
        name='phi2',
        version='3.1.5',
        description='Python Hardware Interfaz GPIO para python',
        long_description='Proyecto educativo que provee una GPIO basada en arduino para python',
        url='https://github.com/claudior117/phi2.git',
        author='cludio ravagnan',
        author_email='claudio@proyecto204.com.ar',
        include_package_data=True, #permite archivos sin extension py
        license='GPL',

        # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            'Operating System :: OS Independent',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',

            'Intended Audience :: Education',

            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        ],

        keywords='sample setup',
        packages=find_packages(),
        install_requires=['pyserial'],
        #install_requires=[i.strip() for i in open("requires.txt").readlines()],
    )