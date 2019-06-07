#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains functions related to working with the system characteristics of the
desired HPE Composable Fabric Manager instance
"""


def get_version(cfmclient):
    """
    Function takes input cfmclient type object to authenticate against CFM API and queries
    versions API to return the version number of the system represented by the CFCMclient object
    Current supported params are

    :param cfmclient: object of type CFMClient
    :return: list of dicts
    """
    path = 'versions'
    return cfmclient.get(path).json().get('result')


def get_audit_logs(cfmclient):
    """
    Get :List of audit log records currently defined in Composable Fabric.
    :param cfmclient:
    :return: list of Dictionary objects where each dictionary represents a single entry in the
    audit log of the HPE Composable Fabric Manager
    :rtype: list
    """
    path = 'audits'
    return cfmclient.get(path).json().get('result')


def get_backups(cfcmclient, uuid=None):
    """
    Function to get a list of current backups located on the Composable Fabric Manager
    represented by the cfcmclient object.
    :param cfcmclient: Composable Fabric Manager connection object of type CFMClient
    :param uuid: str that represents the unique identifier for a specific backup
    :return: single dictionary if UUID. List of dictionaries where each dictionary represents a
    single backup.
    """
    path = 'backups'
    if uuid:
        path = 'backups/{}'.format(uuid)
    return cfcmclient.get(path).json().get('result')


def create_backup(cfcmclient):
    """
    Function to initiate a new backup on the Composable Fabric Manager represented by the
    CFCMClinet object
    :param cfcmclient:Composable Fabric Manager connection object of type CFMClient
    :return: HTTP response
    """
    path = 'backups'
    return cfcmclient.post(path, data='')
