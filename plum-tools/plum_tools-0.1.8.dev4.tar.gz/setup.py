# -*- coding: utf-8 -*-

import os
import shutil

from setuptools import setup, find_packages

from plum_tools.conf import PathConfig

version = '0.1.8.dev4'


def install():
    setup(
        author="seekplum",
        author_email='1131909224m@sina.cn',
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            # 'Programming Language :: Python :: 3.7',
        ],
        description="linux下常用的工具包",
        install_requires=[
            "argparse",
            "pyyaml",
            "schema",
            "paramiko",
        ],
        # scripts=[
        #     "bin/gitrepo"
        # ],
        setup_requires=[],
        include_package_data=True,
        name='plum_tools',
        namespace_packages=['plum_tools'],
        packages=find_packages(exclude=['tests', 'docs']),
        version=version,
        entry_points={
            'console_scripts': [
                "gitrepo = plum_tools.gitrepo:main",
                "gitstash = plum_tools.gitstash:main",
                "pssh = plum_tools.pssh:main",
                "pping = plum_tools.pping:main",
                "pipmi = plum_tools.pipmi:main",
                "prn = plum_tools.prn:main",
            ],
        }
    )


def init():
    if not os.path.exists(PathConfig.plum_yml_path):
        shutil.copy(os.path.join(PathConfig.root, PathConfig.plum_yml_name), PathConfig.home)


if __name__ == '__main__':
    install()
    init()
