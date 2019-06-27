# -*- coding: utf-8 -*-
import get_args
import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements/install.txt', 'r', encoding='utf-8') as f:
    install_requires = f.readlines()


setuptools.setup(
    name='get_args',
    version=get_args.main.__version__,
    author='fun04wr0ng',
    author_email='fun04wr0ng@gmail.com',
    description='get args from command line, environment and configuration file.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fun04wr0ng/get_args',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux'
    ],
    license='GPL v3+',

    python_requires='>=3.6',
    install_requires=install_requires,
    extras_require={
        'toml': [
            'toml',
        ],
    },
    entry_points={
        'console_scripts': [
            'get_args = get_args.main:main',
        ],
    },
    package_data={
        '': ['*.yml', ]
    }
)
