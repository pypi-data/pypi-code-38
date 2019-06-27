# -*- coding: utf-8 -*-
"""
This module contains functions for working with fabric objects
of the HPE Composabale Fabric Manager instance.
"""

####################
# Fabric functions #
####################

def get_fabrics(cfmclient, fabric_uuid=None):
    """
    Get a list of Fabrics currently defined in Composable Fabric.

    :param cfmclient:
    :param fabric_uuid: switch_uuid: UUID of switch from which to fetch port data
    :return: list of Dictionary objects where each dictionary represents a port on a
    Composable Fabric Module
    :rtype: list
    """
    path = 'v1/fabrics'
    if fabric_uuid:
        path += '/{}'.format(fabric_uuid)

    return cfmclient.get(path).json().get('result')


def create_fabric(cfmclient, data, fabric_type=None):
    """
    Create :A Composable Fabric.
    """
    path = 'fabrics'
    params = {'type': fabric_type} if fabric_type else None

    return cfmclient.post(path, params, data).json().get('result')


def get_fabric_ip_networks(cfmclient, fabric_uuid=None):
    """
    Get a list of IP networks from the Composable Fabric.

    :param cfmclient:
    :param fabric_uuid: UUID of fabric
    :return: list of IP address dict objects
    :rtype: list
    """
    path = 'v1/fabric_ip_networks'
    if fabric_uuid:
        path += '/{}'.format(fabric_uuid)

    return cfmclient.get(path).json().get('result')


#####################
# Fitting functions #
#####################

def perform_fit(cfmclient, fabric_uuid, name, description):
    """
    Request a full fit across managed Composable Fabrics.

    :param cfmclient:
    :return:
    """
    data = {
        'fabric_uuid': '{}'.format(fabric_uuid),
        'name': '{}'.format(name),
        'description': '{}'.format(description)
    }
    path = 'fits'

    return cfmclient.post(path, data)


####################
# Switch functions #
####################

def get_switches(cfmclient, params=None):
    """
    Get a list of Composable Fabric switches

    :param cfmclient: object of type CFMClient
    :param params: dict of query parameters used to filter request from API
    :return: list of dicts

    >>> client= CFMClient('10.101.0.210', 'admin', 'plexxi')
    >>> get_switches(client, params={'ports': True})
    >>> get_switches(client, params={'ports': True, 'software': True})
    >>> get_switches(client, params={'ports': True, 'software': True, 'fabric': True})
    """

    return cfmclient.get('v1/switches', params).json().get('result')


def create_switch(cfmclient, data, fabric_type=None):
    """
    Create a Composable Fabric switch.
    """
    params = {'type': fabric_type} if fabric_type else None

    return cfmclient.post('v1/switches', params, data).json().get('result')


##################
# Port functions #
##################

def get_ports(cfmclient, switch_uuid=None):
    """
    Get Composable Fabric switch ports.

    :param cfmclient: object of type CFMClient
    :param switch_uuid: switch_uuid: UUID of switch from which to fetch port data
    :return: list of Dictionary objects where each dictionary represents a port on a
    Composable Fabric Module
    :rtype: list
    """
    path='v1/ports'
    if switch_uuid:
        path += '?switches={}&type=access'.format(switch_uuid)

    return cfmclient.get(path).json().get('result')


def update_ports(cfmclient, port_uuids, field, value):
    """
    Update attributes of composable fabric switch ports

    :param cfmclient:
    :param port_uuids: list of str representing Composable Fabric port UUIDs
    :param field: str specific field which is desired to be modified (case-sensitive)
    :param value: str specific field which sets the new desired value for the field
    :return: dict which contains count, result, and time of the update
    :rtype: dict
    """
    if port_uuids:
        data = [{
            'uuids': port_uuids,
            'patch': [
                {
                    'path': '/{}'.format(field),
                    'value': value,
                    'op': 'replace'
                }
            ]
        }]
        cfmclient.patch('v1/ports', data)

##################
# VLAN functions #
##################

def get_vlan_groups(cfmclient, params=None):
    """
    Get Composable Fabric vlan groups.

    :param cfmclient: object of type CFMClient
    :return: list of VLAN Group dictionary objects in the Composable Fabric
    :rtype: list
    """

    return cfmclient.get('v1/vlan_groups', params).json().get('result')


# TODO POST VLAN_GROUP FUNCTION

# TODO PUT VLAN GROUP FUNCTION

# TODO DELETE VLAN GROUP FUNCTION


def get_vlan_properties(cfmclient, fabric_uuid):
    """
    Get Composable Fabric vlan properties for a specific fabric.

    :param cfmclient: object of type CFMClient
    :param fabric_uuid: str representing a valid fabric UUID
    :return: list of VLAN Group Property dictionary objects from the Composable Fabric
    :rtype: list
    """
    path='v1/vlan_properties/{}'.format(fabric_uuid)

    return cfmclient.get(path).json().get('result')

####################
# VPC functions #
####################

def get_vpcs(cfmclient, uuid=None):
    """
    Get a list of VPCs currently defined in Composable Fabric.

    :param cfmclient: Connected CFM API client
    :param uuid: specific VPC UUID to retrieve
    :return: list of VPC dictionary objects
    :rtype: list
    """
    path = 'v1/vpcs'
    if uuid:
        path += '/{}'.format(uuid)

    return cfmclient.get(path).json().get('result')

def get_bgp(cfmclient, uuid):
    """
    Get VPC BGP configuration.

    :param cfmclient: Connected CFM API client
    :param uuid: VPC UUID from which to retrieve BGP info
    :return: BGP dictionary object
    :rtype: list
    """
    path = 'v1/vpcs/{}/bgp'.format(uuid)

    return cfmclient.get(path).json().get('result')

def get_bgp_leaf_spine(cfmclient, uuid):
    """
    Get VPC BGP leaf and spine configuration.

    :param cfmclient: Connected CFM API client
    :param uuid: VPC UUID from which to retrieve BGP info
    :return: BGP dictionary object
    :rtype: list
    """
    path = 'v1/vpcs/{}/bgp/leaf_spine'.format(uuid)

    return cfmclient.get(path).json().get('result')

def update_bgp_leaf_spine(cfmclient, uuid, config):
    """
    Update VPC BGP leaf and spine configuration.

    :param cfmclient: Connected CFM API client
    :param uuid: VPC UUID from which to retrieve BGP info
    :param config: BGP leaf spine configuration data
    :return: BGP dictionary object
    :rtype: list
    """
    path = 'v1/vpcs/{}/bgp/leaf_spine'.format(uuid)

    return cfmclient.put(path, config).json().get('result')
