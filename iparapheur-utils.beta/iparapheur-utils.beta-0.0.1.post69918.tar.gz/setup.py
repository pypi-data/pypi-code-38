#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import parapheur

setup(
    name='iparapheur-utils.beta',
    version=parapheur.__version__,
    packages=find_packages(),
    author="Lukas Hameury",
    author_email="lukas.hameury@libriciel.fr",
    description="Client python pour i-Parapheur",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'suds',
        'requests>=2.16.0',
        'importlib',
        'PyMySql',
        'progress'
    ],
    include_package_data=True,
    url='https://gitlab.libriciel.fr/i-parapheur/client-python',
    entry_points={
        'console_scripts': [
            'ph-echo = parapheur.core:echo',
            'ph-check = parapheur.core:check',
            'ph-init = parapheur.core:init',
            'ph-recupArchives = parapheur.core:recuparchives',
            'ph-properties-merger = parapheur.core:properties_merger',
            'ph-export = parapheur.core:export_data',
            'ph-import = parapheur.core:import_data',
            'ph-rename = parapheur.core:rename',
            'ph-removeldap = parapheur.core:remove_ldap',
            'ph-pushdoc = parapheur.core:pushdoc',
            'ph-ipclean = parapheur.core:ipclean',
            'ph-ldapsearch = parapheur.core:ldapsearch',
            'ph-count_files = parapheur.core:count_files',
            'ph-reset_admin_password = parapheur.core:reset_admin_password'
        ],
    },
    license="CeCILL v2",
)
