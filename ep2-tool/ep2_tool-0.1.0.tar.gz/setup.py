#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='ep2_tool',
    description='Tool to manage EP2 student attendance, formerly pk-tool',
    version='0.1.0',
    license="MIT",
    author='Felix Resch',
    author_email='felix.resch@tuwien.ac.at',
    packages=['ep2_tool', 'ep2_tool.dialog', 'ep2_tool.ep2_tutors', 'ep2_tool.ui'],
    entry_points={
        'console_scripts': [
            'ep2_tool=ep2_tool.ep2_tool:main'
        ]
    },
    install_requires=[
        'python-gitlab==1.8.0',
        'click==7.0',
        'gitpython==2.1.11',
        'six==1.12.0',
        'unicodecsv==0.14.1',
        'enum34==1.1.6',
        'cheetah3==3.2.3',
        'pyqt5==5.12.2'
    ]
)