# coding: utf-8
""" DeployV is a tool ser to help in the process of deploying Odoo instances inside a docker
container, the main idea is to do that remotely and in a unattended way.

For that we created a package with all needed modules (at least those developed by us) to backup,
start, update and build instances.
"""

import logging

__author__ = 'Tulio Ruiz <tulio@vauxoo.com>'
__version__ = '0.9.130'
__all__ = ['base', 'helpers', 'instance', 'messaging']

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)-5s - %(name)s.%(funcName)s - %(message)s"
)
