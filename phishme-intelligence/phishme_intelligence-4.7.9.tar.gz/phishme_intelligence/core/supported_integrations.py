#Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
#This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
#including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
#disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
#consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
#this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import os
import sys

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


def read_manifest(manifest_file=None):
    """
    Read PhishMe Intelligence integration manifest file

    :param str manifest_file: (optional) Path to PhishMe Intelligence integration manifest; defaults to './phishme_intelligence/output/manifest.ini'
    :return: PhishMe Intelligence integration manifest
    :rtype: ConfigParser
    """

    if manifest_file is None:
        manifest_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'manifest.ini')

    if PYTHON_MAJOR_VERSION == 3:
        manifest = ConfigParser(interpolation=None)
    else:
        manifest = ConfigParser()

    manifest.read(manifest_file)

    return manifest


def import_libraries(config):
    """
    Returns the module and package that needs to be imported, depending on whether an integration is activated.

    :param ConfigParser config: PhishMe Intelligence configuration
    :return: list of integrations used by the installation (based on 'use' being set to True in the section)
    :rtype: list of :class:`phishme_intelligence.core.supported_integrations.SupportedIntegration`
    """

    # Supported integrations are listed in this file with the libraries they need to import.
    supported_integrations = read_manifest()

    # For each of the supported integration in the dictionary above, yield the libraries to be imported.
    activated_integrations = []
    for integration in supported_integrations.sections():

        # Load a supported integration only if it has a section present in the ConfigParser AND use==True.
        if config.has_section(integration) and config.getboolean(integration, 'use'):
            sample = SupportedIntegration(config_name=integration,
                                          mrti_format=supported_integrations.get(integration, 'mrti_format'),
                                          output_product_module=supported_integrations.get(integration, 'output_product_module'),
                                          class_name=supported_integrations.get(integration, 'class_name')
                                          )

            config.set('pm_format', sample.mrti_format, 'True')

            activated_integrations.append(sample)

    return activated_integrations


class SupportedIntegration(object):
    """
    Class for holding information for each integration enabled by a PhishMe Intelligence installation
    """

    def __init__(self, config_name, mrti_format, output_product_module, class_name):
        """
        Initialize a SupportedIntegration object

        :param str config_name: Name of integration (section name e.g. integration_mcafee_siem)
        :param str mrti_format: format of data from PhishMe Intelligence API used by integration
        :param str output_product_module: Python classpath for integration module
        :param str class_name: Name of Python class for integration
        """

        self.config_name = config_name

        self.mrti_format = mrti_format
        self.output_product_module = output_product_module
        self.class_name = class_name
