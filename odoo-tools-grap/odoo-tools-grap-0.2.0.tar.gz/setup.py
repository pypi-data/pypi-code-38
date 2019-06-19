# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import setuptools

setuptools.setup(
    name="odoo-tools-grap",
    version="0.2.0",
    author="GRAP, Groupement Régional Alimentaire de Proximité",
    author_email="informatique@grap.coop",
    description="Small tools for Odoo",
    long_description=open('README.rst').read(),
    url="https://www.grap.coop",
    packages=['odoo_tools'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    install_requires=[
        'argcomplete',
        'pyyaml',
    ],
    entry_points=dict(
        console_scripts=['odoo-tools-grap=odoo_tools.__main__:main']),
)
