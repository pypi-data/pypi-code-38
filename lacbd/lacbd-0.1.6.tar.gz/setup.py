#!/usr/bin/env python3

from setuptools import setup

from setuptools_rust import Binding, RustExtension, Strip

with open('README.md') as f:
    long_description = f.read()

setup(
    name='lacbd',
    version='0.1.6',
    license='AGPL-3.0-or-later',
    description='Fast subsentence searching',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nitros12/like-aho-corasick-but-different-py',
    author='Ben Simms, Ben Mintz',
    author_email='ben@bensimms.moe, bmintz@protonmail.com',

    packages=['lacbd'],

	rust_extensions=[RustExtension('_lacbd', 'like-aho-corasick-but-different-clib/Cargo.toml', binding=Binding.NoBinding, strip=Strip.All)],

    install_requires=[
        'cffi>=1.12,<2.0.0',
    ],

	setup_requires=[
		'wheel',
		'setuptools',
		'setuptools-rust',
	],

    python_requires='>=3.6',

    include_package_data=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Rust',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    zip_safe=False,
)
